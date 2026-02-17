from fastapi import APIRouter, Depends
from services.src.services.auth_service import optional_user
from services.src.utils.logger import get_logger
from services.src.services import device_service
from services.src.schemas.device_schema import RegisterDeviceBody


router = APIRouter(
    prefix="/devices",
    tags=["devices"],
)

logger = get_logger(__name__)

# -------------------------
# Devices
# -------------------------

@router.get("")
def list_devices(type: str | None = None, user=Depends(optional_user)):
    logger.info("GET /devices")
    return device_service.list_devices(device_type=type)


@router.post("/{deviceuuid}")
def register_device(deviceuuid: str, payload: RegisterDeviceBody, user=Depends(optional_user)):
    logger.info(f"POST /devices/{deviceuuid}")
    return device_service.register_device(
        device_uuid=deviceuuid,
        device_type=payload.device_type,
        capabilities=payload.capabilities,
    )


@router.get("/{deviceuuid}")
def get_device(deviceuuid: str, user=Depends(optional_user)):
    logger.info(f"GET /devices/{deviceuuid}")
    # TODO: return device_service.get_device(deviceUuid, user)
    return {"todo": "get_device service call", "deviceuuid": deviceuuid}


@router.patch("/{deviceuuid}")
def update_device(deviceuuid: str, user=Depends(optional_user)):
    logger.info(f"PATCH /devices/{deviceuuid}")
    # TODO: return device_service.update_device(deviceuuid, payload, user)
    return {"todo": "update_device service call", "deviceuuid": deviceuuid}


@router.delete("/{deviceuuid}")
def delete_device(deviceuuid: str, user=Depends(optional_user)):
    logger.info(f"DELETE /devices/{deviceuuid}")
    # TODO: return device_service.delete_device(deviceuuid, user)
    return {"todo": "delete_device service call", "deviceUuid": deviceuuid}

# -------------------------
# Commands
# -------------------------

@router.post("/{deviceuuid}/commands")
def post_command(deviceuuid: str, user=Depends(optional_user)):
    logger.info(f"POST /devices/{deviceuuid}/commands")
    # TODO: return command_service.queue_command(deviceuuid, payload, user)
    return {"todo": "queue_command service call", "deviceuuid": deviceuuid}

# -------------------------
# Health
# -------------------------

@router.post("/{deviceuuid}/heartbeat")
def heartbeat(deviceuuid: str):
    logger.info(f"POST /devices/{deviceuuid}/heartbeat")
    return device_service.heartbeat(deviceuuid)

# -------------------------
# Events (placeholder)
# -------------------------

@router.get("/events")
def events():
    logger.info("GET /devices/events")
    # TODO: return event_service.subscribe()
    return {"todo": "events service call"}

