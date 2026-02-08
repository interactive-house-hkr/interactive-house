from datetime import datetime
from typing import Dict, Any

# In-memory store (för dev/test)
_DEVICES: Dict[str, Dict[str, Any]] = {}


def register_device(device_uuid: str, data: Dict[str, Any]):
    device = {
        "device_uuid": device_uuid,
        "device_type": data.get("device_type"),
        "capabilities": data.get("capabilities", []),
    }
    _DEVICES[device_uuid] = device
    return device


def get_device(device_uuid: str):
    return _DEVICES.get(device_uuid)


def list_devices():
    return list(_DEVICES.values())


def update_last_seen(device_uuid: str, timestamp: datetime):
    device = _DEVICES.get(device_uuid)
    if not device:
        return {"error": "device not found", "device_uuid": device_uuid}

    device["last_seen"] = timestamp.isoformat()
    return device
