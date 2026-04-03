import asyncio
import json
import os

from bleak import BleakClient, BleakScanner

from services.src.utils.logger import get_logger
from services.src.bridge.bridge_message_handler import handle_incoming_message
from services.src.bridge.bridge_state import (
    set_active_ble_client,
    clear_active_ble_client,
)
from services.src.config.bridge_config import HM10_UUID, CMD_DELAY

logger = get_logger("ble_controller")

# HM-10 BLE address — set via env or update before test day
# To find your HM-10 address, run a BLE scan and look for "HMSoft"
HMSOFT_ADDRESS = os.getenv("HM10_ADDRESS", "")
# Match by address if set, otherwise fall back to name-based matching
ALLOWED_DEVICE_NAMES = {"HMSoft"}


def on_disconnect(client):
    logger.info("BLE device disconnected")


async def send_ble_json(client: BleakClient, payload: dict) -> bool:
    if not client.is_connected:
        logger.warning("Cannot send BLE JSON: client is not connected")
        return False

    try:
        message = json.dumps(payload) + "\n"
        await client.write_gatt_char(HM10_UUID, message.encode(), response=False)
        await asyncio.sleep(CMD_DELAY)
        logger.info(f"Sent BLE JSON: {message.strip()}")
        return True
    except Exception as e:
        logger.error(f"BLE write failed: {e}")
        return False


def make_notification_handler(client: BleakClient):
    buffer = ""

    def handle_data(sender, data):
        nonlocal buffer

        chunk = data.decode(errors="ignore")
        logger.info(f"Raw BLE chunk received: {chunk!r}")
        buffer += chunk

        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()

            if not line:
                continue

            logger.info(f"BLE device says: {line}")
            asyncio.create_task(handle_incoming_message("ble", client, line))

    return handle_data


async def run_ble_session(client: BleakClient):
    logger.info("Connected via Bluetooth")
    set_active_ble_client(client)

    handler = make_notification_handler(client)

    try:
        await client.start_notify(HM10_UUID, handler)
        # Wait for BLE notification to settle before sending PING
        await asyncio.sleep(3)
        # Send PING to trigger Arduino to send device data AFTER bridge is ready
        await send_ble_json(client, {"type": "PING"})
    except Exception as e:
        logger.warning(f"Failed to enable notifications on {HM10_UUID}: {e}")

    try:
        while client.is_connected:
            await asyncio.sleep(1)
    finally:
        clear_active_ble_client()
        logger.info("BLE session ended")


async def run_ble() -> bool:
    logger.info("Scanning for BLE devices...")
    devices = await BleakScanner.discover(timeout=5.0)

    if not devices:
        logger.warning("No BLE devices found")
        return False

    # Log all discovered devices for debugging
    for device in devices:
        logger.info(f"Found BLE device: name={device.name}, address={device.address}")

    # Match by address first (more reliable), then by name
    if HMSOFT_ADDRESS:
        candidates = [
            device for device in devices
            if (device.address or "").strip() == HMSOFT_ADDRESS
        ]
    else:
        candidates = [
            device for device in devices
            if (device.name or "").strip() in ALLOWED_DEVICE_NAMES
        ]

    if not candidates:
        logger.warning("No allowed BLE device found")
        return False

    target = candidates[0]

    logger.info(f"Connecting to {target.name} at {target.address}")

    try:
        async with BleakClient(target, disconnected_callback=on_disconnect) as client:
            await run_ble_session(client)
            return True
    except Exception as e:
        logger.error(f"BLE error: {e}")
        return False
