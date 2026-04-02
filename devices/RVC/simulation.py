from RVC import RVC
from RVC_Rest import RVCRestAdapter
import threading
import time

def heartbeat_loop(rest_adapter):
    while True:
        rest_adapter.send_heartbeat()
        time.sleep(5)

def command_loop(rest_adapter):
    while True:
        command = rest_adapter.poll_next_command()
        if command:
            print(f"Received command: {command}")
            ack = rest_adapter.apply_command(command)
            rest_adapter.send_command_ack(ack)
        time.sleep(0.5)


if __name__ == "__main__":
    rvc = RVC(device_id="RVC001", name="RoboVac", grid_size=10)
    rest_adapter = RVCRestAdapter(rvc, base_url="https://knolly-svetlana-beribboned.ngrok-free.dev/api/v1/device-gateway")
    rest_adapter.connect()

    heartbeat_thread = threading.Thread(target=heartbeat_loop, args=(rest_adapter,), daemon=True)
    heartbeat_thread.start()

    command_thread = threading.Thread(target=command_loop, args=(rest_adapter,), daemon=True)
    command_thread.start()

    heartbeat_thread.join()
    command_thread.join()


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