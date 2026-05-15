class MockRestAdapter:
    def __init__(self, device_id):
        self.device_id = device_id

    def heartbeat(self):
        print(f"[MOCK] Heartbeat sent for {self.device_id}")

    def get_command(self):
        return None  # or return a hardcoded command to test handling

    def apply_command(self, payload):
        return {"status": "ok", "reported_state": {}}

    def ack_command(self, payload):
        print(f"[MOCK] ACK sent: {payload}")

    def connect(self):
        print(f"[MOCK] Connected {self.device_id}")

    def connect_device(self):
        print(f"[MOCK] Connected {self.device_id}")

class MockFanController:
    def __init__(self):
        self.state = {
            "power": False,
            "speed": 4,
            "mode": "normal",
            "timer": None,
            "swing": False
        }
        print("[MOCK FAN] Initialized")

    def power_on(self):
        self.state.update({"power": True, "speed": 4, "mode": "normal", "timer": None})
        print("[MOCK FAN] Power ON")

    def power_off(self):
        self.state["power"] = False
        print("[MOCK FAN] Power OFF")

    def speed_up(self):
        if self.state["speed"] < 7:
            self.state["speed"] += 1
            print(f"[MOCK FAN] Speed up -> {self.state['speed']}")

    def speed_down(self):
        if self.state["speed"] > 1:
            self.state["speed"] -= 1
            print(f"[MOCK FAN] Speed down -> {self.state['speed']}")

    def mode_next(self):
        modes = ["normal", "sleep", "nature"]
        self.state["mode"] = modes[(modes.index(self.state["mode"]) + 1) % len(modes)]
        print(f"[MOCK FAN] Mode -> {self.state['mode']}")

    def timer_next(self):
        timers = [None, "0.5h", "1h", "2h", "4h"]
        self.state["timer"] = timers[(timers.index(self.state["timer"]) + 1) % len(timers)]
        print(f"[MOCK FAN] Timer -> {self.state['timer']}")

    def toggle_swing(self):
        self.state["swing"] = not self.state["swing"]
        print(f"[MOCK FAN] Swing -> {self.state['swing']}")

    def apply_state(self, requested_state):
        if "power" in requested_state:
            self.power_on() if requested_state["power"] else self.power_off()
        if requested_state.get("speed_up"): self.speed_up()
        if requested_state.get("speed_down"): self.speed_down()
        if requested_state.get("mode_next"): self.mode_next()
        if requested_state.get("timer_next"): self.timer_next()
        if requested_state.get("swing_toggle"): self.toggle_swing()
        return self.state

    def get_status(self):
        return self.state

    def close(self):
        print("[MOCK FAN] Closed")