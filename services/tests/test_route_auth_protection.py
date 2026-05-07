import pytest
from fastapi.testclient import TestClient

from services.src.main import app
from services.src.controllers import device_controller, state_controller # Controllers are mocked

# These tests check that the device and state routes actually require auth.
# The controllers are mocked because this file is only about route protection.

@pytest.fixture
def client():
    return TestClient(app)

@pytest.mark.parametrize("method,path,json_body", [
    ("GET", "/api/v1/devices", None), 
    ("GET", "/api/v1/devices/DEVICE_01", None), 
    ("DELETE", "/api/v1/devices/DEVICE_01", None), 
    ("POST", "/api/v1/devices/DEVICE_01/commands", {"state": {"power": "on"}}),
    ("GET", "/api/v1/devices/DEVICE_01/state", None),
    ("PATCH", "/api/v1/devices/DEVICE_01/state", {"state": {"power": "on"}}),
])
def test_protected_routes_reject_invalid_token(client, monkeypatch, method, path, json_body):

    monkeypatch.setattr(device_controller, "list_devices", lambda type=None: {"ok": True})
    monkeypatch.setattr(device_controller, "get_device", lambda device_uuid: {"ok": True})
    monkeypatch.setattr(device_controller, "delete_device", lambda device_uuid: {"ok": True})

    async def fake_post_command(device_uuid, payload):
        return {"ok": True}
    
    monkeypatch.setattr(device_controller, "post_command", fake_post_command)

    monkeypatch.setattr(state_controller, "get_state", lambda device_uuid: {"ok": True})
    monkeypatch.setattr(state_controller, "patch_state", lambda device_uuid, updates: {"ok": True})

    response = client.request(
        method,
        path,
        json=json_body,
        headers={"Authorization": "Bearer invalid-token"},
    )

    # All protected routes should return '401 Unauthorized' for an invalid token.
    assert response.status_code == 401
