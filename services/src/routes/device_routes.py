from fastapi import APIRouter, Depends
from services.src.services.auth_service import optional_user
from services.src.schemas.device_schema import ConnectDeviceBody
from services.src.controllers import device_controller as controller


router = APIRouter(
    prefix="/devices",
    tags=["devices"],
)

# -------------------------
# Devices
# -------------------------

@router.get("")
def list_devices(type: str | None = None, user=Depends(optional_user)):
    return controller.list_devices(type=type)

@router.get("/{device_uuid}")
def get_device(device_uuid: str, user=Depends(optional_user)):
    return controller.get_device(device_uuid=device_uuid)

@router.delete("/{device_uuid}")
def delete_device(device_uuid: str, user=Depends(optional_user)):
    return controller.delete_device(device_uuid=device_uuid)

# -------------------------
# Commands
# -------------------------

@router.post("/{device_uuid}/commands")
def post_command(device_uuid: str, user=Depends(optional_user)):
    return controller.post_command(device_uuid=device_uuid)

# -------------------------
# Health
# -------------------------

@router.post("/{device_uuid}/heartbeat")
def heartbeat(device_uuid: str):
    return controller.heartbeat(device_uuid=device_uuid)

# -------------------------
# Events (placeholder)
# -------------------------

@router.get("/events")
def events():
    return controller.events()
