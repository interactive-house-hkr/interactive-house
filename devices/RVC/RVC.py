# This file is for the RVC device, which is a type of robotic vacuum cleaner. It is used to control the device and receive updates from it.

from RVC_Vis import RVCVisualizer
import time
import random

class RVC:
    def __init__(self, device_id, name, grid_size=10):
        self.device_id = device_id
        self.name = name
        self.position = (0, 0)
        self.dock_position = (0, 0)
        self.status = "idle"
        self.battery_level = 100
        self.visualizer = RVCVisualizer(grid_size)
        self.grid_size = grid_size


    def get_status(self):
        return {
            "device_id": self.device_id,
            "name": self.name,
            "position": self.position,
            "status": self.status,
            "battery_level": self.battery_level
        }  
    
    def start(self):
        if self.status == "idle":
            self.status = "cleaning"
            print(f"{self.name} has started cleaning.")
        else:
            print(f"{self.name} is already {self.status}.")

    def stop(self):
        if self.status == "cleaning":
            self.status = "idle"
            print(f"{self.name} has stopped cleaning.")
        else:
            print(f"{self.name} is not currently cleaning.")

    def dock(self):
        if self.status != "idle":
            self.status = "returning to base"
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
                self.visualize()  # Update visualization at each step

                if self.position == self.dock_position:
                    self.status = "idle"
                    print(f"{self.name} has docked at the base.")
        else:
            print(f"{self.name} is already at the base.")

    def update_battery_level(self, level):
        self.battery_level = level
        print(f"{self.name}'s battery level is now {self.battery_level}%.")

    def move(self):
        if self.status == "cleaning":
            x, y = self.position

            new_x = random.randint(max(0, x - 1), min(self.grid_size - 1, x + 1))
            new_y = random.randint(max(0, y - 1), min(self.grid_size - 1, y + 1))

            self.position = (new_x, new_y)
            print(f"{self.name} has moved to position {self.position}.")
        else:
            print(f"{self.name} cannot move while {self.status}.")

    def visualize(self):
        self.visualizer.update_plot(self.position, self.name)
        time.sleep(1)
        

if __name__ == "__main__":
    rvc = RVC(device_id="RVC001", name="RoboVac", grid_size=10)

    rvc.visualizer.initialize_plot(rvc.name)

    rvc.start()
    rvc.visualize()

    for _ in range(20):
        rvc.move()
        rvc.visualize()

    rvc.stop()
    rvc.dock()
