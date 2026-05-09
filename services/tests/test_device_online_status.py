from datetime import datetime, timedelta, timezone

from services.src.services import device_service


def iso_seconds_ago(seconds):
    return (datetime.now(timezone.utc) - timedelta(seconds=seconds)).isoformat()


def test_direct_device_is_online_when_last_seen_is_recent():
    device = {
        "device_uuid": "fan-1",
        "last_seen": iso_seconds_ago(5),
    }

    assert device_service.is_device_online(device) is True


def test_direct_device_is_offline_when_last_seen_is_old():
    device = {
        "device_uuid": "fan-1",
        "last_seen": iso_seconds_ago(60),
    }

    assert device_service.is_device_online(device) is False


def test_child_device_is_online_when_controller_is_online():
    controller = {
        "device_uuid": "arduino-1",
        "last_seen": iso_seconds_ago(5),
    }
    child = {
        "device_uuid": "light-1",
        "last_seen": iso_seconds_ago(60),
        "transport": {
            "mode": "via_controller",
            "controller_uuid": "arduino-1",
        },
    }
    devices_by_uuid = {
        "arduino-1": controller,
        "light-1": child,
    }

    assert device_service.is_device_online(child, devices_by_uuid) is True


def test_child_device_is_offline_when_controller_is_offline():
    controller = {
        "device_uuid": "arduino-1",
        "last_seen": iso_seconds_ago(60),
    }
    child = {
        "device_uuid": "light-1",
        "last_seen": iso_seconds_ago(60),
        "transport": {
            "mode": "via_controller",
            "controller_uuid": "arduino-1",
        },
    }
    devices_by_uuid = {
        "arduino-1": controller,
        "light-1": child,
    }

    assert device_service.is_device_online(child, devices_by_uuid) is False

