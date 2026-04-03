from RVC import RVC
from RVC_Rest import RVCRestAdapter
import signal
import threading

stop_event = threading.Event()


def heartbeat_loop(rest_adapter):
    while not stop_event.is_set():
        rest_adapter.send_heartbeat()
        stop_event.wait(5)


def command_loop(rest_adapter):
    while not stop_event.is_set():
        command = rest_adapter.poll_next_command()
        if command:
            print(f"Received command: {command}")
            ack = rest_adapter.apply_command(command)
            rest_adapter.send_command_ack(ack)
        stop_event.wait(0.5)


def handle_shutdown(signum, frame):
    print("Stopping simulation...", flush=True)
    stop_event.set()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    rvc = RVC(device_id="RVC001", name="RoboVac", grid_size=10)
    rest_adapter = RVCRestAdapter(rvc, base_url="https://knolly-svetlana-beribboned.ngrok-free.dev/api/v1/device-gateway")
    rest_adapter.connect()

    heartbeat_thread = threading.Thread(target=heartbeat_loop, args=(rest_adapter,))
    heartbeat_thread.start()

    command_thread = threading.Thread(target=command_loop, args=(rest_adapter,))
    command_thread.start()

    try:
        while heartbeat_thread.is_alive() or command_thread.is_alive():
            heartbeat_thread.join(timeout=0.5)
            command_thread.join(timeout=0.5)
    except KeyboardInterrupt:
        handle_shutdown(None, None)
        heartbeat_thread.join(timeout=2)
        command_thread.join(timeout=2)


    # manual testing of RVC functionality
    """
    if rvc.visualizer:
        rvc.visualizer.initialize_plot(rvc.name)

    rvc.start()
    rvc.visualize()

    for _ in range(20):
        rvc.move()
        rvc.visualize()

    rvc.pause()
    rvc.resume()
    rvc.stop()
    rvc.dock()
    """
