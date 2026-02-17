class Device:
  def __init__(self, device_uuid, device_type, capabilities, state):
    self.device_uuid = device_uuid
    self.device_type = device_type
    self.capabilities = capabilities
    self.state = state