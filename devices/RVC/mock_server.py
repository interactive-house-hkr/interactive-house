from flask import Flask, jsonify, request

app = Flask(__name__)

command = None
device_states = {}
connected_devices = {}


@app.route("/api/v1/device-gateway/connect", methods=["POST"])
def connect():
    data = request.json
    print("Device connected:", data)

    devices = data.get("devices", {})
    for device_uuid, device_data in devices.items():
        connected_devices[device_uuid] = device_data
        device_states[device_uuid] = device_data.get("state", {})

    return jsonify({
        "message": "Devices connected",
        "devices": connected_devices
    })


@app.route("/api/v1/device-gateway/<device_uuid>/heartbeat", methods=["POST"])
def heartbeat(device_uuid):
    return jsonify({
        "device_uuid": device_uuid,
        "state": device_states.get(device_uuid, {})
    })


@app.route("/api/v1/device-gateway/<device_uuid>/commands/next", methods=["GET"])
def next_command(device_uuid):
    global command

    if command:
        cmd = command
        command = None
        return jsonify({
            "device_uuid": device_uuid,
            "command": cmd
        })

    return jsonify({
        "device_uuid": device_uuid,
        "command": None
    })


@app.route("/api/v1/device-gateway/<device_uuid>/command-ack", methods=["POST"])
def ack(device_uuid):
    data = request.json
    reported_state = data.get("reported_state", {})

    device_states[device_uuid] = reported_state

    print("ACK received:")
    print(data)
    print("Saved state:")
    print(device_states[device_uuid])

    return jsonify({
        "message": "Command acknowledgement received",
        "device_uuid": device_uuid,
        "status": data.get("status"),
        "reported_state": reported_state
    })


@app.route("/send-command", methods=["POST"])
def send_command():
    global command
    command = request.json

    print("Command queued:")
    print(command)

    return jsonify({
        "status": "queued",
        "command": command
    })


@app.route("/state", methods=["GET"])
def get_state():
    return jsonify(device_states)


@app.route("/state/<device_uuid>", methods=["GET"])
def get_device_state(device_uuid):
    return jsonify({
        "device_uuid": device_uuid,
        "state": device_states.get(device_uuid)
    })


if __name__ == "__main__":
    app.run(port=8000)