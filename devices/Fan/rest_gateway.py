import time
import requests
from fan_controller import FanController

SERVER_URL = "http://localhost:8000"  # ändra om behövs
DEVICE_UUID = "FAN001"

fan = FanController()


def connect_device():
    payload = {
        "devices": {
            DEVICE_UUID: {
                "device_uuid": DEVICE_UUID,
                "type": "fan",
                "transport": {
                    "mode": "rest",
                    "protocol": "rest"
                },
                "capabilities": {
                    "power": {"type": "boolean", "writable": True},
                    "speed_up": {"type": "boolean", "writable": True},
                    "speed_down": {"type": "boolean", "writable": True},
                    "mode_next": {"type": "boolean", "writable": True},
                    "timer_next": {"type": "boolean", "writable": True},
                    "swing_toggle": {"type": "boolean", "writable": True}
                },
                "state": fan.get_status(),
                "status": {
                    "connected": True
                }
            }
        }
    }

    r = requests.post(
        f"{SERVER_URL}/api/v1/device-gateway/connect",
        json=payload
    )
    print("Connect:", r.status_code, r.text)


def heartbeat():
    try:
        r = requests.post(
            f"{SERVER_URL}/api/v1/device-gateway/{DEVICE_UUID}/heartbeat"
        )
        print("Heartbeat:", r.status_code)
    except Exception as e:
        print("Heartbeat error:", e)


def get_command():
    try:
        r = requests.get(
            f"{SERVER_URL}/api/v1/device-gateway/{DEVICE_UUID}/commands/next"
        )
        data = r.json()
        return data.get("command")
    except Exception as e:
        print("Command fetch error:", e)
        return None


def ack_command(state):
    payload = {
        "status": "ok",
        "reported_state": state
    }

    r = requests.post(
        f"{SERVER_URL}/api/v1/device-gateway/{DEVICE_UUID}/command-ack",
        json=payload
    )
    print("ACK:", r.status_code)


def main():
    print("Starting REST Gateway...")

    connect_device()

    last_heartbeat = 0

    while True:
        now = time.time()

        # 🔁 heartbeat var 5 sek
        if now - last_heartbeat >= 5:
            heartbeat()
            last_heartbeat = now

        # 🔁 hämta command
        command = get_command()

        if command:
            print("Received command:", command)

            requested_state = command.get("state", {})

            new_state = fan.apply_state(requested_state)

            ack_command(new_state)

        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    finally:
        fan.close()