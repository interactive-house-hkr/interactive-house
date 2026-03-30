import asyncio
import json
from datetime import datetime

from bleak import BleakClient
import serial

from services.src.utils.logger import get_logger
from services.src.controllers import device_controller
from services.src.schemas.device_schema import ConnectDeviceBody

logger = get_logger("bridge_message_handler")


def now() -> str:
    return datetime.now().isoformat()


async def handle_connect_message(transport_type: str, transport, message: str):
    try:
        parsed = json.loads(message)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON from device: {e}")
        # Removed debug log to avoid cluttered logs
        # logger.debug(f"Raw message: {message}")
        return

    device_uuid = parsed.get("device_uuid")
    device_type = parsed.get("device_type")

    if not device_uuid or not device_type:
        logger.warning(
            f"CONNECT message missing device_uuid or device_type: {parsed}")
        return

    # Build a state from extracted state fields in connect message
    state = {}
    if "power" in parsed:
        state["power"] = parsed["power"]
    if "open" in parsed:
        state["open"] = parsed["open"]

    logger.info(
        f"Device connected: uuid={device_uuid}, type={device_type}, state={state}")

    try:
        payload = ConnectDeviceBody(devices={
            device_uuid: {
                "device_uuid": device_uuid,
                "type": device_type,
                "state": state
            }
        })
        result = device_controller.connect_device(payload)
        logger.info(f"Connect result: {result}")
    except Exception as e:
        logger.error(f"Failed to connect device {device_uuid}: {e}")
        return

"""response_payload = {
        "type": "CONNECT_ACK",
        "device_uuid": device_uuid,
        "message": result.get("message"),
        "server_time": now(),
    }

    await asyncio.sleep(1)

    if transport_type == "ble":
        from services.src.bridge.ble_controller import send_ble_json
        sent = await send_ble_json(transport, response_payload)
    else:
        from services.src.bridge.usb_controller import send_usb_json
        sent = await send_usb_json(transport, response_payload)

    if sent:
        logger.info(f"Sent CONNECT_ACK back {device_uuid}")
    else:
        logger.error(
            f"Failed to send CONNECT_ACK back {device_uuid}") """


async def handle_heartbeat_message(message: str):
    try:
        parsed = json.loads(message)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid HEARTBEAT JSON: {e}")
        logger.debug(f"Raw message: {message}")
        return

    device_uuid = parsed.get("device_uuid")
    if not device_uuid:
        logger.warning("HEARTBEAT missing device_uuid")
        return

    try:
        result = device_controller.heartbeat(device_uuid)
        logger.info(
            f"Heartbeat updated for device_uuid={device_uuid}: {result}")
    except Exception as e:
        logger.error(f"Failed to process heartbeat for {device_uuid}: {e}")


async def handle_command_ack(message: str):
    try:
        parsed = json.loads(message)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid COMMAND_ACK JSON: {e}")
        logger.debug(f"Raw message: {message}")
        return

    device_uuid = parsed.get("device_uuid")
    status = parsed.get("status")
    reported_state = parsed.get("reported_state", {})

    logger.info(
        f"Command ACK received from device_uuid={device_uuid}, "
        f"status={status}, reported_state={reported_state}"
    )

    try:
        # Update device state with reported_state from ACK
        device_controller.handle_command_ack(
            device_uuid, status, reported_state)
    except Exception as e:
        logger.error(f"Failed to update state from command ACK: {e}")


async def handle_incoming_message(transport_type: str, transport, message: str):
    try:
        parsed = json.loads(message)
    except json.JSONDecodeError:
        logger.info(
            f"Received non-JSON {transport_type.upper()} message: {message}")
        return

    message_type = parsed.get("type")

    if message_type == "CONNECT":
        await handle_connect_message(transport_type, transport, message)
        return

    if message_type == "HEARTBEAT":
        await handle_heartbeat_message(message)
        return

    if message_type == "COMMAND_ACK":
        await handle_command_ack(message)
        return

    logger.info(
        f"Unhandled {transport_type.upper()} message type: {message_type}")
