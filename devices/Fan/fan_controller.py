import serial
import time

PORT = "COM3"
BAUD = 9600


class FanController:
    def __init__(self):
        self.ser = serial.Serial(PORT, BAUD, timeout=2)

        print("Waiting for fan/Bluetooth to be ready...")
        time.sleep(15)

        self.state = {
            "power": False,
            "speed": 4,
            "mode": "normal",
            "timer": None,
            "swing": False
        }

    def send(self, cmd):
        print(f"Sending: {cmd}")
        self.ser.write(cmd.encode())
        self.ser.flush()
        time.sleep(1)

    def power_on(self):
        self.send("A")
        self.state.update({
            "power": True,
            "speed": 4,
            "mode": "normal",
            "timer": None
        })

    def power_off(self):
        self.send("S")
        self.state["power"] = False

    def speed_up(self):
        if self.state["speed"] < 7:
            self.send("F")
            self.state["speed"] += 1

    def speed_down(self):
        if self.state["speed"] > 1:
            self.send("G")
            self.state["speed"] -= 1

    def mode_next(self):
        self.send("D")
        modes = ["normal", "sleep", "nature"]
        current_index = modes.index(self.state["mode"])
        next_index = (current_index + 1) % len(modes)
        self.state["mode"] = modes[next_index]

    def timer_next(self):
        self.send("H")
        timers = [None, "0.5h", "1h", "2h", "4h"]
        current_index = timers.index(self.state["timer"])
        next_index = (current_index + 1) % len(timers)
        self.state["timer"] = timers[next_index]

    def toggle_swing(self):
        self.send("J")
        self.state["swing"] = not self.state["swing"]

    def apply_state(self, requested_state):
        if "power" in requested_state:
            if requested_state["power"]:
                self.power_on()
            else:
                self.power_off()

        if requested_state.get("speed_up"):
            self.speed_up()

        if requested_state.get("speed_down"):
            self.speed_down()

        if requested_state.get("mode_next"):
            self.mode_next()

        if requested_state.get("timer_next"):
            self.timer_next()

        if requested_state.get("swing_toggle"):
            self.toggle_swing()

        return self.state

    def get_status(self):
        return self.state

    def close(self):
        self.ser.close()