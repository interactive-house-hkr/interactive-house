from fastapi import APIRouter, Depends
from services.src.services.auth_service import optional_user
from services.src.utils.logger import get_logger

router = APIRouter(
    prefix="/devices",
    tags=["devices"]
)

logger = get_logger(__name__)

# -------------------------
# State
# -------------------------

@router.get("/{deviceUuid}/state")
def get_state(deviceUuid: str, user=Depends(optional_user)):
    logger.info(f"GET /devices/{deviceUuid}/state")
    # TODO: return state_service.get_state(deviceUuid, user)
    return {"todo": "get_state service call", "deviceUuid": deviceUuid}

@router.patch("/{deviceUuid}/state")
def patch_state(deviceUuid: str, user=Depends(optional_user)):
    logger.info(f"PATCH /devices/{deviceUuid}/state")
    # TODO: return state_service.update_state(deviceUuid, payload, user)
    return {"todo": "update_state service call", "deviceUuid": deviceUuid}