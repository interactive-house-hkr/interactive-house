import asyncio
import json
import threading
from datetime import datetime
from bleak import BleakClient, BleakScanner
import serial
import serial.tools.list_ports

from services.src.utils.logger import get_logger
from services.src.controllers import device_controller
from services.src.schemas.device_schema import ConnectDeviceBody

from services.src.config.bridge_config import (
    DEVICE_UUID,
    HM10_UUID,
    CMD_DELAY,
    USB_BAUD,
    USB_PORT,
    HEARTBEAT_INTERVAL,
    RECONNECT_DELAY,
)


logger = get_logger("bridge")


def now():
    return datetime.now().isoformat()


def on_disconnect(client):
    ts = now()
    logger.info("Arduino BLE disconnected — updating Firebase")
    # TODO: offline functionality
    #for module in ['lights', 'fan', 'door', 'window', 'doorbell']:
    #   modules_ref.child(module).update({'state': 'unknown', 'last_updated': ts})


def handle_data(sender, data):
    message = data.decode().strip()
    print(f"Arduino: {message}")
    if '{"event":"DOORBELL"}' in message:
        pass
        # TODO: Add doorbell status
    elif '"type":"STATUS"' in message:
        try:
            status = json.loads(message)
            ts = now()
            speed = status.get('fan_speed', 0)

        except Exception as e:
            print(f"Failed to parse STATUS: {e}")


def find_arduino_port():
    """Auto-detect Arduino USB port."""
    keywords = ['arduino', 'ch340', 'ch341', 'usb serial', 'usb-serial', 'usbserial']
    for port in serial.tools.list_ports.comports():
        desc = port.description.lower()
        if any(k in desc for k in keywords):
            return port.device
    return None


async def send_ble_cmd(client, cmd):
    if not client.is_connected:
        return False
    try:
        await client.write_gatt_char(HM10_UUID, (cmd + "\n").encode(), response=True)
        await asyncio.sleep(CMD_DELAY)
        return True
    except Exception as e:
        logger.error(f"BLE write failed ({cmd}): {e}")
        return False

# Bluetooth connection
"""
async def run_ble_session(client):
    logger.info("Connected via Bluetooth (HM-10)")
    # modules_ref.child('arduino').update({'connected': True, 'last_seen': now()})
    await client.start_notify(HM10_UUID, handle_data)

    last_state = {}
    while client.is_connected:
        data = ref.get()
        if data:
            if data.get('lights') != last_state.get('lights'):
                cmd = 'LIGHTS_ON' if data['lights'] else 'LIGHTS_OFF'
                logger.debug(f"Sending: {cmd}")
                if not await send_ble_cmd(client, cmd):
                    break
                last_state['lights'] = data['lights']

            if data.get('door') != last_state.get('door'):
                cmd = 'DOOR_OPEN' if data['door'] == 'open' else 'DOOR_CLOSE'
                logger.debug(f"Sending: {cmd}")
                if not await send_ble_cmd(client, cmd):
                    break
                last_state['door'] = data['door']

            if data.get('window') != last_state.get('window'):
                cmd = 'WINDOW_OPEN' if data['window'] == 'open' else 'WINDOW_CLOSE'
                logger.debug(f"Sending: {cmd}")
                if not await send_ble_cmd(client, cmd):
                    break
                last_state['window'] = data['window']

            if data.get('fan_speed') != last_state.get('fan_speed'):
                speed = data.get('fan_speed', 0)
                cmd = f'FAN_SPEED:{speed}'
                logger.debug(f"Sending: {cmd}")
                if not await send_ble_cmd(client, cmd):
                    break
                last_state['fan_speed'] = speed
                #modules_ref.child('fan').update({'speed': speed, 'state': 'on' if speed > 0 else 'off', 'last_updated': now()})

        await asyncio.sleep(1)
        
# USB session connection

async def run_usb_session(port):
    print(f"Connecting via USB Serial on {port}...")
    try:
        ser = serial.Serial(port, USB_BAUD, timeout=0.1)
    except Exception as e:
        print(f"Failed to open {port}: {e}")
        return

    print("Connected via USB Serial")
    #modules_ref.child('arduino').update({'connected': True, 'last_seen': now()})

    stop = threading.Event()

    def read_loop():
        while not stop.is_set():
            try:
                if ser.in_waiting:
                    line = ser.readline().decode(errors='ignore').strip()
                    if line:
                        handle_data(None, line.encode())
            except Exception:
                break

    reader = threading.Thread(target=read_loop, daemon=True)
    reader.start()

    last_state = {}
    try:
        while ser.is_open:
            data = ref.get()
            if data:
                if data.get('lights') != last_state.get('lights'):
                    cmd = 'LIGHTS_ON' if data['lights'] else 'LIGHTS_OFF'
                    print(f"Sending: {cmd}")
                    ser.write((cmd + "\n").encode())
                    await asyncio.sleep(CMD_DELAY)
                    last_state['lights'] = data['lights']

                if data.get('door') != last_state.get('door'):
                    cmd = 'DOOR_OPEN' if data['door'] == 'open' else 'DOOR_CLOSE'
                    print(f"Sending: {cmd}")
                    ser.write((cmd + "\n").encode())
                    await asyncio.sleep(CMD_DELAY)
                    last_state['door'] = data['door']

                if data.get('window') != last_state.get('window'):
                    cmd = 'WINDOW_OPEN' if data['window'] == 'open' else 'WINDOW_CLOSE'
                    print(f"Sending: {cmd}")
                    ser.write((cmd + "\n").encode())
                    await asyncio.sleep(CMD_DELAY)
                    last_state['window'] = data['window']

                if data.get('fan_speed') != last_state.get('fan_speed'):
                    speed = data.get('fan_speed', 0)
                    cmd = f'FAN_SPEED:{speed}'
                    print(f"Sending: {cmd}")
                    ser.write((cmd + "\n").encode())
                    await asyncio.sleep(CMD_DELAY)
                    last_state['fan_speed'] = speed
                    modules_ref.child('fan').update({'speed': speed, 'state': 'on' if speed > 0 else 'off', 'last_updated': now()})

            await asyncio.sleep(1)
    except Exception as e:
        print(f"USB session error: {e}")
    finally:
        stop.set()
        ser.close()
        modules_ref.child('arduino').update({'connected': False, 'last_seen': now()})
"""


async def main():
    while True:
        logger.info("Scanning for BLE devices...")
        devices = await BleakScanner.discover()

        if not devices:
            logger.warning("No BLE devices found")
            await asyncio.sleep(RECONNECT_DELAY)
            continue

        for d in devices:
            logger.info(f"Found BLE device: name={d.name}, address={d.address}")

        target = next((d for d in devices if d.name), None)

        if not target:
            logger.warning("No usable BLE device found")
            await asyncio.sleep(RECONNECT_DELAY)
            continue

        logger.info(f"Connecting to {target.name} at {target.address}")

        try:
            async with BleakClient(target.address, disconnected_callback=on_disconnect) as client:
                await run_ble_session(client)
        except Exception as e:
            logger.error(f"BLE error: {e}")

        logger.info(f"Retrying in {RECONNECT_DELAY} seconds")
        await asyncio.sleep(RECONNECT_DELAY)


if __name__ == "__main__":
    asyncio.run(main())
