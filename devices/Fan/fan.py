import serial
import time

print("Starting fan control script...")

# Setup serial connection
ser = serial.Serial('COM13', 9600, timeout=1)
time.sleep(2)  # Let Arduino initialize


def send(command):
    """Send a single command to the fan."""
    ser.write((command).encode())
    return ser.readline().decode().strip()


# ---- Fan Controls ----

def power_on():
    return send("A")


def power_off():
    return send("S")


def speed_up():
    return send("F")


def speed_down():
    return send("G")


def set_mode():
    return send("D")


def set_timer():
    return send("H")


def swing():
    return send("J")


# ---- Example usage ----

print("Power ON:", power_on())
print("Speed UP:", speed_up())
print("Swing:", swing())
print("Power OFF:", power_off())


# Close connection
ser.close()