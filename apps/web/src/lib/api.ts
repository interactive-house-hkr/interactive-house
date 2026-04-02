const BASE_URL = "http://localhost:8000/api/v1";

export interface ServerDevice {
  device_uuid: string;
  name: string;
  room: string;
  type: "light" | "fan";
  state: {
    power?: boolean;
    brightness?: number;
    speed?: number;
  };
}

export async function getDevices(): Promise<ServerDevice[]> {
  const res = await fetch(`${BASE_URL}/devices`);

  if (!res.ok) {
    throw new Error("Failed to fetch devices");
  }

  return res.json();
}

export async function sendDeviceCommand(
  id: string,
  state: { power?: boolean; brightness?: number; speed?: number }
) {
  const res = await fetch(`${BASE_URL}/devices/${id}/commands`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ state }),
  });

  if (!res.ok) {
    throw new Error("Failed to send command");
  }

  return res.json();
}