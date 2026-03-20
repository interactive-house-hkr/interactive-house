active_ble_client = None
active_usb_serial = None


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
