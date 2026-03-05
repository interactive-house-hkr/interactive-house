import asyncio
import firebase_admin
from firebase_admin import credentials, db
from bleak import BleakClient, BleakScanner

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://se-prototyp-default-rtdb.europe-west1.firebasedatabase.app'
})
ref = db.reference('smarthouse')

HM10_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"


def handle_data(sender, data):
    message = data.decode().strip()
    print(f"Arduino: {message}")
    if '{"event":"DOORBELL"}' in message:
        ref.update({'doorbell': True})
    elif '{"event":"FAN_ON"}' in message:
        ref.update({'fan': True})
    elif '{"event":"FAN_OFF"}' in message:
        ref.update({'fan': False})


async def main():
    print("Scanning for HMSoft...")
    devices = await BleakScanner.discover()
    hm10 = None
    for d in devices:
        if d.name == "HMSoft":
            hm10 = d
            break

    if not hm10:
        print("HMSoft not found. Make sure it's powered on.")
        return

    print(f"Found HMSoft at {hm10.address}")

    async with BleakClient(hm10.address) as client:
        print("Connected to HM-10")

        await client.start_notify(HM10_UUID, handle_data)

        last_state = {}
        while True:
            data = ref.get()
            print(f"Firebase data: {data}")
            if data:
                if data.get('lights') != last_state.get('lights'):
                    cmd = 'LIGHTS_ON' if data['lights'] else 'LIGHTS_OFF'
                    print(f"Sending: {cmd}")

                    await client.write_gatt_char(
                        HM10_UUID,
                        (cmd + "\n").encode(),   # important
                        response=True            # important
                    )
                    last_state['lights'] = data['lights']

                if data.get('door') != last_state.get('door'):
                    cmd = 'DOOR_OPEN' if data['door'] == 'open' else 'DOOR_CLOSE'
                    print(f"Sending: {cmd}")

                    await client.write_gatt_char(
                        HM10_UUID,
                        (cmd + "\n").encode(),   # important
                        response=True            # important
                    )
                    last_state['door'] = data['door']

            await asyncio.sleep(1)

asyncio.run(main())
