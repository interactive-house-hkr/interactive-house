import asyncio

from services.src.utils.logger import get_logger
from services.src.bridge.ble_controller import run_ble
from services.src.bridge.usb_controller import run_usb
from services.src.config.bridge_config import RECONNECT_DELAY

logger = get_logger("bridge")


async def run_bridge():
    """
    Run the bridge communication loop.
    This function is called as a background task by FastAPI.
    It continuously attempts to connect to devices via BLE and USB.
    """
    logger.info("Bridge started - scanning for devices via BLE and USB")
    
    while True:
        try:
            # Try BLE first
            ble_connected = await run_ble()

            if not ble_connected:
                # Fall back to USB
                await run_usb()

            logger.info(f"Retrying device connection in {RECONNECT_DELAY} seconds")
            await asyncio.sleep(RECONNECT_DELAY)
        except Exception as e:
            logger.error(f"Bridge error: {e}")
            await asyncio.sleep(RECONNECT_DELAY)


if __name__ == "__main__":
    # Standalone execution (for testing)
    asyncio.run(run_bridge())