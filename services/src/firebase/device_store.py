from datetime import datetime, timezone
from typing import Any, Dict, Optional

from services.src.firebase.firebase_client import get_ref


DEVICES_PATH = "devices"
PENDING_COMMANDS_PATH = "pending_commands"


def _devices_ref():
    """Returns a Firebase reference to the root devices node."""
    return get_ref(DEVICES_PATH)


def _device_ref(device_uuid: str):
    """Returns a Firebase reference to a specific device node by UUID."""
    return get_ref(f"{DEVICES_PATH}/{device_uuid}")


def _pending_commands_ref(device_uuid: str):
    """Returns a Firebase reference to the pending commands queue for a specific device."""
    return get_ref(f"{PENDING_COMMANDS_PATH}/{device_uuid}")


def _now_iso() -> str:
    """Returns the current UTC time as an ISO 8601 formatted string."""
    return datetime.now(timezone.utc).isoformat()


def _build_device(device_uuid: str, data: Dict[str, Any], existing: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Builds a complete device dictionary by merging new data with existing data.

    If existing data is provided, fields are merged rather than replaced.
    The device is always marked as connected=True when built.

    Args:
        device_uuid: The unique identifier of the device.
        data: New data to apply to the device.
        existing: Optional existing device data to merge with.

    Returns:
        A complete device dictionary ready to be stored in Firebase.
    """
    existing = existing or {}

    status = existing.get("status", {}).copy()
    status.update(data.get("status", {}))
    status["connected"] = True

    return {
        "device_uuid": device_uuid,
        "type": data.get("type", existing.get("type")),
        "transport": data.get("transport", existing.get("transport", {})),
        "capabilities": data.get("capabilities", existing.get("capabilities", {})),
        "state": data.get("state", existing.get("state", {})),
        "status": status,
        "last_seen": data.get("last_seen") or existing.get("last_seen") or _now_iso(),
    }


def get_device(device_uuid: str) -> Dict[str, Any] | None:
    """
    Retrieves a single device from Firebase by UUID.

    Args:
        device_uuid: The unique identifier of the device.

    Returns:
        The device dictionary, or None if not found.
    """
    return _device_ref(device_uuid).get()


def register_device(device_uuid: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Registers a new device in Firebase.

    Builds a complete device object from the provided data and stores it.

    Args:
        device_uuid: The unique identifier of the device.
        data: Device data including type, transport, capabilities, and state.

    Returns:
        The registered device dictionary.
    """
    device = _build_device(device_uuid, data)
    _device_ref(device_uuid).set(device)
    return device


def update_device(device_uuid: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates an existing device in Firebase by merging new data with existing data.

    Args:
        device_uuid: The unique identifier of the device.
        data: New data to merge into the existing device.

    Returns:
        The updated device dictionary.

    Raises:
        ValueError: If the device does not exist in Firebase.
    """
    existing = get_device(device_uuid)

    if not existing:
        raise ValueError("Device not found")

    updated = _build_device(device_uuid, data, existing=existing)
    _device_ref(device_uuid).set(updated)
    return updated


def list_devices() -> list[Dict[str, Any]]:
    """
    Returns a list of all registered devices from Firebase.

    Returns:
        A list of device dictionaries. Returns an empty list if no devices exist.
    """
    devices = _devices_ref().get() or {}
    return list(devices.values())


def delete_device(device_uuid: str) -> Dict[str, Any] | None:
    """
    Deletes a device and its pending commands from Firebase.

    Args:
        device_uuid: The unique identifier of the device to delete.

    Returns:
        The deleted device dictionary, or None if the device was not found.
    """
    device = get_device(device_uuid)
    if not device:
        return None

    _pending_commands_ref(device_uuid).delete()
    _device_ref(device_uuid).delete()
    return device


def update_last_seen(device_uuid: str, timestamp: datetime) -> Dict[str, Any]:
    """
    Updates the last_seen timestamp of a device and marks it as connected.

    Called on each heartbeat received from a device.

    Args:
        device_uuid: The unique identifier of the device.
        timestamp: The datetime of the most recent heartbeat.

    Returns:
        The updated device dictionary, or an error dict if the device was not found.
    """
    device = get_device(device_uuid)
    if not device:
        return {"error": "device not found", "device_uuid": device_uuid}

    device["last_seen"] = timestamp.isoformat()
    status = device.get("status", {})
    status["connected"] = True
    device["status"] = status
    _device_ref(device_uuid).set(device)
    return device


def update_device_state(
    device_uuid: str,
    reported_state: Dict[str, Any],
    status: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any] | None:
    """
    Updates the state of a device in Firebase.

    Merges the reported state with the existing state. Also updates
    the device's connected status and last_seen timestamp.

    Args:
        device_uuid: The unique identifier of the device.
        reported_state: A dictionary of state key-value pairs to merge.
        status: Optional status fields to merge into the device's status.

    Returns:
        The updated device dictionary, or None if the device was not found.
    """
    device = get_device(device_uuid)
    if not device:
        return None

    current_state = device.get("state", {})
    current_state.update(reported_state)
    device["state"] = current_state

    current_status = device.get("status", {})
    if status:
        current_status.update(status)
    current_status["connected"] = True
    device["status"] = current_status
    device["last_seen"] = _now_iso()

    _device_ref(device_uuid).set(device)
    return device


def enqueue_command(device_uuid: str, payload: Dict[str, Any]) -> None:
    """
    Adds a command to the pending commands queue for a device in Firebase.

    Commands are pushed to the queue and consumed in order by the device.

    Args:
        device_uuid: The unique identifier of the target device.
        payload: The command payload to enqueue.
    """
    _pending_commands_ref(device_uuid).push(payload)


def pop_next_command(device_uuid: str) -> Dict[str, Any] | None:
    """
    Retrieves and removes the next pending command for a device from Firebase.

    Commands are consumed in FIFO order based on their Firebase push keys.

    Args:
        device_uuid: The unique identifier of the device.

    Returns:
        The next command payload, or None if the queue is empty.
    """
    queue = _pending_commands_ref(device_uuid).get() or {}
    if not queue:
        return None

    next_key = sorted(queue.keys())[0]
    next_command = queue[next_key]
    _pending_commands_ref(device_uuid).child(next_key).delete()
    return next_command


def mark_stale_devices_offline(threshold_seconds: int = 30) -> list[str]:
    """
    Checks all devices in Firebase and marks them as offline (connected=False)
    if their last_seen timestamp is older than the given threshold.

    This function is called on each heartbeat to ensure stale device states
    do not persist in the system. Implements the mitigation for Risk R9.

    Args:
        threshold_seconds: Number of seconds without a heartbeat before a
                           device is considered offline. Defaults to 30.

    Returns:
        A list of device_uuids that were marked offline in this sweep.
    """
    now = datetime.now(timezone.utc)
    marked_offline = []

    devices = _devices_ref().get() or {}

    for device_uuid, device in devices.items():
        status = device.get("status", {})
        if not status.get("connected", False):
            continue

        last_seen_str = device.get("last_seen")
        if not last_seen_str:
            continue

        try:
            last_seen = datetime.fromisoformat(last_seen_str)
            if last_seen.tzinfo is None:
                last_seen = last_seen.replace(tzinfo=timezone.utc)
        except ValueError:
            continue

        elapsed = (now - last_seen).total_seconds()
        if elapsed > threshold_seconds:
            device["status"]["connected"] = False
            _device_ref(device_uuid).set(device)
            marked_offline.append(device_uuid)

    return marked_offline

