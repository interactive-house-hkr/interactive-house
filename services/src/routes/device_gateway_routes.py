from fastapi import APIRouter

from services.src.controllers import device_controller as controller
from services.src.schemas.device_schema import ConnectDeviceBody, CommandAckPayload


router = APIRouter(
    prefix="/device-gateway",
    tags=["device-gateway"],
)


@router.post("/connect")
def connect_device(payload: ConnectDeviceBody):
    return controller.connect_device(payload)


@router.post("/{device_uuid}/heartbeat")
def heartbeat(device_uuid: str):
    return controller.heartbeat(device_uuid=device_uuid)


@router.get("/{device_uuid}/commands/next")
def get_next_command(device_uuid: str):
    return controller.get_next_command(device_uuid=device_uuid)


@router.post("/{device_uuid}/command-ack")
def post_command_ack(device_uuid: str, payload: CommandAckPayload):
    return controller.handle_command_ack(
        device_uuid=device_uuid,
        status=payload.status,
        reported_state=payload.reported_state,
    )
