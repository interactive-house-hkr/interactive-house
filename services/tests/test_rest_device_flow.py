import asyncio

from services.src.schemas.device_schema import CommandPayload
from services.src.services import device_service

def test_post_command_for_rest_device_queues_command(monkeypatch):
    queued = {}

    def fake_get_device(device_uuid):
        return {
            "device_uuid": device_uuid,
            "transport": {
                "mode": "rest"
            }
        }
    
    def fake_enqueue_command(device_uuid, payload):
        queued["device_uuid"] = device_uuid
        queued["payload"] = payload

    monkeypatch.setattr(device_service.device_store, "get_device", fake_get_device)
    monkeypatch.setattr(device_service.device_store, "enqueue_command", fake_enqueue_command)

    payload = CommandPayload(state={"power": "on"})

    result = asyncio.run(device_service.post_command("DEVICE_01", payload))

    assert result["message"] == "Command dispatched"
    assert result["device_uuid"] == "DEVICE_01"
    assert result["sent"] is True
    assert result["delivery"] == "queued"

    assert queued["device_uuid"] == "DEVICE_01"
    assert queued["payload"] == {
        "type": "COMMAND",
        "device_uuid": "DEVICE_01",
        "state": {"power": "on"},
    }