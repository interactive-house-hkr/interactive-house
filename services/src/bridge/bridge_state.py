active_ble_client = None
active_usb_serial = None
device_transports = {}


def set_active_ble_client(client):
    global active_ble_client
    active_ble_client = client


def clear_active_ble_client():
    global active_ble_client
    active_ble_client = None


def get_active_ble_client():
    return active_ble_client


def set_active_usb_serial(ser):
    global active_usb_serial
    active_usb_serial = ser


def clear_active_usb_serial():
    global active_usb_serial
    active_usb_serial = None


def get_active_usb_serial():
    return active_usb_serial


def register_device_transport(device_uuid: str, transport_type: str, transport):
    device_transports[device_uuid] = {
        "transport_type": transport_type,
        "transport": transport,
    }


def unregister_device_transport(device_uuid: str):
    device_transports.pop(device_uuid, None)


def clear_device_transports_for(transport_type: str, transport):
    stale_device_uuids = [
        device_uuid
        for device_uuid, binding in device_transports.items()
        if binding["transport_type"] == transport_type and binding["transport"] is transport
    ]

    for device_uuid in stale_device_uuids:
        unregister_device_transport(device_uuid)


def get_device_transport(device_uuid: str):
    return device_transports.get(device_uuid)
