import unittest
import json
import os
from unittest.mock import MagicMock, patch
from RVC_Rest import RVCRestAdapter

class TestRVCRestAdapter(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        # Mock RVC object
        self.mock_rvc = MagicMock()
        self.mock_rvc.device_id = "RVC001"
        self.mock_rvc.name = "RoboVac"
        self.mock_rvc.status = "idle"
        self.mock_rvc.get_reported_state.return_value = {
            "cleaning": False,
            "paused": False,
            "return_to_base": False,
            "battery_level": 100,
            "position_x": 0,
            "position_y": 0,
            "docked": True,
            "status_text": "idle"
        }

        # Mock RVCProtocolAdapter
        self.mock_protocol = MagicMock()
        self.mock_protocol.build_device_entry.return_value = {
            "devices": {
                "RoboVac": {
                    "device_uuid": "RVC001",
                    "type": "robot_vacuum",
                    "transport": {"mode": "rest", "protocol": "rest"},
                    "capabilities": {
                        "cleaning": {"type": "boolean", "writable": True},
                        "paused": {"type": "boolean", "writable": True},
                        "return_to_base": {"type": "boolean", "writable": True},
                        "docked": {"type": "boolean", "writable": False}
                    },
                    "state": self.mock_rvc.get_reported_state(),
                    "status": {"connected": True},
                    "last_seen": "2026-04-02T12:00:00Z"
                }
            }
        }
        self.mock_protocol.build_connect_message.return_value = {
            "devices": {
                "RoboVac": {
                    "device_uuid": "RVC001",
                    "status": {"connected": True},
                    "last_seen": "2026-04-02T12:00:00Z"
                }
            }
        }

        # Create RVCRestAdapter instance with mocked dependencies
        self.adapter = RVCRestAdapter(self.mock_rvc, "http://test/api/v1/device-gateway")
        self.adapter.session = MagicMock()
        self.adapter.protocol = self.mock_protocol

    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists("cfg.json"):
            os.remove("cfg.json")

    def test_load_registration_status_not_exists(self):
        """Test loading registration status when cfg.json does not exist."""
        self.assertFalse(self.adapter._load_registration_status())

    def test_load_registration_status_exists_false(self):
        """Test loading registration status when cfg.json exists with false."""
        with open("cfg.json", "w") as f:
            json.dump({"is_registered": False}, f)
        self.assertFalse(self.adapter._load_registration_status())

    def test_load_registration_status_exists_true(self):
        """Test loading registration status when cfg.json exists with true."""
        with open("cfg.json", "w") as f:
            json.dump({"is_registered": True}, f)
        self.assertTrue(self.adapter._load_registration_status())

    def test_save_registration_status(self):
        """Test saving registration status to cfg.json."""
        self.adapter.is_registered = True
        self.adapter._save_registration_status()
        self.assertTrue(os.path.exists("cfg.json"))
        with open("cfg.json", "r") as f:
            data = json.load(f)
        self.assertTrue(data["is_registered"])

    def test_connect_not_registered(self):
        """Test connect() when device is not registered."""
        self.adapter.session.post.return_value = MagicMock()
        self.adapter.session.post.return_value.status_code = 200
        self.adapter.session.post.return_value.json.return_value = {"message": "Devices connected"}

        self.adapter.is_registered = False
        status_code, response = self.adapter.connect()

        self.assertEqual(status_code, 200)
        self.assertEqual(response, {"message": "Devices connected"})
        self.assertTrue(self.adapter.is_registered)
        self.mock_protocol.build_device_entry.assert_called_once()

    def test_connect_registered(self):
        """Test connect() when device is already registered."""
        self.adapter.session.post.return_value = MagicMock()
        self.adapter.session.post.return_value.status_code = 200
        self.adapter.session.post.return_value.json.return_value = {"message": "Devices connected"}

        self.adapter.is_registered = True
        status_code, response = self.adapter.connect()

        self.assertEqual(status_code, 200)
        self.assertEqual(response, {"message": "Devices connected"})
        self.mock_protocol.build_connect_message.assert_called_once()

    def test_connect_exception(self):
        self.adapter.session.post.side_effect = Exception("Network error")

        status_code, response = self.adapter.connect()

        self.assertIsNone(status_code)
        self.assertIsNone(response)

    def test_send_heartbeat(self):
        """Test sending a heartbeat."""
        self.adapter.session.post.return_value = MagicMock()
        self.adapter.session.post.return_value.status_code = 200
        self.adapter.session.post.return_value.json.return_value = {"status": "ok"}

        status_code, response = self.adapter.heartbeat()

        self.assertEqual(status_code, 200)
        self.assertEqual(response, {"status": "ok"})

    def test_poll_next_command(self):
        """Test polling for the next command."""
        self.adapter.session.get.return_value = MagicMock()
        self.adapter.session.get.return_value.status_code = 200
        self.adapter.session.get.return_value.json.return_value = {
            "device_uuid": "RVC001",
            "command": {"type": "COMMAND", "device_uuid": "RVC001", "state": {"cleaning": True}}
        }

        command = self.adapter.get_command()

        self.assertEqual(command, {"type": "COMMAND", "device_uuid": "RVC001", "state": {"cleaning": True}})

    def test_poll_next_command_no_command(self):
        """Test polling for the next command when there is no command."""
        self.adapter.session.get.return_value = MagicMock()
        self.adapter.session.get.return_value.status_code = 200
        self.adapter.session.get.return_value.json.return_value = {
            "device_uuid": "RVC001",
            "command": None
        }

        command = self.adapter.get_command()

        self.assertIsNone(command)

    def test_apply_command_valid(self):
        """Test applying a valid command."""
        self.mock_protocol.build_command_ack.return_value = {
            "status": "ok",
            "reported_state": self.mock_rvc.get_reported_state()
        }

        command_payload = {
            "type": "COMMAND",
            "device_uuid": "RVC001",
            "state": {"cleaning": True}
        }

        ack = self.adapter.apply_command(command_payload)

        self.assertEqual(ack, {"status": "ok", "reported_state": self.mock_rvc.get_reported_state()})
        self.mock_rvc.start.assert_called_once()

    def test_apply_command_invalid_type(self):
        """Test applying a command with an invalid type."""
        self.mock_protocol.build_command_ack.return_value = {
            "status": "error",
            "error": "Invalid message type"
        }

        command_payload = {
            "type": "INVALID",
            "device_uuid": "RVC001",
            "state": {"cleaning": True}
        }

        ack = self.adapter.apply_command(command_payload)

        self.assertEqual(ack, {"status": "error", "error": "Invalid message type"})

    def test_apply_command_wrong_device_uuid(self):
        """Test applying a command with the wrong device UUID."""
        self.mock_protocol.build_command_ack.return_value = {
            "status": "error",
            "error": "Wrong device_uuid"
        }

        command_payload = {
            "type": "COMMAND",
            "device_uuid": "WRONG_ID",
            "state": {"cleaning": True}
        }

        ack = self.adapter.apply_command(command_payload)

        self.assertEqual(ack, {"status": "error", "error": "Wrong device_uuid"})

    def test_apply_command_return_to_base_priority(self):
        command_payload = {
            "type": "COMMAND",
            "device_uuid": "RVC001",
            "state": {
                "return_to_base": True,
                "cleaning": True
            }
        }

        self.adapter.apply_command(command_payload)

        self.mock_rvc.dock.assert_called_once()
        self.mock_rvc.start.assert_not_called()

    def test_send_command_ack(self):
        """Test sending a command acknowledgment."""
        self.adapter.session.post.return_value = MagicMock()
        self.adapter.session.post.return_value.status_code = 200
        self.adapter.session.post.return_value.json.return_value = {"status": "ok"}

        status_code, response = self.adapter.ack_command()

        self.assertEqual(status_code, 200)
        self.assertEqual(response, {"status": "ok"})

if __name__ == "__main__":
    unittest.main()