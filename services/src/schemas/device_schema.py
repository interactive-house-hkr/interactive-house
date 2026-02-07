from pydantic import BaseModel

class DeviceSchema(BaseModel):
  device_id: str
  device_type: str
  capabilities: list[str]