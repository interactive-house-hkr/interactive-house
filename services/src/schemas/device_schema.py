from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional



class DeviceSchema(BaseModel):
    device_uuid: str
    device_type: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    last_seen: datetime | None = None


class ConnectDeviceBody(BaseModel):
    device_uuid: Optional[str] = None
    device_type: Optional[str] = None
    transport: Dict[str, Any] = Field(default_factory=dict)
    capabilities: List[Dict[str, Any]] = Field(default_factory=list)
    desired_state: Dict[str, Any] = Field(default_factory=dict)
    reported_state: Dict[str, Any] = Field(default_factory=dict)
    status: Dict[str, Any] = Field(default_factory=dict)
