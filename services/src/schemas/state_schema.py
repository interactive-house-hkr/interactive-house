from pydantic import BaseModel

class StateSchema(BaseModel):
  device_id: str
  values: dict