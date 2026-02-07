from fastapi import APIRouter, Depends
from services.src.services.auth_service import optional_user
from services.src.utils.logger import get_logger

router = APIRouter(
    prefix="/devices",
    tags=["devices"]
)

logger = get_logger(__name__)

# -------------------------
# Devices
# -------------------------

@router.get("")
def list_devices(type: str | None = None, user=Depends(optional_user)):
    logger.info("GET /devices")
    # TODO: return device_service.list_devices(user=user, device_type=type)
    return {"todo": "list_devices service call"}

@router.post("/{deviceUuid}")
def register_device(deviceUuid: str, user=Depends(optional_user)):
    logger.info(f"POST /devices/{deviceUuid}")
    # TODO: return device_service.register_device(deviceUuid, payload, user)
    return {"todo": "register_device service call", "deviceUuid": deviceUuid}

@router.get("/{deviceUuid}")
def get_device(deviceUuid: str, user=Depends(optional_user)):
    logger.info(f"GET /devices/{deviceUuid}")
    # TODO: return device_service.get_device(deviceUuid, user)
    return {"todo": "get_device service call", "deviceUuid": deviceUuid}

@router.patch("/{deviceUuid}")
def update_device(deviceUuid: str, user=Depends(optional_user)):
    logger.info(f"PATCH /devices/{deviceUuid}")
    # TODO: return device_service.update_device(deviceUuid, payload, user)
    return {"todo": "update_device service call", "deviceUuid": deviceUuid}

@router.delete("/{deviceUuid}")
def delete_device(deviceUuid: str, user=Depends(optional_user)):
    logger.info(f"DELETE /devices/{deviceUuid}")
    # TODO: return device_service.delete_device(deviceUuid, user)
    return {"todo": "delete_device service call", "deviceUuid": deviceUuid}

# -------------------------
# Commands
# -------------------------

@router.post("/{deviceUuid}/commands")
def post_command(deviceUuid: str, user=Depends(optional_user)):
    logger.info(f"POST /devices/{deviceUuid}/commands")
    # TODO: return command_service.queue_command(deviceUuid, payload, user)
    return {"todo": "queue_command service call", "deviceUuid": deviceUuid}

# -------------------------
# Health
# -------------------------

@router.post("/{deviceUuid}/heartbeat")
def heartbeat(deviceUuid: str):
    logger.info(f"POST /devices/{deviceUuid}/heartbeat")
    # TODO: return device_service.heartbeat(deviceUuid)
    return {"todo": "heartbeat service call", "deviceUuid": deviceUuid}

# -------------------------
# Events (placeholder)
# -------------------------

@router.get("/events")
def events():
    logger.info("GET /devices/events")
    # TODO: return event_service.subscribe()
    return {"todo": "events service call"}
