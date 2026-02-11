from datetime import datetime
from typing import Any, Dict


# In-memory store (dev/test)
_DEVICES: Dict[str, Dict[str, Any]] = {}


def register_device(device_uuid: str, data: Dict[str, Any]) -> Dict[str, Any]:
    device = {
        "device_uuid": device_uuid,
        "device_type": data.get("device_type"),
        "capabilities": data.get("capabilities", []),
        "last_seen": data.get("last_seen"),
    }
    _DEVICES[device_uuid] = device
    return device


def get_device(device_uuid: str) -> Dict[str, Any] | None:
    return _DEVICES.get(device_uuid)


def list_devices() -> list[Dict[str, Any]]:
    return list(_DEVICES.values())


def update_last_seen(device_uuid: str, timestamp: datetime) -> Dict[str, Any]:
    device = _DEVICES.get(device_uuid)
    if not device:
        return {"error": "device not found", "device_uuid": device_uuid}

    device["last_seen"] = timestamp.isoformat()
    return device
