from pydantic import BaseModel

class StateSchema(BaseModel):
  deviceUuid: str
  values: dict