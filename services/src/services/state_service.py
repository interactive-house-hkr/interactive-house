from models.state import DeviceState

# Returns the current state values
def get_state(state: DeviceState) -> dict:
  return state.values

# Update parts of the state (PATCH)
def update_state(state: DeviceState, updates:dict) -> DeviceState:
  state.values.update(updates)
  return state