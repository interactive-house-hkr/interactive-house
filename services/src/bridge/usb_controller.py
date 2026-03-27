import asyncio
import json
import serial
import serial.tools.list_ports

from services.src.utils.logger import get_logger
from services.src.bridge.bridge_message_handler import handle_incoming_message
from services.src.bridge.bridge_state import (
    set_active_usb_serial,
    clear_active_usb_serial,
    clear_device_transports_for,
)
from services.src.config.bridge_config import USB_BAUD, USB_PORT, CMD_DELAY

logger = get_logger("usb_controller")


def find_arduino_port():
    keywords = ["arduino", "ch340", "ch341", "usb serial", "usb-serial", "usbserial"]
    for port in serial.tools.list_ports.comports():
        desc = port.description.lower()
        if any(keyword in desc for keyword in keywords):
            return port.device
    return None


async def send_usb_json(ser: serial.Serial, payload: dict) -> bool:
    try:
        message = json.dumps(payload) + "\n"
        ser.write(message.encode())
        await asyncio.sleep(CMD_DELAY)
        logger.debug(f"Sent USB JSON: {message.strip()}")
        return True
    except Exception as e:
        logger.error(f"USB write failed: {e}")
        return False


async def run_usb_session(port: str):
    logger.info(f"Connecting via USB Serial on {port}")

    try:
        ser = serial.Serial(port, USB_BAUD, timeout=0.1)
    except Exception as e:
        logger.error(f"Failed to open USB port {port}: {e}")
        return

    logger.info("Connected via USB Serial")
    set_active_usb_serial(ser)

    buffer = ""

    try:
        while ser.is_open:
            if ser.in_waiting:
                chunk = ser.read(ser.in_waiting).decode(errors="ignore")
                buffer += chunk

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()

                    if not line:
                        continue

                    logger.info(f"USB device says: {line}")
                    await handle_incoming_message("usb", ser, line)

            await asyncio.sleep(0.1)

    except Exception as e:
        logger.error(f"USB session error: {e}")
    finally:
        clear_device_transports_for("usb", ser)
        clear_active_usb_serial()
        if ser.is_open:
            ser.close()
        logger.info("USB session ended")


async def run_usb() -> bool:
    logger.info("Falling back to USB Serial...")
    port = USB_PORT or find_arduino_port()

    if not port:
        logger.warning("No Arduino found on USB either")
        return False

    await run_usb_session(port)
    return True
