from datetime import datetime
from pydantic import BaseModel, Field


class DeviceSchema(BaseModel):
    device_uuid: str
    device_type: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    last_seen: datetime | None = None


class RegisterDeviceBody(BaseModel):
    device_type: str | None = None
    capabilities: list[str] = Field(default_factory=list)
