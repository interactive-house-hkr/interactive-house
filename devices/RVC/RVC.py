# This file is for the RVC device, which is a type of robotic vacuum cleaner.
# It contains the internal simulation logic for the device.

import time
import random
from collections import deque

from floorplan import GRID_SIZE, DOCK_POSITION, WALKABLE_CELLS, neighbors, shortest_path, room_name

LOW_BATTERY_THRESHOLD = 20
MOVE_INTERVAL = 0.45
CHARGE_INTERVAL = 0.20
CHARGE_STEP_AMOUNT = 2

try:
    from RVC_Vis import RVCVisualizer
except ModuleNotFoundError:
    RVCVisualizer = None


class RVC:
    def __init__(self, device_id, name, grid_size=GRID_SIZE):
        self.device_id = device_id
        self.name = name
        self.grid_size = grid_size

        self.position = DOCK_POSITION
        self.dock_position = DOCK_POSITION
        self.status = "idle"   # idle, cleaning, paused, returning_to_base
        self.battery_level = 100
        self.low_battery_triggered = False
        self.last_move_time = 0.0
        self.last_charge_time = 0.0

        self.cleaned_cells = {self.position}
        self.visualizer = RVCVisualizer(grid_size) if RVCVisualizer else None

    def get_status(self):
        return {
            "device_id": self.device_id,
            "name": self.name,
            "position": self.position,
            "position_x": self.position[0],
            "position_y": self.position[1],
            "status": self.status,
            "battery_level": self.battery_level,
            "current_room": room_name(self.position),
        }

    def get_reported_state(self):
        return {
            "cleaning": self.status == "cleaning",
            "paused": self.status == "paused",
            "return_to_base": self.status == "returning_to_base",
            "docked": self.position == self.dock_position and self.status == "idle",
            "battery_level": self.battery_level,
            "low_battery": self.battery_level <= LOW_BATTERY_THRESHOLD,
            "position_x": self.position[0],
            "position_y": self.position[1],
            "current_room": room_name(self.position),
            "status_text": self.status,
        }

    def start(self):
        if self.battery_level <= LOW_BATTERY_THRESHOLD and self.position != self.dock_position:
            print(f"{self.name} cannot start cleaning. Battery is too low.")
            return

        if self.status == "idle":
            self.status = "cleaning"
            self.low_battery_triggered = False
            self.cleaned_cells = {self.position}
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
            self.low_battery_triggered = False
            print(f"{self.name} is already at the base.")
            return

        self.status = "returning_to_base"
        print(f"{self.name} is returning to base.")

        path = shortest_path(self.position, self.dock_position)
        if not path:
            print(f"{self.name} could not find a path back to the dock.")
            self.status = "paused"
            return

        for step in path[1:]:
            self.position = step
            self.cleaned_cells.add(step)
            self.visualize()
            time.sleep(0.12)

        self.status = "idle"
        self.low_battery_triggered = False
        print(f"{self.name} has docked at the base.")

    def update_battery_level(self, level):
        self.battery_level = max(0, min(100, level))
        print(f"{self.name}'s battery level is now {self.battery_level}%.")

    def nearest_unvisited(self):
        unvisited = WALKABLE_CELLS - self.cleaned_cells
        if not unvisited:
            return None

        queue = deque([self.position])
        seen = {self.position}

        while queue:
            current = queue.popleft()
            if current in unvisited:
                return current
            for neighbor in neighbors(current):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)

        return None
    
    def move(self):
        if self.status != "cleaning":
            return

        target = self.nearest_unvisited()

        if target is None:
            # All reachable cells are clean, return to dock
            print(f"{self.name} has finished cleaning all reachable cells.")
            self.dock()
            return

        path = shortest_path(self.position, target)

        # Take one step along the path toward the target
        if len(path) >= 2:
            next_position = path[1]
        else:
            next_position = self.position

        self.position = next_position
        self.cleaned_cells.add(next_position)
        self.battery_level = max(0, self.battery_level - 1)

        time.sleep(0.2)

        if self.battery_level <= LOW_BATTERY_THRESHOLD and self.position != self.dock_position:
            self.low_battery_triggered = True
            self.dock()

    def charge_step(self):
        if self.position == self.dock_position and self.status == "idle" and self.battery_level < 100:
            self.battery_level = min(100, self.battery_level + CHARGE_STEP_AMOUNT)

    def toggle_clean_pause(self):
        if self.status == "idle":
            self.start()
        elif self.status == "cleaning":
            self.pause()
        elif self.status == "paused":
            self.resume()

    def reset_demo(self):
        self.position = self.dock_position
        self.status = "idle"
        self.battery_level = 100
        self.low_battery_triggered = False
        self.cleaned_cells = {self.position}

        if self.visualizer:
            self.visualizer.reset_traces()

    def tick(self, now):
        if self.status == "cleaning" and now - self.last_move_time >= MOVE_INTERVAL:
            self.move()
            self.last_move_time = now

        elif (
            self.status == "idle"
            and self.position == self.dock_position
            and self.battery_level < 100
            and now - self.last_charge_time >= CHARGE_INTERVAL
        ):
            self.charge_step()
            self.last_charge_time = now

    def visualize(self):
        if self.visualizer:
            return self.visualizer.update_plot(
                self.position,
                self.name,
                self.status,
                self.battery_level
            )
        return []


if __name__ == "__main__":
    rvc = RVC(device_id="RVC001", name="RoboVac", grid_size=8)

    if rvc.visualizer:
        rvc.visualizer.initialize_plot(rvc.name)

    running = True
    while running and rvc.visualizer and rvc.visualizer.running:
        actions = rvc.visualize()

        for action in actions:
            if action == "toggle_clean":
                rvc.toggle_clean_pause()
            elif action == "dock":
                rvc.dock()
            elif action == "stop":
                rvc.stop()
            elif action == "reset":
                rvc.reset_demo()
            elif action == "quit":
                running = False

        rvc.tick(time.time())
        time.sleep(0.3)