import asyncio
import json
import threading
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
from bleak import BleakClient, BleakScanner
import serial
import serial.tools.list_ports

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://se-prototyp-default-rtdb.europe-west1.firebasedatabase.app'
})
ref = db.reference('smarthouse')
modules_ref = ref.child('modules')

HM10_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
CMD_DELAY = 0.15

# Backup connection incase bluetooth fails during Demo
USB_PORT = 'COM5'
USB_BAUD = 9600


def now():
    return datetime.now().isoformat()


def on_disconnect(client):
    ts = now()
    print("Arduino BLE disconnected — updating Firebase")
    modules_ref.child('arduino').update({'connected': False, 'last_seen': ts})
    for module in ['lights', 'fan', 'door', 'window', 'doorbell']:
        modules_ref.child(module).update({'state': 'unknown', 'last_updated': ts})


def handle_data(sender, data):
    message = data.decode().strip()
    print(f"Arduino: {message}")
    if '{"event":"DOORBELL"}' in message:
        ref.update({'doorbell': True})
        modules_ref.child('doorbell').update({'state': 'ringing', 'last_updated': now()})
    elif '"type":"STATUS"' in message:
        try:
            status = json.loads(message)
            ts = now()
            speed = status.get('fan_speed', 0)
            modules_ref.child('lights').update({'state': 'on' if status['lights'] else 'off', 'last_updated': ts})
            modules_ref.child('fan').update({'speed': speed, 'state': 'on' if speed > 0 else 'off', 'last_updated': ts})
            modules_ref.child('door').update({'state': status['door'], 'last_updated': ts})
            modules_ref.child('window').update({'state': status['window'], 'last_updated': ts})
            modules_ref.child('arduino').update({'connected': True, 'last_seen': ts})
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
        print(f"BLE write failed ({cmd}): {e}")
        return False

# Bluetooth connection
async def run_ble_session(client):
    print("Connected via Bluetooth (HM-10)")
    modules_ref.child('arduino').update({'connected': True, 'last_seen': now()})
    await client.start_notify(HM10_UUID, handle_data)

    last_state = {}
    while client.is_connected:
        data = ref.get()
        if data:
            if data.get('lights') != last_state.get('lights'):
                cmd = 'LIGHTS_ON' if data['lights'] else 'LIGHTS_OFF'
                print(f"Sending: {cmd}")
                if not await send_ble_cmd(client, cmd):
                    break
                last_state['lights'] = data['lights']

            if data.get('door') != last_state.get('door'):
                cmd = 'DOOR_OPEN' if data['door'] == 'open' else 'DOOR_CLOSE'
                print(f"Sending: {cmd}")
                if not await send_ble_cmd(client, cmd):
                    break
                last_state['door'] = data['door']

            if data.get('window') != last_state.get('window'):
                cmd = 'WINDOW_OPEN' if data['window'] == 'open' else 'WINDOW_CLOSE'
                print(f"Sending: {cmd}")
                if not await send_ble_cmd(client, cmd):
                    break
                last_state['window'] = data['window']

            if data.get('fan_speed') != last_state.get('fan_speed'):
                speed = data.get('fan_speed', 0)
                cmd = f'FAN_SPEED:{speed}'
                print(f"Sending: {cmd}")
                if not await send_ble_cmd(client, cmd):
                    break
                last_state['fan_speed'] = speed
                modules_ref.child('fan').update({'speed': speed, 'state': 'on' if speed > 0 else 'off', 'last_updated': now()})

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
    modules_ref.child('arduino').update({'connected': True, 'last_seen': now()})

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



async def main():
    while True:
        # Try Bluetooth first
        print("Scanning for HMSoft (Bluetooth)...")
        devices = await BleakScanner.discover()
        hm10 = next((d for d in devices if d.name == "HMSoft"), None)

        if hm10:
            print(f"Found HMSoft at {hm10.address}")
            try:
                async with BleakClient(hm10.address, disconnected_callback=on_disconnect) as client:
                    await run_ble_session(client)
            except Exception as e:
                print(f"BLE error: {e}")
        else:
            print("HMSoft not found - falling back to USB Serial.")
            port = USB_PORT or find_arduino_port()
            if port:
                await run_usb_session(port)
            else:
                print("No Arduino found on USB either.")
                print("Plug in the USB cable, or check that the COM port is correct.")
                print("Set USB_PORT manually at the top of bridge.py (e.g. 'COM5') so that it matches the port from Device Manager")

        print("Retrying in 5 seconds.\n")
        await asyncio.sleep(5)


asyncio.run(main())
