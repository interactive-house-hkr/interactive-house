from RVC import RVC
from RVC_Rest import RVCRest

# TODO:
# - Implement threading to allow the RVC to send heartbeats and 
#   status updates at regular intervals. (essential)



if __name__ == "__main__":
    rvc = RVC(device_id="RVC001", name="RoboVac", grid_size=10)
    rest = RVCRest(rvc, base_url="URLGOESHERE/api/v1/device-gateway")

    rvc.visualizer.initialize_plot(rvc.name)
    rvc.start()
    rvc.visualize()

    for _ in range(20):
        rvc.move()
        rvc.visualize()

    rvc.stop()
