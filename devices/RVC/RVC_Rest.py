import requests
import rvc_protocol_adapter as protocol
import os
import json

"""
This file implements the REST adapter for the RVC robotic vacuum cleaner.
It translates between the internal RVC simulation and the JSON protocol used by the project.
The RVCRestAdapter class handles the REST communication, including device registration, heartbeat messages, and command processing.
"""

class RVCRestAdapter:
    def __init__(self, rvc, base_url):
        self.rvc = rvc
        self.base_url = base_url
        self.session = requests.Session()
        self.protocol = protocol.RVCProtocolAdapter(rvc)
        self.is_registered = self._load_registration_status()

    def _load_registration_status(self):
        config_file = "cfg.json"

        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                data = json.load(f)
                return data.get("is_registered", False)
            
        return False

    def _save_registration_status(self):
        config_file = "cfg.json"
        with open(config_file, "w") as f:
            json.dump({"is_registered": self.is_registered}, f)

    def connect(self):
        try:
            url = f"{self.base_url}/connect"

            if not self.is_registered:
                payload = self.protocol.build_device_entry()
            else:
                payload = self.protocol.build_connect_message()

            response = self.session.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                self.is_registered = True
                self._save_registration_status()

            return response.status_code, response.json()

        except Exception as e:
            print(f"Error during connect: {e}")
            return None, None
        

    def heartbeat(self):
        try:
            url = f"{self.base_url}/{self.rvc.device_id}/heartbeat"
            response = self.session.post(url, timeout=5)
            return response.status_code, response.json()

        except Exception as e:
            print(f"Error sending heartbeat: {e}")
            return None, None
        

    def apply_command(self, command_payload: dict):
        if command_payload.get("type") != "COMMAND":
            return self.protocol.build_command_ack(status="error", error="Invalid message type")
        
        if command_payload.get("device_uuid") != self.rvc.device_id:
            return self.protocol.build_command_ack(status="error", error="Wrong device_uuid")

        state = command_payload.get("state", {})

        try:
            self._apply_state(state)
            return self.protocol.build_command_ack(status="ok")
        except Exception as e:
            return self.protocol.build_command_ack(status="error", error=str(e))


    def ack_command(self, payload: dict):
        try:
            url = f"{self.base_url}/{self.rvc.device_id}/command-ack"
            response = self.session.post(url, json=payload, timeout=5)
            return response.status_code, response.json()
         
        except Exception as e:
            print(f"Error sending command ack: {e}")
            return None, None
        
    def get_command(self):
        try:
            url = f"{self.base_url}/{self.rvc.device_id}/commands/next"
            response = self.session.get(url, timeout=5)

            if response.status_code == 200:
                return response.json().get("command")
            
            else:
                print(f"Error polling command: {response.status_code} - {response.text}")
                return None
            
        except Exception as e:
            print(f"Error polling command: {e}")
            return None
        

    def _apply_state(self, state: dict):
        #dock command gets highest priority
        if state.get("return_to_base") is True:
            self.rvc.dock()
            return

        #pause/resume logic
        if "paused" in state:
            if state["paused"] is True:
                self.rvc.pause()
            elif state["paused"] is False and self.rvc.status == "paused":
                self.rvc.resume()

        #cleaning on/off
        if "cleaning" in state:
            if state["cleaning"] is True:
                self.rvc.start()
            elif state["cleaning"] is False:
                self.rvc.stop()
