from datetime import datetime, timezone


class RVCProtocolAdapter:
    """
    Bridges the local RVC simulation to the JSON protocol used by the project.
    This class does not handle BLE/USB transport.
    It only builds/parses protocol messages for the robot vacuum.
    """

    def __init__(self, rvc):
        self.rvc = rvc

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def build_device_entry(self) -> dict:
        return {
            "devices": {
                self.rvc.name: {
                    "device_uuid": self.rvc.device_id,
                    "type": "robot_vacuum",
                    "transport": {
                        "mode": "rest",
                        "protocol": "rest"
                    },
                    "capabilities": {
                        "cleaning": {
                            "type": "boolean",
                            "writable": True
                        },
                        "paused": {
                            "type": "boolean",
                            "writable": True
                        },
                        "return_to_base": {
                            "type": "boolean",
                            "writable": True
                        },
                        "docked": {
                            "type": "boolean",
                            "writable": False
                        }
                    },
                    "state": self.rvc.get_reported_state(),
                    "status": {
                        "connected": True
                    },
                    "last_seen": self._timestamp()
                }
            }
        }

    def build_connect_message(self) -> dict:
        return {
                "devices": {
                    self.rvc.name: {
                        "device_uuid": self.rvc.device_id,
                        "status": {
                            "connected": True
                        },
                        "last_seen": self._timestamp()
                    },
                }
            }

    def build_command_ack(self, status: str = "ok", error: str | None = None) -> dict:
        payload = {
            "status": status,
            "reported_state": self.rvc.get_reported_state()
        }

        if error:
            payload["error"] = error

        return payload
