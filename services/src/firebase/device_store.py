from __future__ import annotations
from typing import Any

# Enkel in-memory store (placeholder tills Firebase kopplas på riktigt)
_DEVICES: dict[str, dict[str, Any]] = {}


def list_devices() -> list[dict[str, Any]]:
    return list(_DEVICES.values())


def get_device(device_uuid: str) -> dict[str, Any] | None:
    return _DEVICES.get(device_uuid)


def register_device(device_uuid: str, data: dict[str, Any]) -> dict[str, Any]:
    # sparar/uppdaterar device
    payload = {"device_uuid": device_uuid, **data}
    _DEVICES[device_uuid] = payload
    return payload
