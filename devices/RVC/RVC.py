# This file is for the RVC device, which is a type of robotic vacuum cleaner.
# It contains the internal simulation logic for the device.

# TODO:
# - Implement a more realistic movement pattern for the robot vacuum. (essential)
# - Add property for registration status.   (essential)
# - Add support for multiple rooms or zones in the grid. (optional)       

import time
import random

try:
    from RVC_Vis import RVCVisualizer
except ModuleNotFoundError:
    RVCVisualizer = None


class RVC:
    def __init__(self, device_id, name, grid_size=10):
        self.device_id = device_id
        self.name = name
        self.position = (0, 0)
        self.dock_position = (0, 0)
        self.state = "idle"   # idle, cleaning, paused, returning_to_base
        self.battery_level = 100
        self.visualizer = RVCVisualizer(grid_size) if RVCVisualizer else None
        self.grid_size = grid_size

    def get_state(self):
        return {
            "device_id": self.device_id,
            "name": self.name,
            "position": self.position,
            "state": self.state,
            "battery_level": self.battery_level
        }

    def get_reported_state(self):
        return {
            "cleaning": self.state == "cleaning",
            "paused": self.state == "paused",
            "return_to_base": self.state == "returning_to_base",
            "battery_level": self.battery_level,
            "position_x": self.position[0],
            "position_y": self.position[1],
            "docked": self.position == self.dock_position and self.state == "idle",
            "state_text": self.state
        }

    def start(self):
        if self.state == "idle":
            self.state = "cleaning"
            print(f"{self.name} has started cleaning.")
        elif self.state == "paused":
            self.resume()
        else:
            print(f"{self.name} is already {self.state}.")

    def stop(self):
        if self.state in ("cleaning", "paused"):
            self.state = "idle"
            print(f"{self.name} has stopped cleaning.")
            self.dock()
        else:
            print(f"{self.name} is not currently cleaning.")

    def pause(self):
        if self.state == "cleaning":
            self.state = "paused"
            print(f"{self.name} has paused cleaning.")
        else:
            print(f"{self.name} cannot pause while {self.state}.")

    def resume(self):
        if self.state == "paused":
            self.state = "cleaning"
            print(f"{self.name} has resumed cleaning.")
        else:
            print(f"{self.name} is not paused.")

    def dock(self):
        if self.position == self.dock_position:
            self.state = "idle"
            print(f"{self.name} is already at the base.")
            return

        self.state = "returning_to_base"
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

        self.state = "idle"
        print(f"{self.name} has docked at the base.")

    def update_battery_level(self, level):
        self.battery_level = max(0, min(100, level))
        print(f"{self.name}'s battery level is now {self.battery_level}%.")

    def move(self):
        if self.state == "cleaning":
            x, y = self.position

            pos_bool = True
            while pos_bool:
                new_x = random.randint(max(0, x - 1), min(self.grid_size - 1, x + 1))
                new_y = random.randint(max(0, y - 1), min(self.grid_size - 1, y + 1))
                if (new_x, new_y) != self.position:
                    pos_bool = False

            self.position = (new_x, new_y)
            self.battery_level = max(0, self.battery_level - 1)

            print(f"{self.name} has moved to position {self.position}.")
        else:
            print(f"{self.name} cannot move while {self.state}.")

    def visualize(self):
        if self.visualizer:
            self.visualizer.update_plot(self.position, self.name)
            time.sleep(1)
