class Device:
  def __init__(self, deviceUuid, device_type, capabilities, state):
    self.deviceUuid = deviceUuid
    self.device_type = device_type
    self.capabilities = capabilities
    self.state = state