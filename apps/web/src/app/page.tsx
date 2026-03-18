"use client";

import { useState } from "react";
import DeviceCard from "../components/DeviceCard";
import { Device } from "../types/device";

export default function Home() {
  const [devices, setDevices] = useState<Device[]>([
    {
      device_uuid: "light-1",
      name: "Living Room Lamp",
      room: "Living Room",
      type: "light",
      state: {
        power: true,
        brightness: 80,
      },
    },
    {
      device_uuid: "fan-1",
      name: "Bedroom Fan",
      room: "Bedroom",
      type: "fan",
      state: {
        power: false,
      },
    },
  ]);

  function togglePower(deviceUuid: string) {
    const updatedDevices = devices.map((device) => {
      if (device.device_uuid === deviceUuid) {
        return {
          ...device,
          state: {
            ...device.state,
            power: !device.state.power,
          },
        };
      }
      return device;
    });

    setDevices(updatedDevices);
  }

  return (
    <main
      style={{
        padding: "2rem",
        fontFamily: "Arial, sans-serif",
        backgroundColor: "#f5f5f5",
        minHeight: "100vh",
      }}
    >
      <h1
        style={{
          fontSize: "2.2rem",
          fontWeight: "600",
          marginBottom: "0.5rem",
        }}
      >
        Smart Home Dashboard
      </h1>

      <p
        style={{
          marginBottom: "2rem",
          color: "#666",
          fontSize: "1rem",
        }}
      >
        Welcome! Here you can view and control your devices.
      </p>

      <section
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
          gap: "1rem",
        }}
      >
        {devices.map((device) => (
          <DeviceCard
            key={device.device_uuid}
            device={device}
            onToggle={togglePower}
          />
        ))}
      </section>
    </main>
  );
}