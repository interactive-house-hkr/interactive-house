from datetime import datetime, timezone
import uuid
from services.src.firebase import device_store
from services.src.schemas.device_schema import ConnectDeviceBody, CommandPayload
from fastapi import HTTPException
from typing import Any, Dict
from services.src.bridge.bridge import dispatch_command

OFFLINE_THRESHOLD_SECONDS = 30


def is_device_online(device: dict) -> bool:
    """Check whether a device is considered online based on its last_seen timestamp.

    A device is considered online if its last_seen timestamp is within
    OFFLINE_THRESHOLD_SECONDS of the current UTC time.

    Args:
        device (dict): A device dictionary containing at least a 'last_seen' ISO 8601 timestamp.

    Returns:
        bool: True if the device is online, False if it is offline or has no last_seen value.
    """
    last_seen = device.get("last_seen")

    if not last_seen:
        return False

    last_seen_dt = datetime.fromisoformat(last_seen)
    now = datetime.now(timezone.utc)

    diff = (now - last_seen_dt).total_seconds()
    return diff <= OFFLINE_THRESHOLD_SECONDS


def connect_device(payload: ConnectDeviceBody) -> Dict[str, Any]:
    """Register or update one or more devices from a connection payload.

    For each device in the payload, if a device_uuid is provided and already
    exists in Firebase, the device is updated. If no device_uuid is provided,
    a new UUID is generated and the device is registered.

    Args:
        payload (ConnectDeviceBody): The request body containing a dictionary
            of devices to connect, each with optional device_uuid and device data.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - message (str): Confirmation message.
            - devices (dict): The saved device data keyed by device_uuid.
            - generated_uuids (dict): Any newly generated UUIDs keyed by device key.
    """
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
    """Retrieve all registered devices, optionally filtered by device type.

    Fetches all devices from Firebase and appends an is_online field to each
    device based on the last_seen timestamp.

    Args:
        device_type (str | None): Optional device type to filter by.
            If None, all devices are returned.

    Returns:
        list[dict]: A list of device dictionaries, each including an is_online field.
    """
    devices = device_store.list_devices()

    if device_type:
        devices = [d for d in devices if d.get("device_type") == device_type]

    for device in devices:
        device["is_online"] = is_device_online(device)

    return devices


def get_device(device_uuid: str) -> Dict[str, Any]:
    """Retrieve a single device by its UUID.

    Fetches the device from Firebase and appends an is_online field based
    on the last_seen timestamp.

    Args:
        device_uuid (str): The unique identifier of the device.

    Raises:
        HTTPException: 404 if no device with the given UUID exists.

    Returns:
        Dict[str, Any]: The device data dictionary including an is_online field.
    """
    device = device_store.get_device(device_uuid)

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    device["is_online"] = is_device_online(device)

    return device


def delete_device(device_uuid: str) -> dict[str, str]:
    """Delete a device from Firebase by its UUID.

    Args:
        device_uuid (str): The unique identifier of the device to delete.

    Raises:
        HTTPException: 404 if no device with the given UUID exists.

    Returns:
        dict[str, str]: A confirmation dictionary containing:
            - message (str): Confirmation message.
            - device_uuid (str): The UUID of the deleted device.
    """
    device = device_store.delete_device(device_uuid)

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return {
        "message": "Device deleted successfully",
        "device_uuid": device_uuid
    }


def heartbeat(device_uuid: str):
    """Update the last_seen timestamp for a device and sweep for stale devices.

    Called by a device to signal that it is still active. Updates the device's
    last_seen field in Firebase to the current UTC time. After updating, triggers
    a sweep to mark any devices that have not sent a heartbeat within
    OFFLINE_THRESHOLD_SECONDS as offline.

    Args:
        device_uuid (str): The unique identifier of the device sending the heartbeat.

    Raises:
        HTTPException: 404 if no device with the given UUID exists.

    Returns:
        dict: The result from updating the last_seen timestamp in Firebase.
    """
    now = datetime.now(timezone.utc)
    result = device_store.update_last_seen(device_uuid, now)

    if "error" in result:
        raise HTTPException(status_code=404, detail="Device not found")

    # Mark any stale devices as offline
    device_store.mark_stale_devices_offline(OFFLINE_THRESHOLD_SECONDS)

    return result


def get_next_command(device_uuid: str) -> Dict[str, Any]:
    """Retrieve and remove the next pending command for a device.

    Checks that the device exists in Firebase, then pops the next command
    from the device's command queue. Returns None as the command value if
    the queue is empty.

    Args:
        device_uuid (str): The unique identifier of the device.

    Raises:
        HTTPException: 404 if no device with the given UUID exists.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - device_uuid (str): The device's UUID.
            - command (dict | None): The next command payload, or None if the queue is empty.
    """
    device = device_store.get_device(device_uuid)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    command = device_store.pop_next_command(device_uuid)
    return {
        "device_uuid": device_uuid,
        "command": command,
    }


def handle_command_ack(device_uuid: str, status: str, reported_state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle a command acknowledgement from a device.

    Updates the device's reported state and records the last command status
    in Firebase after the device has executed a command.

    Args:
        device_uuid (str): The unique identifier of the device.
        status (str): The result status of the command execution (e.g. 'ok', 'error').
        reported_state (Dict[str, Any]): The device's current state as reported after execution.

    Raises:
        HTTPException: 404 if no device with the given UUID exists.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - message (str): Confirmation message.
            - device_uuid (str): The device's UUID.
            - status (str): The reported command status.
            - reported_state (dict): The device's reported state.
    """
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
    """Dispatch a command to a device via REST queue or the bridge.

    Determines the transport mode for the device. If the device uses REST
    transport, the command is enqueued in Firebase for the device to poll.
    Otherwise, the command is dispatched immediately via the bridge service.

    Args:
        device_uuid (str): The unique identifier of the target device.
        payload (CommandPayload): The command payload containing the desired state.

    Raises:
        HTTPException: 404 if no device with the given UUID exists.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - message (str): Confirmation message.
            - device_uuid (str): The target device's UUID.
            - sent (bool): Whether the command was successfully dispatched.
            - delivery (str): Delivery method used, either 'queued' or 'bridge'.
            - payload (dict): The full command payload that was sent.
    """
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
