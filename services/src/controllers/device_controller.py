from services.src.services import device_service
from services.src.schemas.device_schema import ConnectDeviceBody, CommandPayload
from services.src.utils.logger import get_logger

logger = get_logger("device_controller")


# -------------------------
# Devices
# -------------------------

def list_devices(type: str | None = None):
    return device_service.list_devices(device_type=type)


def connect_device(payload: ConnectDeviceBody):
    return device_service.connect_device(payload)


def get_device(device_uuid: str):
    return device_service.get_device(device_uuid)


def update_device(device_uuid: str):
    # TODO: return device_service.update_device(device_uuid, payload, user)
    return {"todo": "update_device service call", "device_uuid": device_uuid}


def delete_device(device_uuid: str):
    return device_service.delete_device(device_uuid)


# -------------------------
# Commands
# -------------------------

async def post_command(device_uuid: str, payload: CommandPayload):
    return await device_service.post_command(
        device_uuid=device_uuid,
        payload=payload,
    )


# -------------------------
# Bridge Integration
# -------------------------

def handle_command_ack(device_uuid: str, status: str, state: dict):
    """
    Handle command acknowledgement from device.
    Updates the device's state.
    """
    try:
        logger.info(f"Updating device {device_uuid} with state: {state}")
        return device_service.handle_command_ack(device_uuid, status, state)
    except Exception as e:
        logger.error(f"Failed to handle command ACK: {e}")
        raise


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
