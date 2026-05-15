import time
import requests
from Fan.fan_controller import FanController

DEVICE_UUID = "FAN001"

class FanRestAdapter:
    def __init__(self, fan, base_url):
        self.fan = fan
        self.base_url = base_url

    def connect_device(self):
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
                    "state": self.fan.get_status(),
                    "status": {
                        "connected": True
                    }
                }
            }
        }

        r = requests.post(
            f"{self.base_url}/connect",
            json=payload
        )
        print("Connect:", r.status_code, r.text)


    def heartbeat(self):
        try:
            r = requests.post(
                f"{self.base_url}/{DEVICE_UUID}/heartbeat"
            )
            print("Heartbeat:", r.status_code)
        except Exception as e:
            print("Heartbeat error:", e)


    def get_command(self):
        try:
            r = requests.get(
                f"{self.base_url}/{DEVICE_UUID}/commands/next"
            )
            data = r.json()
            return data.get("command")
        except Exception as e:
            print("Command fetch error:", e)
            return None


    def ack_command(self, state):
        payload = {
            "status": "ok",
            "reported_state": state
        }

        r = requests.post(
            f"{self.base_url}/{DEVICE_UUID}/command-ack",
            json=payload
        )
        print("ACK:", r.status_code)

    def apply_command(self, command_payload):
        if command_payload.get("type") != "COMMAND":
            return {"status": "error", "error": "Invalid message type"}
        
        if command_payload.get("device_uuid") != DEVICE_UUID:
            return {"status": "error", "error": "Wrong device_uuid"}

        state = command_payload.get("state", {})

        try:
            new_state = self.fan.apply_state(state)
            return {"status": "ok", "reported_state": new_state}
        except Exception as e:
            return {"status": "error", "error": str(e)}


    def main(self):
        print("Starting REST Gateway...")

        self.connect_device()

        last_heartbeat = 0

        while True:
            now = time.time()

            # 🔁 heartbeat var 5 sek
            if now - last_heartbeat >= 5:
                self.heartbeat()
                last_heartbeat = now

            # 🔁 hämta command
            command = self.get_command()

            if command:
                print("Received command:", command)

                requested_state = command.get("state", {})

                new_state = self.fan.apply_state(requested_state)

                self.ack_command(new_state)

            time.sleep(1)


if __name__ == "__main__":
    fan = FanController()
    rest_adapter = FanRestAdapter(fan, base_url="http://localhost:8000/api/v1/device-gateway")
    rest_adapter.main()

