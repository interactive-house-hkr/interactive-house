from pydantic import BaseModel

class MessageSchema(BaseModel):
  device_uuid: str
  command: str
  payload: dict | None = None # Extra info, such as Brightness. Not mandatory.

  # TODO: Specify payload limits (Valid ranges)