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
            "device_uuid": self.rvc.device_id,
            "type": "robot_vacuum",
            "transport": {
                "mode": "simulated",
                "protocol": "python_local"
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
                "battery_level": {
                    "type": "integer",
                    "min": 0,
                    "max": 100,
                    "writable": False
                },
                "position_x": {
                    "type": "integer",
                    "writable": False
                },
                "position_y": {
                    "type": "integer",
                    "writable": False
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

    def build_initial_connect_message(self) -> dict:
        return {
            "type": "CONNECT",
            "devices": {
                self.rvc.device_id: self.build_device_entry()
            }
        }
    
    def build_connect_message(self) -> dict:
        return {
            "type": "CONNECT",
            "devices": {
                self.rvc.name: {
                    "device_uuid": self.rvc.device_id,
                    "status": {
                        "connected": True
                    },
                    "state": self.rvc.get_reported_state(),
                    "last_seen": self._timestamp()
                }
            }
        }

    def build_heartbeat_message(self) -> dict:
        return {
            "type": "HEARTBEAT",
            "device_uuid": self.rvc.device_id
        }

    def build_command_ack(self, status: str = "ok", error: str | None = None) -> dict:
        payload = {
            "type": "COMMAND_ACK",
            "device_uuid": self.rvc.device_id,
            "status": status,
            "reported_state": self.rvc.get_reported_state()
        }

        if error:
            payload["error"] = error

        return payload

    def apply_command(self, payload: dict) -> dict:
        """
        Accepts a COMMAND message and applies it's state to the local RVC.
        Returns a COMMAND_ACK payload.
        """
        if payload.get("type") != "COMMAND":
            return self.build_command_ack(status="error", error="Invalid message type")

        if payload.get("device_uuid") != self.rvc.device_id:
            return self.build_command_ack(status="error", error="Wrong device_uuid")

        state = payload.get("state", {})

        try:
            self._apply_state(state)
            return self.build_command_ack(status="ok")
        except Exception as e:
            return self.build_command_ack(status="error", error=str(e))

    def _apply_state(self, state: dict):
        # Dock command gets highest priority
        if state.get("return_to_base") is True:
            self.rvc.dock()
            return

        if "paused" in state:
            if state["paused"] is True:
                self.rvc.pause()
            elif state["paused"] is False and self.rvc.status == "paused":
                self.rvc.resume()

        if "cleaning" in state:
            if state["cleaning"] is True:
                self.rvc.start()
            elif state["cleaning"] is False:
                self.rvc.stop()