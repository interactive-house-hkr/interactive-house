from datetime import datetime, timezone
import uuid
from services.src.firebase import device_store
from typing import Any, Dict


def connect_device(payload) -> Dict[str, Any]:
    data = payload.model_dump()
    incoming_uuid = data.get("device_uuid")

    if incoming_uuid:
        existing_device = device_store.get_device(incoming_uuid)

        if existing_device:
            updated_device = device_store.update_device(incoming_uuid, data)
            return {
                "message": "Device connected",
                "device": updated_device,
            }

        created_device = device_store.register_device(incoming_uuid, data)
        return {
            "message": "Device connected with provided UUID",
            "device": created_device,
        }

    new_uuid = str(uuid.uuid4())
    data["device_uuid"] = new_uuid
    created_device = device_store.register_device(new_uuid, data)

    return {
        "message": "New device connected",
        "device": created_device,
    }

def list_devices(device_type: str | None = None):
    devices = device_store.list_devices()
    if device_type:
        devices = [d for d in devices if d.get("device_type") == device_type]
    return devices


def heartbeat(device_uuid: str):
    now = datetime.now(timezone.utc)
    return device_store.update_last_seen(device_uuid, now)

