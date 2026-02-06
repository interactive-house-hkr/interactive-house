class Device:
  def __init__(self, device_id, device_type, capabilities, state):
    self.device_id = device_id
    self.device_type = device_type
    self.capabilities = capabilities
    self.state = state