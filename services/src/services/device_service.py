from datetime import datetime, timezone
from services.src.firebase import device_store


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


def heartbeat(device_uuid: str):
    now = datetime.now(timezone.utc)
    return device_store.update_last_seen(device_uuid, now)

