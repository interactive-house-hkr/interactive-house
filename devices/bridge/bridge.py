import asyncio
import json
import requests
from bleak import BleakClient, BleakScanner

HM10_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
# Need to fill in Server Url below
SERVER_URL = ""
# ----- From Arduino to Server -----


def handle_data(sender, data):
    try:
        message = data.decode().strip()
        print("From Arduino:", message)

        # validate JSON before sending
        json.loads(message)

        requests.post(f"{SERVER_URL}/device", json=json.loads(message))

    except Exception as e:
        print("Error handling data:", e)


async def main():
    print("Scanning for HMSoft...")
    devices = await BleakScanner.discover()

    hm10 = next((d for d in devices if d.name == "HMSoft"), None)

    if not hm10:
        print("HMSoft not found")
        return

    print(f"Connecting to {hm10.address}")

    async with BleakClient(hm10.address) as client:
        print("Connected")

        await client.start_notify(HM10_UUID, handle_data)

        while True:
            try:
                # ---- GET COMMANDS FROM SERVER ----
                response = requests.get(f"{SERVER_URL}/commands")

                if response.status_code == 200:
                    commands = response.json()

                    for cmd in commands:
                        # Ensure it's valid JSON
                        msg = json.dumps(cmd)

                        print("Sending:", msg)

                        # Send the full message and not bytes
                        await client.write_gatt_char(
                            HM10_UUID,
                            (msg + "\n").encode(),
                            response=True
                        )
                        # Small delay to ensure HM10 processes the command
                        await asyncio.sleep(0.1)

            except Exception as e:
                print("Server error:", e)

            await asyncio.sleep(1)


asyncio.run(main())
