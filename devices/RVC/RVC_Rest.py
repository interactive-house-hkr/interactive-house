import requests
from datetime import datetime, timezone
from rvc_protocol_adapter import RVCProtocolAdapter

# TODO:
# - Implement the rest of the REST API methods (essential)
# - Implement error handling for failed REST requests. (essential)
# - Add support for authentication if required by the API.

class RVCRest:
    def __init__(self, rvc, base_url):
        self.rvc = rvc
        self.base_url = base_url
        self.adapter = RVCProtocolAdapter(self.rvc)
        self.session = requests.Session()

    def initial_connect(self):
        try:
            url = f"{self.base_url}/connect"
            payload = {
                self.adapter.build_connect_message()
            }
            response = self.session.post(url, json=payload)
            return response.json()
        except Exception as e:
            print(f"Error during initial connection attempt: {e}")
            return None
        
    def connect(self):
        try:
            url = f"{self.base_url}/connect"
            payload = self.adapter.build_connect_message()
            response = self.session.post(url, json=payload)
            return response.json()
        except Exception as e:
            print(f"Error during connection attempt: {e}")
            return None
        
    def heartbeat(self):
        try:
            url = f"{self.base_url}/{self.rvc.device_id}/heartbeat"
            payload = self.adapter.build_heartbeat_message()
            response = self.session.post(url, json=payload)
            return response.json()
        except Exception as e:
            print(f"Error during heartbeat attempt: {e}")
            return None