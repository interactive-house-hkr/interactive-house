from pydantic import BaseModel, Field


class DeviceSchema(BaseModel):
    device_id: str
    device_type: str
    capabilities: list[str]


class RegisterDeviceBody(BaseModel):
    device_type: str | None = None
    capabilities: list[str] = Field(default_factory=list)
