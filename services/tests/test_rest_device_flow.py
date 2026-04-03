import asyncio

from services.src.schemas.device_schema import CommandPayload
from services.src.services import device_service

def test_post_command_for_rest_device_queues_command(monkeypatch):
    # This test tests the flow of:
    # 1. The service receives a command for a device that uses REST transport.
    # 2. The service looks up the device and sees it uses REST.
    # 3. The service queues the command instead of sending it to the bridge.
    queued = {}

    def fake_get_device(device_uuid):
        # Fake the device lookup so the test does not depend on Firebase.
        # Returning a REST transport should make the service choose the queue path.
        return {
            "device_uuid": device_uuid,
            "transport": {
                "mode": "rest"
            }
        }
    
    def fake_enqueue_command(device_uuid, payload):
        # Fake the queue write by saving the values locally,
        # so the test can verify what would have been queued.
        queued["device_uuid"] = device_uuid
        queued["payload"] = payload

    # Replace the real store functions with fake ones to isolate service logic.
    monkeypatch.setattr(device_service.device_store, "get_device", fake_get_device)
    monkeypatch.setattr(device_service.device_store, "enqueue_command", fake_enqueue_command)

    payload = CommandPayload(state={"power": "on"})

    # post_command is async, so the test needs to run it with asyncio.
    result = asyncio.run(device_service.post_command("DEVICE_01", payload))

    # Verify the response returned from the service.
    assert result["message"] == "Command dispatched"
    assert result["device_uuid"] == "DEVICE_01"
    assert result["sent"] is True
    assert result["delivery"] == "queued"

    # Verify the command payload that was "queued" for the device.
    assert queued["device_uuid"] == "DEVICE_01"
    assert queued["payload"] == {
        "type": "COMMAND",
        "device_uuid": "DEVICE_01",
        "state": {"power": "on"},
    }
