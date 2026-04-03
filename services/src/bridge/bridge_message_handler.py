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
        return

    # Support both batch format {"devices": {...}} and individual Arduino format
    # Arduino sends: {"type":"CONNECT","device_uuid":"light-1","device_type":"light","power":false}
    if "devices" in parsed:
        # Batch format from REST simulators
        try:
            payload = ConnectDeviceBody(**parsed)
        except Exception as e:
            logger.error(f"Payload validation failed: {e}")
            return
    else:
        # Individual device format from Arduino
        device_uuid = parsed.get("device_uuid")
        device_type = parsed.get("device_type")

        if not device_uuid or not device_type:
            logger.warning(f"CONNECT message missing device_uuid or device_type: {parsed}")
            return

        # Build state from extracted fields in the connect message
        state = {}
        if "power" in parsed:
            state["power"] = parsed["power"]
        if "open" in parsed:
            state["open"] = parsed["open"]

        logger.info(f"Device connected: uuid={device_uuid}, type={device_type}, state={state}")

        try:
            payload = ConnectDeviceBody(devices={
                device_uuid: {
                    "device_uuid": device_uuid,
                    "type": device_type,
                    "transport": {"mode": "bridge", "protocol": "ble"},
                    "state": state
                }
            })
        except Exception as e:
            logger.error(f"Payload validation failed: {e}")
            return

    try:
        result = device_controller.connect_device(payload)
        logger.info(f"Connect result: {result}")
    except Exception as e:
        logger.error(f"Failed to connect devices: {e}")
        return

    # CONNECT_ACK disabled for Arduino — sending ACK interrupts reception of
    # multiple consecutive CONNECT messages from the Arduino (it sends 4 devices
    # one at a time with 100ms gaps). The Arduino does not wait for ACK.


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
        logger.info(f"Heartbeat updated for device_uuid={device_uuid}: {result}")
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
        device_controller.handle_command_ack(device_uuid, status, reported_state)
    except Exception as e:
        logger.error(f"Failed to update state from command ACK: {e}")


async def handle_incoming_message(transport_type: str, transport, message: str):
    try:
        parsed = json.loads(message)
    except json.JSONDecodeError:
        logger.info(f"Received non-JSON {transport_type.upper()} message: {message}")
        return

    message_type = parsed.get("type")

    if message_type == "DIAG":
        # Arduino sends diagnostics on startup — log for version verification
        aj_ver = parsed.get("arduino_json", "unknown")
        board = parsed.get("board", "unknown")
        sram = parsed.get("sram", "?")
        free_ram = parsed.get("free_ram", "?")
        logger.info(
            f"ARDUINO DIAGNOSTICS: ArduinoJson={aj_ver}, board={board}, "
            f"SRAM={sram} bytes, free_ram={free_ram} bytes"
        )
        # Validate ArduinoJson version
        if aj_ver != "unknown" and not aj_ver.startswith("6."):
            logger.error(
                f"ARDUINO VERSION MISMATCH: ArduinoJson {aj_ver} detected. "
                f"This bridge requires ArduinoJson v6.x. "
                f"v5.x has incompatible API, v7.x removed StaticJsonDocument."
            )
        # Warn if free RAM is low
        if isinstance(free_ram, int) and free_ram < 500:
            logger.warning(
                f"ARDUINO LOW MEMORY: Only {free_ram} bytes free. "
                f"Risk of crashes during JSON operations."
            )
        return

    if message_type == "CONNECT":
        await handle_connect_message(transport_type, transport, message)
        return

    if message_type == "HEARTBEAT":
        await handle_heartbeat_message(message)
        return

    if message_type == "COMMAND_ACK":
        await handle_command_ack(message)
        return

    logger.info(f"Unhandled {transport_type.upper()} message type: {message_type}")