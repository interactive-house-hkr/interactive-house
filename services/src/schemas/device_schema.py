from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class DeviceSchema(BaseModel):
    device_uuid: str | None = None
    type: str | None = None
    transport: Dict[str, Any] = Field(default_factory=dict)
    capabilities: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    state: Dict[str, Any] = Field(default_factory=dict)
    status: Dict[str, Any] = Field(default_factory=dict)
    last_seen: datetime | None = None


class ConnectDeviceBody(BaseModel):
    devices: Dict[str, DeviceSchema] = Field(default_factory=dict)


class CommandPayload(BaseModel):
    state: Dict[str, Any]
