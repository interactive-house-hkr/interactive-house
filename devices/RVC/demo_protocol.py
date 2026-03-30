import json
from RVC import RVC
from rvc_protocol_adapter import RVCProtocolAdapter


def pretty_print(title: str, payload: dict):
    print(f"\n--- {title} ---")
    print(json.dumps(payload, indent=2))


def main():
    rvc = RVC(device_id="RVC001", name="RoboVac", grid_size=10)
    adapter = RVCProtocolAdapter(rvc)

    pretty_print("CONNECT", adapter.build_initial_connect_message())
    pretty_print("HEARTBEAT", adapter.build_heartbeat_message())

    command_start = {
        "type": "COMMAND",
        "device_uuid": "RVC001",
        "state": {
            "cleaning": True
        }
    }

    ack = adapter.apply_command(command_start)
    pretty_print("COMMAND_ACK after start", ack)

    rvc.move()
    pretty_print("STATE after one move", rvc.get_reported_state())

    command_pause = {
        "type": "COMMAND",
        "device_uuid": "RVC001",
        "state": {
            "paused": True
        }
    }

    ack = adapter.apply_command(command_pause)
    pretty_print("COMMAND_ACK after pause", ack)

    command_resume = {
        "type": "COMMAND",
        "device_uuid": "RVC001",
        "state": {
            "paused": False,
            "cleaning": True
        }
    }

    ack = adapter.apply_command(command_resume)
    pretty_print("COMMAND_ACK after resume", ack)

    command_dock = {
        "type": "COMMAND",
        "device_uuid": "RVC001",
        "state": {
            "return_to_base": True
        }
    }

    ack = adapter.apply_command(command_dock)
    pretty_print("COMMAND_ACK after dock", ack)


if __name__ == "__main__":
    main()