from fastapi import APIRouter, Depends
from services.src.services.auth_service import optional_user
from services.src.controllers import unit_controller as controller

router = APIRouter(
    prefix="/units",
    tags=["units"],
)

# -------------------------
# Read devices
# -------------------------

@router.get("/devices")
def list_devices(type: str | None = None, user=Depends(optional_user)):
    return controller.list_devices(type=type)


@router.get("/devices/{device_uuid}")
def get_device(device_uuid: str, user=Depends(optional_user)):
    return controller.get_device(device_uuid=device_uuid)


# -------------------------
# Commands
# -------------------------

@router.post("/devices/{device_uuid}/commands")
def post_command(device_uuid: str, user=Depends(optional_user)):
    return controller.post_command(device_uuid=device_uuid)