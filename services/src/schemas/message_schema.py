from pydantic import BaseModel

class MessageSchema(BaseModel):
  deviceUuid: str
  command: str
  payload: dict | None = None # Extra info, such as Brightness. Not mandatory.

  # TODO: Specify payload limits (Valid ranges)