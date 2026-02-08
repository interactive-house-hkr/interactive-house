from services.src.firebase import device_store


def list_devices(device_type: str | None = None):
    devices = device_store.list_devices()
    if device_type:
        devices = [d for d in devices if d.get("device_type") == device_type]
    return devices


def register_device(device_uuid: str, device_type: str | None = None, capabilities: list[str] | None = None):
    data = {
        "device_type": device_type,
        "capabilities": capabilities or [],
    }
    return device_store.register_device(device_uuid, data)


def get_device(device_uuid: str):
    return device_store.get_device(device_uuid)
