# This file is for the RVC device, which is a type of robotic vacuum cleaner.
# It contains the internal simulation logic for the device.

import time
import random

try:
    from devices.RVC.RVC_Vis import RVCVisualizer
except ModuleNotFoundError:
    RVCVisualizer = None


class RVC:
    def __init__(self, device_id, name, grid_size=10):
        self.device_id = device_id
        self.name = name
        self.position = (0, 0)
        self.dock_position = (0, 0)
        self.status = "idle"   # idle, cleaning, paused, returning_to_base
        self.battery_level = 100
        self.visualizer = RVCVisualizer(grid_size) if RVCVisualizer else None
        self.grid_size = grid_size

    def get_status(self):
        return {
            "device_id": self.device_id,
            "name": self.name,
            "position": self.position,
            "status": self.status,
            "battery_level": self.battery_level
        }

    def get_reported_state(self):
        return {
            "cleaning": self.status == "cleaning",
            "paused": self.status == "paused",
            "return_to_base": self.status == "returning_to_base",
            "battery_level": self.battery_level,
            "position_x": self.position[0],
            "position_y": self.position[1],
            "docked": self.position == self.dock_position and self.status == "idle",
            "status_text": self.status
        }

    def start(self):
        if self.status == "idle":
            self.status = "cleaning"
            print(f"{self.name} has started cleaning.")
        elif self.status == "paused":
            self.resume()
        else:
            print(f"{self.name} is already {self.status}.")

    def stop(self):
        if self.status in ("cleaning", "paused"):
            self.status = "idle"
            print(f"{self.name} has stopped cleaning.")
        else:
            print(f"{self.name} is not currently cleaning.")

    def pause(self):
        if self.status == "cleaning":
            self.status = "paused"
            print(f"{self.name} has paused cleaning.")
        else:
            print(f"{self.name} cannot pause while {self.status}.")

    def resume(self):
        if self.status == "paused":
            self.status = "cleaning"
            print(f"{self.name} has resumed cleaning.")
        else:
            print(f"{self.name} is not paused.")

    def dock(self):
        if self.position == self.dock_position:
            self.status = "idle"
            print(f"{self.name} is already at the base.")
            return

        self.status = "returning_to_base"
        print(f"{self.name} is returning to base.")

        x, y = self.position
        while (x, y) != self.dock_position:
            if x < self.dock_position[0]:
                x += 1
            elif x > self.dock_position[0]:
                x -= 1

            if y < self.dock_position[1]:
                y += 1
            elif y > self.dock_position[1]:
                y -= 1

            self.position = (x, y)
            print(f"{self.name} is moving to position {self.position}.")
            self.visualize()

        self.status = "idle"
        print(f"{self.name} has docked at the base.")

    def update_battery_level(self, level):
        self.battery_level = max(0, min(100, level))
        print(f"{self.name}'s battery level is now {self.battery_level}%.")

    def move(self):
        if self.status == "cleaning":
            x, y = self.position

            new_x = random.randint(max(0, x - 1), min(self.grid_size - 1, x + 1))
            new_y = random.randint(max(0, y - 1), min(self.grid_size - 1, y + 1))

            self.position = (new_x, new_y)
            self.battery_level = max(0, self.battery_level - 1)

            print(f"{self.name} has moved to position {self.position}.")
        else:
            print(f"{self.name} cannot move while {self.status}.")

    def visualize(self):
        if self.visualizer:
            self.visualizer.update_plot(self.position, self.name)
            time.sleep(1)


if __name__ == "__main__":
    rvc = RVC(device_id="RVC001", name="RoboVac", grid_size=10)

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