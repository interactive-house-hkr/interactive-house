import { Device } from "../types/device";

const BASE_URL = "http://localhost:8080/api/v1";

export async function fetchDevices(): Promise<Device[]> {
  const response = await fetch(`${BASE_URL}/devices`);

  if (!response.ok) {
    throw new Error("Failed to fetch devices");
  }

  return response.json();
}