from pydantic import BaseModel

class DeviceSchema(BaseModel):
  deviceUuid: str
  device_type: str
  capabilities: list[str]