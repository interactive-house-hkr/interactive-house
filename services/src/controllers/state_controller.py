from services.src.models.state import DeviceState
from services.src.services import state_service


def get_state(device_uuid: str, user=None):
    # TODO: return state_service.get_state(device_uuid, user)
    return {"todo": "get_state service call", "device_uuid": device_uuid}

def patch_state(device_uuid: str, updates: dict, user=None):
    # TODO: return state_service.update_state(device_uuid, updates, user)
    return {"todo": "update_state service call", "device_uuid": device_uuid}
