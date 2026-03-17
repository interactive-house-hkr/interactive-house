import os

DEVICE_UUID = os.getenv("DEVICE_UUID", "arduino")

HM10_UUID = os.getenv("HM10_UUID", "0000ffe1-0000-1000-8000-00805f9b34fb")
CMD_DELAY = float(os.getenv("CMD_DELAY", "0.2"))

USB_BAUD = int(os.getenv("USB_BAUD", "9600"))
USB_PORT = os.getenv("USB_PORT") or None

HEARTBEAT_INTERVAL = float(os.getenv("HEARTBEAT_INTERVAL", "1"))
RECONNECT_DELAY = float(os.getenv("RECONNECT_DELAY", "5"))

# Bridge integration with server
ENABLE_BRIDGE = os.getenv("ENABLE_BRIDGE", "true").lower() == "true"