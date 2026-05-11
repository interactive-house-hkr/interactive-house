import time
from RVC import RVC
from RVC_Rest import RVCRestAdapter
import signal
import threading
from devices.Fan.fan_controller import FanController
from devices.Fan.rest_gateway import FanRestAdapter

stop_event = threading.Event()


def heartbeat_loop(rest_adapter):
    while not stop_event.is_set():
        rest_adapter.heartbeat()
        stop_event.wait(5)


def command_loop(rest_adapter):
    while not stop_event.is_set():
        command = rest_adapter.get_command()
        if command:
            print(f"Received command: {command}")
            ack = rest_adapter.apply_command(command)
            rest_adapter.ack_command(ack)
        stop_event.wait(0.5)

def rvc_tick_loop(rvc):
    while not stop_event.is_set():
        rvc.tick(time.time())
        stop_event.wait(0.1)


def handle_shutdown(signum, frame):
    print("Stopping simulation...", flush=True)
    stop_event.set()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    rvc = RVC(device_id="RVC001", name="RoboVac", grid_size=10)#
    rvc.rest_adapter = RVCRestAdapter(
        rvc, 
        base_url="https://knolly-svetlana-beribboned.ngrok-free.dev/api/v1/device-gateway"
    )
    rvc.rest_adapter.connect()

    fan = FanController()
    fan_adapter = FanRestAdapter(
        fan,
        base_url="http://localhost:8000/api/v1/device-gateway"
    )
    fan_adapter.connect_device()

    heartbeat_thread_rvc = threading.Thread(target=heartbeat_loop, args=(rvc.rest_adapter,))
    heartbeat_thread_rvc.start()

    command_thread_rvc = threading.Thread(target=command_loop, args=(rvc.rest_adapter,))
    command_thread_rvc.start()

    rvc_tick_thread = threading.Thread(target=rvc_tick_loop, args=(rvc,))
    rvc_tick_thread.start()

    heartbeat_thread_fan = threading.Thread(target=heartbeat_loop, args=(fan_adapter,))
    heartbeat_thread_fan.start()

    command_thread_fan = threading.Thread(target=command_loop, args=(fan_adapter,))
    command_thread_fan.start()

    threads = [
        heartbeat_thread_rvc,
        command_thread_rvc,
        rvc_tick_thread,
        heartbeat_thread_fan,
        command_thread_fan
    ]

    try:
        while any(t.is_alive() for t in threads):
            for t in threads:
                t.join(timeout=0.5)
    except KeyboardInterrupt:
        handle_shutdown(None, None)
        for t in threads:
            t.join(timeout=2)
    finally:
        stop_event.set()
        fan.close()