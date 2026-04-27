export interface ServerDevice {
  device_uuid: string;
  type: "robot_vacuum" | "light" | "fan" | string;
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
  capabilities?: any;
  transport?: any;
}

export async function getDevices(): Promise<ServerDevice[]> {
  const res = await fetch("/api/devices");

  if (!res.ok) {
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
  const res = await fetch(
    `https://knolly-svetlana-beribboned.ngrok-free.dev/api/v1/devices/${id}/commands`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        "ngrok-skip-browser-warning": "true",
      },
      body: JSON.stringify({ state }),
    }
  );

  const data = await res.json();
  console.log("COMMAND RESPONSE:", data);

  if (!res.ok) {
    throw new Error("Failed to send command");
  }

  return data;
}