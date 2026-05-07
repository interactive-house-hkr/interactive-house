"use client";

import { useEffect, useState } from "react";
import { DeviceCard, Device } from "@/components/DeviceCard";
import { Home } from "lucide-react";
import { getDevices, sendDeviceCommand, ServerDevice } from "@/lib/api";

const fallbackDevices: Device[] = [
  { id: "1", name: "Ceiling Light", type: "light", room: "Living Room", isOn: true, brightness: 80 },
  { id: "2", name: "Desk Lamp", type: "light", room: "Office", isOn: false, brightness: 50 },
  { id: "3", name: "Floor Lamp", type: "light", room: "Bedroom", isOn: true, brightness: 30 },
  { id: "4", name: "Ceiling Fan", type: "fan", room: "Living Room", isOn: true, speed: 2 },
  { id: "5", name: "Fan", type: "fan", room: "Bedroom", isOn: false, speed: 1 },
  { id: "6", name: "Vacuum Cleaner", type: "fan", room: "Living Room", isOn: false, speed: 1 },
];

function mapDevice(d: ServerDevice): Device {
  return {
    id: d.device_uuid,
    name: d.name,
    type: d.type,
    room: d.room,
    isOn: d.state?.power ?? false,
    brightness: d.state?.brightness,
    speed: d.state?.speed,
  };
}

export default function DashboardPage() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [activeRoom, setActiveRoom] = useState("All");
  const [loading, setLoading] = useState(true);
  const [usingFallback, setUsingFallback] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem("token");
    window.location.href = "/login";
  };

  async function loadDevices() {
    try {
      const data = await getDevices();
      const mapped = data.map(mapDevice);
      setDevices(mapped);
      setUsingFallback(false);
    } catch (err) {
      console.error("Server not available, using fallback", err);

      setDevices((prev) => (prev.length === 0 ? fallbackDevices : prev));
      setUsingFallback(true);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDevices();

    const interval = setInterval(() => {
      loadDevices();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const rooms = ["All", ...Array.from(new Set(devices.map((d) => d.room)))];

  const filtered =
    activeRoom === "All"
      ? devices
      : devices.filter((d) => d.room === activeRoom);

  const activeCount = devices.filter((d) => d.isOn).length;

  const toggle = async (id: string) => {
    const currentDevice = devices.find((d) => d.id === id);
    if (!currentDevice) return;

    const newPower = !currentDevice.isOn;

    setDevices((prev) =>
      prev.map((d) => (d.id === id ? { ...d, isOn: newPower } : d))
    );

    if (!usingFallback) {
      try {
        await sendDeviceCommand(id, { power: newPower });
        await loadDevices();
      } catch (err) {
        console.error(err);
      }
    }
  };

  const setBrightness = async (id: string, value: number) => {
    const currentDevice = devices.find((d) => d.id === id);
    if (!currentDevice) return;

    setDevices((prev) =>
      prev.map((d) => (d.id === id ? { ...d, brightness: value } : d))
    );

    if (!usingFallback) {
      try {
        await sendDeviceCommand(id, { brightness: value });
        await loadDevices();
      } catch (err) {
        console.error(err);
      }
    }
  };

  const setSpeed = async (id: string, value: number) => {
    const currentDevice = devices.find((d) => d.id === id);
    if (!currentDevice) return;

    setDevices((prev) =>
      prev.map((d) => (d.id === id ? { ...d, speed: value } : d))
    );

    if (!usingFallback) {
      try {
        await sendDeviceCommand(id, { speed: value });
        await loadDevices();
      } catch (err) {
        console.error(err);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b border-gray-200">
  <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
      <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-teal-100">
            <Home className="h-5 w-5 text-teal-600" />
          </div>
                </div>

          <div>
            <h1 className="text-lg font-bold text-gray-900">My Home</h1>
            <p className="text-xs text-gray-500">{activeCount} devices active</p>
          </div>
           <button
      onClick={handleLogout}
        className="px-4 py-2 text-sm font-medium rounded-lg bg-teal-500 text-white hover:bg-teal-600 transition-colors"       >
      Logout
    </button>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6">
        {usingFallback && (
          <div className="mb-4 rounded-lg bg-yellow-100 px-4 py-2 text-sm text-yellow-800">
            Showing demo devices (server not connected)
          </div>
        )}

        {loading ? (
          <p className="text-gray-500">Loading devices...</p>
        ) : (
          <>
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
          </>
        )}
      </main>
    </div>
  );
}