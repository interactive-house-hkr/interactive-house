const BASE_URL = "https://knolly-svetlana-beribboned.ngrok-free.dev/api/v1";

function getAuthHeaders() {
  const token = localStorage.getItem("token");

    return {
    "Content-Type": "application/json",
    Accept: "application/json",
    "ngrok-skip-browser-warning": "true",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export interface ServerDevice {
  device_uuid: string;

  name?: string;
  room?: string;

  type: string;

  is_online?: boolean;

  status?: {
    connected?: boolean;
    last_command_status?: string;
  };

  capabilities?: Record<
    string,
    {
      type: string;
      writable: boolean;
    }
  >;

  state: {
    power?: boolean;

    brightness?: number;

    speed?: number;

    cleaning?: boolean;

    open?: boolean;

    swing?: boolean;

    mode?: string;

    battery_level?: number;

    docked?: boolean;

    paused?: boolean;

    return_to_base?: boolean;
  };
}

export async function getDevices(): Promise<ServerDevice[]> {
  const token = localStorage.getItem("token");

  const res = await fetch(
    "https://knolly-svetlana-beribboned.ngrok-free.dev/api/v1/devices",
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        "ngrok-skip-browser-warning": "true",
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!res.ok) {
    const error = await res.text();
    console.error(error);

    throw new Error("Failed to fetch devices");
  }

  return res.json();
}

export async function sendDeviceCommand(
  id: string,
  state: {
    power?: boolean;

    brightness?: number;

    speed_up?: boolean;

    speed_down?: boolean;

    mode_next?: boolean;

    timer_next?: boolean;

    swing_toggle?: boolean;

    cleaning?: boolean;

    paused?: boolean;

    return_to_base?: boolean;

    open?: boolean;
  }
) {
  const res = await fetch(
    `${BASE_URL}/devices/${id}/commands`,
    {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ state }),
    }
  );

  if (!res.ok) {
    const text = await res.text();
    console.error(text);

    throw new Error("Failed to send command");
  }

  return res.json();
}