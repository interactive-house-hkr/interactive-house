from datetime import datetime, timezone
import uuid
from services.src.firebase import device_store
from services.src.schemas.device_schema import ConnectDeviceBody, CommandPayload
from fastapi import HTTPException
from typing import Any, Dict
from services.src.bridge.bridge import dispatch_command


OFFLINE_THRESHOLD_SECONDS = 30


def is_device_online(device: dict) -> bool:
    last_seen = device.get("last_seen")

    if not last_seen:
        return False

    last_seen_dt = datetime.fromisoformat(last_seen)
    now = datetime.now(timezone.utc)

    diff = (now - last_seen_dt).total_seconds()
    return diff <= OFFLINE_THRESHOLD_SECONDS


def connect_device(payload: ConnectDeviceBody) -> Dict[str, Any]:
    data = payload.model_dump(exclude_unset=True)
    devices = data.get("devices", {})

    connected_devices: Dict[str, Dict[str, Any]] = {}
    generated_uuids: Dict[str, str] = {}

    for device_key, device_data in devices.items():
        incoming_uuid = device_data.get("device_uuid")

        if not incoming_uuid:
            incoming_uuid = str(uuid.uuid4())
            device_data["device_uuid"] = incoming_uuid
            generated_uuids[device_key] = incoming_uuid

        existing_device = device_store.get_device(incoming_uuid)

        if existing_device:
            saved_device = device_store.update_device(incoming_uuid, device_data)
        else:
            saved_device = device_store.register_device(incoming_uuid, device_data)

        connected_devices[incoming_uuid] = saved_device

    return {
        "message": "Devices connected",
        "devices": connected_devices,
        "generated_uuids": generated_uuids,
    }


def list_devices(device_type: str | None = None):
    devices = device_store.list_devices()

    if device_type:
        devices = [d for d in devices if d.get("device_type") == device_type]

    for device in devices:
        device["is_online"] = is_device_online(device)

    return devices


def get_device(device_uuid: str) -> Dict[str, Any]:
    device = device_store.get_device(device_uuid)

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    device["is_online"] = is_device_online(device)

    return device


def delete_device(device_uuid: str) -> dict[str, str]:
    device = device_store.delete_device(device_uuid)

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return {
        "message": "Device deleted successfully",
        "device_uuid": device_uuid
    }


def heartbeat(device_uuid: str):
    now = datetime.now(timezone.utc)
    result = device_store.update_last_seen(device_uuid, now)

    if "error" in result:
        raise HTTPException(status_code=404, detail="Device not found")

    # Mark any stale devices as offline
    device_store.mark_stale_devices_offline(OFFLINE_THRESHOLD_SECONDS)

    return result



def get_next_command(device_uuid: str) -> Dict[str, Any]:
    device = device_store.get_device(device_uuid)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    command = device_store.pop_next_command(device_uuid)
    return {
        "device_uuid": device_uuid,
        "command": command,
    }


def handle_command_ack(device_uuid: str, status: str, reported_state: Dict[str, Any]) -> Dict[str, Any]:
    device = device_store.update_device_state(
        device_uuid,
        reported_state,
        status={"last_command_status": status},
    )

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return {
        "message": "Command acknowledgement received",
        "device_uuid": device_uuid,
        "status": status,
        "reported_state": reported_state,
    }


async def post_command(device_uuid: str, payload: CommandPayload) -> Dict[str, Any]:
    device = device_store.get_device(device_uuid)

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    command_payload = {
        "type": "COMMAND",
        "device_uuid": device_uuid,
        "state": payload.state,
    }

    transport = device.get("transport", {})
    transport_mode = transport.get("mode")
    transport_protocol = transport.get("protocol")

    if transport_mode == "rest" or transport_protocol == "rest":
        device_store.enqueue_command(device_uuid, command_payload)
        sent = True
        delivery = "queued"
    else:
        sent = await dispatch_command(command_payload)
        delivery = "bridge"

    return {
        "message": "Command dispatched",
        "device_uuid": device_uuid,
        "sent": sent,
        "delivery": delivery,
        "payload": command_payload,
    }
