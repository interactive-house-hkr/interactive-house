from services.src.services import device_service
from services.src.schemas.device_schema import ConnectDeviceBody


# -------------------------
# Devices
# -------------------------

def list_devices(type: str | None = None):
    return device_service.list_devices(device_type=type)

def connect_device(payload: ConnectDeviceBody):
    return device_service.connect_device(payload)

def get_device(device_uuid: str):
    # TODO: return device_service.get_device(device_uuid, user)
    return {"todo": "get_device service call", "device_uuid": device_uuid}

def update_device(device_uuid: str):
    # TODO: return device_service.update_device(device_uuid, payload, user)
    return {"todo": "update_device service call", "device_uuid": device_uuid}

def delete_device(device_uuid: str):
    # TODO: return device_service.delete_device(device_uuid, user)
    return {"todo": "delete_device service call", "device_uuid": device_uuid}

# -------------------------
# Commands
# -------------------------

def post_command(device_uuid: str):
    # TODO: return command_service.queue_command(device_uuid, payload, user)
    return {"todo": "queue_command service call", "device_uuid": device_uuid}

# -------------------------
# Health
# -------------------------

def heartbeat(device_uuid: str):
    return device_service.heartbeat(device_uuid)

# -------------------------
# Events (placeholder)
# -------------------------

def events():
    # TODO: return event_service.subscribe()
    return {"todo": "events service call"}
