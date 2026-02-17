from pydantic import BaseModel

class StateSchema(BaseModel):
  device_uuid: str
  values: dict