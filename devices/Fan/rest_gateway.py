import requests


class FanRestAdapter:
    def __init__(self, fan, device_id="FAN001", base_url="http://localhost:8000/api/v1/device-gateway"):
        self.fan = fan
        self.device_id = device_id
        self.base_url = base_url

    def connect(self):
        payload = {
            "devices": {
                self.device_id: {
                    "device_uuid": self.device_id,
                    "type": "fan",
                    "transport": {"mode": "rest", "protocol": "rest"},
                    "capabilities": {
                        "power": {"type": "boolean", "writable": True},
                        "speed_up": {"type": "boolean", "writable": True},
                        "speed_down": {"type": "boolean", "writable": True},
                        "mode_next": {"type": "boolean", "writable": True},
                        "timer_next": {"type": "boolean", "writable": True},
                        "swing_toggle": {"type": "boolean", "writable": True}
                    },
                    "state": self.fan.get_status(),
                    "status": {"connected": True}
                }
            }
        }

        r = requests.post(f"{self.base_url}/connect", json=payload)
        print("Fan connect:", r.status_code, r.text)

    def send_heartbeat(self):
        r = requests.post(f"{self.base_url}/{self.device_id}/heartbeat")
        print("Fan heartbeat:", r.status_code)

    def poll_next_command(self):
        r = requests.get(f"{self.base_url}/{self.device_id}/commands/next")
        return r.json().get("command")

    def apply_command(self, command):
        requested_state = command.get("state", {})
        new_state = self.fan.apply_state(requested_state)

        return {
            "status": "ok",
            "reported_state": new_state
        }

    def send_command_ack(self, ack):
        r = requests.post(
            f"{self.base_url}/{self.device_id}/command-ack",
            json=ack
        )
        print("Fan ACK:", r.status_code)