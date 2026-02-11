class Device:
  def __init__(self, deviceuuid, device_type, capabilities, state):
    self.deviceuuid = deviceuuid
    self.device_type = device_type
    self.capabilities = capabilities
    self.state = state