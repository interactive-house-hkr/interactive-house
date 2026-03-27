import asyncio

from services.src.utils.logger import get_logger
from services.src.bridge.ble_controller import run_ble, send_ble_json
from services.src.bridge.usb_controller import run_usb, send_usb_json
from services.src.bridge.bridge_state import (
    get_active_ble_client,
    get_device_transport,
    get_active_usb_serial,
)
from services.src.config.bridge_config import RECONNECT_DELAY

logger = get_logger("bridge")


async def run_bridge():
    logger.info("Bridge started - trying BLE first, then USB fallback")

    while True:
        try:
            ble_connected = await run_ble()
            if not ble_connected:
                await run_usb()
            logger.info(f"Retrying device connection in {RECONNECT_DELAY} seconds")
            await asyncio.sleep(RECONNECT_DELAY)
        except Exception as e:
            logger.error(f"Bridge error: {e}")
            await asyncio.sleep(RECONNECT_DELAY)


async def dispatch_command(device_uuid: str, payload: dict) -> bool:
    binding = get_device_transport(device_uuid)
    if binding is not None:
        transport_type = binding["transport_type"]
        transport = binding["transport"]

        if transport_type == "ble":
            return await send_ble_json(transport, payload)

        if transport_type == "usb":
            return await send_usb_json(transport, payload)

        logger.warning(f"Unsupported transport type '{transport_type}' for device {device_uuid}")
        return False

    ble_client = get_active_ble_client()
    usb_serial = get_active_usb_serial()
    logger.warning(
        "No registered transport for device %s. Active BLE=%s, active USB=%s",
        device_uuid,
        ble_client is not None,
        usb_serial is not None,
    )
    return False


if __name__ == "__main__":
    asyncio.run(run_bridge())
