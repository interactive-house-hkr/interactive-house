const BASE_URL = "https://knolly-svetlana-beribboned.ngrok-free.dev/api/v1";

function getAuthHeaders() {
  const token = localStorage.getItem("token");

  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

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
const res = await fetch(`${BASE_URL}/devices`, {
  headers: getAuthHeaders(),
});

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
    headers: getAuthHeaders(),
    body: JSON.stringify({ state }),
  });

  if (!res.ok) {
    throw new Error("Failed to send command");
  }

  return res.json();
}