export interface ServerDevice {
  device_uuid: string;
  name?: string;
  type: "robot_vacuum" | "light" | "fan" | string;
  room?: string;
  last_seen?: string;
  is_online?: boolean;
  state: {
    cleaning?: boolean;
    docked?: boolean;
    paused?: boolean;
    return_to_base?: boolean;
    power?: boolean;
    brightness?: number;
    speed?: number;
  };
  status?: {
    connected?: boolean;
    last_command_status?: string;
  };
  capabilities?: unknown;
  transport?: unknown;
}

const BASE_URL = "https://knolly-svetlana-beribboned.ngrok-free.dev/api/v1";

function getAuthHeaders() {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("token") : null;

  return {
    Accept: "application/json",
    "ngrok-skip-browser-warning": "true",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function getDevices(): Promise<ServerDevice[]> {
  const res = await fetch(`${BASE_URL}/devices`, {
    headers: getAuthHeaders(),
  });

  if (!res.ok) {
    const errorText = await res.text();
    console.error("GET DEVICES ERROR:", res.status, errorText);
    throw new Error("Failed to fetch devices");
  }

  return res.json();
}

export async function sendDeviceCommand(
  id: string,
  state: {
    cleaning?: boolean;
    paused?: boolean;
    return_to_base?: boolean;
    power?: boolean;
    brightness?: number;
    speed?: number;
  }
) {
  const res = await fetch(`${BASE_URL}/devices/${id}/commands`, {
    method: "POST",
    headers: {
      ...getAuthHeaders(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ state }),
  });

  const data = await res.json();

  if (!res.ok) {
    console.error("COMMAND ERROR:", res.status, data);
    throw new Error("Failed to send command");
  }

  return data;
}