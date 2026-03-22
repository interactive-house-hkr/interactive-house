import asyncio

from services.src.utils.logger import get_logger
from services.src.bridge.ble_controller import run_ble, send_ble_json
from services.src.bridge.usb_controller import run_usb, send_usb_json
from services.src.bridge.bridge_state import (
    get_active_ble_client,
    get_active_usb_serial,
)
from services.src.config.bridge_config import RECONNECT_DELAY


logger = get_logger("bridge")


async def run_bridge():
    """Run the bridge communication loop."""
    logger.info("Bridge started - scanning for devices via BLE and USB")
    
    # Start command sender as concurrent task
    
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


async def dispatch_command(payload: dict) -> bool:
    """Send a command payload through the active BLE transport, or USB as fallback."""
    ble_client = get_active_ble_client()
    if ble_client is not None:
        return await send_ble_json(ble_client, payload)
    
    usb_serial = get_active_usb_serial()
    if usb_serial is not None:
        return await send_usb_json(usb_serial, payload)
    
    logger.warning("No active BLE or USB transport available for command dispatch")
    return False


if __name__ == "__main__":
    # Standalone execution (for testing)
    asyncio.run(run_bridge())
