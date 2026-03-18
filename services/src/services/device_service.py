from datetime import datetime, timezone
import uuid
from services.src.firebase import device_store
from services.src.schemas.device_schema import ConnectDeviceBody
from fastapi import HTTPException
from typing import Any, Dict


def connect_device(payload: ConnectDeviceBody) -> Dict[str, Any]:
    data = payload.model_dump()
    devices = data.get("devices", {})

    connected_devices: Dict[str, Dict[str, Any]] = {}
    generated_uuids: Dict[str, str] = {}

    for device_key, device_data in devices.items():
        incoming_uuid = device_data.get("device_uuid")

        if not incoming_uuid:
            incoming_uuid = str(uuid.uuid4())
            device_data["device_uuid"] = incoming_uuid
            generated_uuids[device_key] = incoming_uuid

        existing_device = device_store.get_device(incoming_uuid)

        if existing_device:
            saved_device = device_store.update_device(incoming_uuid, device_data)
        else:
            saved_device = device_store.register_device(incoming_uuid, device_data)

        connected_devices[incoming_uuid] = saved_device

    return {
        "message": "Devices connected",
        "devices": connected_devices,
        "generated_uuids": generated_uuids,
    }


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

def post_command(device_uuid: str, command: str, params: dict | None = None) -> Dict[str, Any]:
    device = device_store.get_device(device_uuid)

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return {
        "message": "Command handed off to service",
        "device_uuid": device_uuid,
        "command": command,
        "params": params or {},
    }