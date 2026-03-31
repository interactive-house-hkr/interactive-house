from datetime import datetime, timezone
from typing import Any, Dict, Optional

from services.src.firebase.firebase_client import get_ref


DEVICES_PATH = "devices"
PENDING_COMMANDS_PATH = "pending_commands"


def _devices_ref():
    return get_ref(DEVICES_PATH)


def _device_ref(device_uuid: str):
    return get_ref(f"{DEVICES_PATH}/{device_uuid}")


def _pending_commands_ref(device_uuid: str):
    return get_ref(f"{PENDING_COMMANDS_PATH}/{device_uuid}")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_device(device_uuid: str, data: Dict[str, Any], existing: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    existing = existing or {}

    status = existing.get("status", {}).copy()
    status.update(data.get("status", {}))
    status["connected"] = True

    return {
        "device_uuid": device_uuid,
        "type": data.get("type", existing.get("type")),
        "transport": data.get("transport", existing.get("transport", {})),
        "capabilities": data.get("capabilities", existing.get("capabilities", {})),
        "state": data.get("state", existing.get("state", {})),
        "status": status,
        "last_seen": data.get("last_seen") or existing.get("last_seen") or _now_iso(),
    }


def get_device(device_uuid: str) -> Dict[str, Any] | None:
    return _device_ref(device_uuid).get()


def register_device(device_uuid: str, data: Dict[str, Any]) -> Dict[str, Any]:
    device = _build_device(device_uuid, data)
    _device_ref(device_uuid).set(device)
    return device


def update_device(device_uuid: str, data: Dict[str, Any]) -> Dict[str, Any]:
    existing = get_device(device_uuid)

    if not existing:
        raise ValueError("Device not found")

    updated = _build_device(device_uuid, data, existing=existing)
    _device_ref(device_uuid).set(updated)
    return updated


def list_devices() -> list[Dict[str, Any]]:
    devices = _devices_ref().get() or {}
    return list(devices.values())


def delete_device(device_uuid: str) -> Dict[str, Any] | None:
    device = get_device(device_uuid)
    if not device:
        return None

    _pending_commands_ref(device_uuid).delete()
    _device_ref(device_uuid).delete()
    return device


def update_last_seen(device_uuid: str, timestamp: datetime) -> Dict[str, Any]:
    device = get_device(device_uuid)
    if not device:
        return {"error": "device not found", "device_uuid": device_uuid}

    device["last_seen"] = timestamp.isoformat()
    _device_ref(device_uuid).set(device)
    return device


def update_device_state(
    device_uuid: str,
    reported_state: Dict[str, Any],
    status: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any] | None:
    device = get_device(device_uuid)
    if not device:
        return None

    current_state = device.get("state", {})
    current_state.update(reported_state)
    device["state"] = current_state

    current_status = device.get("status", {})
    if status:
        current_status.update(status)
    current_status["connected"] = True
    device["status"] = current_status
    device["last_seen"] = _now_iso()

    _device_ref(device_uuid).set(device)
    return device


def enqueue_command(device_uuid: str, payload: Dict[str, Any]) -> None:
    _pending_commands_ref(device_uuid).push(payload)


def pop_next_command(device_uuid: str) -> Dict[str, Any] | None:
    queue = _pending_commands_ref(device_uuid).get() or {}
    if not queue:
        return None
    return queue.pop(0)

def mark_stale_devices_offline(threshold_seconds: int = 30) -> list[str]:
    """
    Checks all devices and marks them as offline (connected=False) 
    if their last_seen is older than threshold_seconds.
    Returns a list of device_uuids that were marked offline.
    """
    now = datetime.now(timezone.utc)
    marked_offline = []
    
    for device_uuid, device in _DEVICES.items():
        # Skip if already offline
        status = device.get("status", {})
        if not status.get("connected", False):
            continue
            
        last_seen_str = device.get("last_seen")
        if not last_seen_str:
            continue
            
        try:
            last_seen_dt = datetime.fromisoformat(last_seen_str)
            diff = (now - last_seen_dt).total_seconds()
            
            if diff > threshold_seconds:
                # Mark as offline
                status["connected"] = False
                device["status"] = status
                marked_offline.append(device_uuid)
        except ValueError:
            pass
            
    return marked_offline

    
