"use client";

import { useState } from "react";
import { DeviceCard, Device } from "@/components/DeviceCard";
import { Home } from "lucide-react";

const initialDevices: Device[] = [
  { id: "1", name: "Ceiling Light", type: "light", room: "Living Room", isOn: true, brightness: 80 },
  { id: "2", name: "Desk Lamp", type: "light", room: "Office", isOn: false, brightness: 50 },
  { id: "3", name: "Floor Lamp", type: "light", room: "Bedroom", isOn: true, brightness: 30 },
  { id: "4", name: "Ceiling Fan", type: "fan", room: "Living Room", isOn: true, speed: 2 },
  { id: "5", name: "Fan", type: "fan", room: "Bedroom", isOn: false, speed: 1 },
  { id: "6", name: "Vacuum Cleaner", type: "fan", room: "Living Room", isOn: false, speed: 1 },
];

const rooms = ["All", ...Array.from(new Set(initialDevices.map((d) => d.room)))];

export default function DashboardPage() {
  const [devices, setDevices] = useState<Device[]>(initialDevices);
  const [activeRoom, setActiveRoom] = useState("All");

  const filtered =
    activeRoom === "All"
      ? devices
      : devices.filter((d) => d.room === activeRoom);

  const activeCount = devices.filter((d) => d.isOn).length;

  const toggle = (id: string) =>
    setDevices((prev) =>
      prev.map((d) => (d.id === id ? { ...d, isOn: !d.isOn } : d))
    );

  const setBrightness = (id: string, value: number) =>
    setDevices((prev) =>
      prev.map((d) => (d.id === id ? { ...d, brightness: value } : d))
    );

  const setSpeed = (id: string, value: number) =>
    setDevices((prev) =>
      prev.map((d) => (d.id === id ? { ...d, speed: value } : d))
    );

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-teal-100">
            <Home className="h-5 w-5 text-teal-600" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900">My Home</h1>
            <p className="text-xs text-gray-500">{activeCount} devices active</p>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6">
        <div className="flex gap-2 mb-6 overflow-x-auto pb-1">
          {rooms.map((room) => (
            <button
              key={room}
              onClick={() => setActiveRoom(room)}
              className={`shrink-0 rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
                activeRoom === room
                  ? "bg-teal-500 text-white"
                  : "bg-gray-200 text-gray-600 hover:bg-gray-300"
              }`}
            >
              {room}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((device) => (
            <DeviceCard
              key={device.id}
              device={device}
              onToggle={toggle}
              onBrightnessChange={setBrightness}
              onSpeedChange={setSpeed}
            />
          ))}
        </div>

        {filtered.length === 0 && (
          <p className="text-center text-gray-500 py-12">
            No devices in this room.
          </p>
        )}
      </main>
    </div>
  );
}