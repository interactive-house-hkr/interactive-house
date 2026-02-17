from fastapi import APIRouter, Depends
from services.src.services.auth_service import optional_user
from services.src.controllers import state_controller as controller

router = APIRouter(
    prefix="/devices",
    tags=["devices"]
)

# -------------------------
# State
# -------------------------

@router.get("/{device_uuid}/state")
def get_state(device_uuid: str, user=Depends(optional_user)):
    return controller.get_state(device_uuid=device_uuid)

@router.patch("/{device_uuid}/state")
def patch_state(device_uuid: str, updates: dict, user=Depends(optional_user)):
    return controller.patch_state(device_uuid=device_uuid, updates=updates)