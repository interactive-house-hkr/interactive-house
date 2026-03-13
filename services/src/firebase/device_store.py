from datetime import datetime, timezone
from typing import Any, Dict, Optional


# In-memory store (dev/test)
_DEVICES: Dict[str, Dict[str, Any]] = {}


def get_device(device_uuid: str) -> Dict[str, Any] | None:
    return _DEVICES.get(device_uuid)


def register_device(device_uuid: str, data: Dict[str, Any]) -> Dict[str, Any]:
    status = data.get("status", {})
    status["connected"] = True

    device = {
        "device_uuid": device_uuid,
        "device_type": data.get("device_type"),
        "transport": data.get("transport", {}),
        "capabilities": data.get("capabilities", []),
        "desired_state": data.get("desired_state", {}),
        "reported_state": data.get("reported_state", {}),
        "status": status,
        "last_seen": data.get("last_seen") or datetime.now(timezone.utc).isoformat(),
    }

    _DEVICES[device_uuid] = device
    return device


def update_device(device_uuid: str, data: Dict[str, Any]) -> Dict[str, Any]:
    existing = _DEVICES.get(device_uuid)

    if not existing:
        raise ValueError("Device not found")

    existing["device_type"] = data.get("device_type", existing.get("device_type"))
    existing["transport"] = data.get("transport", existing.get("transport", {}))
    existing["capabilities"] = data.get("capabilities", existing.get("capabilities", []))
    existing["desired_state"] = data.get("desired_state", existing.get("desired_state", {}))
    existing["reported_state"] = data.get("reported_state", existing.get("reported_state", {}))

    existing_status = existing.get("status", {})
    incoming_status = data.get("status", {})
    existing_status.update(incoming_status)
    existing_status["connected"] = True
    existing["status"] = existing_status

    existing["last_seen"] = data.get("last_seen") or datetime.now(timezone.utc).isoformat()

    return existing


def list_devices() -> list[Dict[str, Any]]:
    return list(_DEVICES.values())


def update_last_seen(device_uuid: str, timestamp: datetime) -> Dict[str, Any]:
    device = _DEVICES.get(device_uuid)
    if not device:
        return {"error": "device not found", "device_uuid": device_uuid}

    device["last_seen"] = timestamp.isoformat()
    return device
