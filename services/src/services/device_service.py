from datetime import datetime, timezone
from fastapi import HTTPException
from services.src.firebase import device_store
from typing import Any, Dict


def register_device(device_uuid: str, device_type: str | None, capabilities: list[str]):
    return device_store.register_device(
        device_uuid,
        {"device_type": device_type, "capabilities": capabilities},
    )


def list_devices(device_type: str | None = None):
    devices = device_store.list_devices()
    if device_type:
        devices = [d for d in devices if d.get("device_type") == device_type]
    return devices

def get_device(device_uuid: str)-> Dict[str, Any]:
    device = device_store.get_device(device_uuid)

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return device

def delete_device(device_uuid:str) -> dict[str, str]:
    device = device_store.delete_device(device_uuid)

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {
        "message": "Device deleted successfully",
        "device_uuid": device_uuid
    }

def heartbeat(device_uuid: str):
    now = datetime.now(timezone.utc)
    return device_store.update_last_seen(device_uuid, now)

