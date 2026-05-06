"use client";

import { useEffect, useState } from "react";
import { DeviceCard, Device } from "@/components/DeviceCard";
import { Home, LogOut } from "lucide-react";
import { getDevices, sendDeviceCommand, ServerDevice } from "@/lib/api";
import { useRouter } from "next/navigation";

const fallbackDevices: Device[] = [
  { id: "1", name: "Ceiling Light", type: "light", room: "Living Room", isOn: true },
  { id: "4", name: "Smart Fan", type: "fan", room: "Living Room", isOn: false, speed: 1 },
  { id: "6", name: "Vacuum Cleaner", type: "robot_vacuum", room: "Living Room", isOn: false },
  { id: "door-1", name: "Front Door", type: "door", room: "Hallway", isOn: false },
];

function mapDevice(d: ServerDevice): Device {
  const rawType = d.type || "unknown";
  let displayName = d.name || d.device_uuid || "Unknown Device";
  
  // Standardvärden
  let isOn = d.state?.power ?? d.is_online ?? false;
  let speed = undefined;
  let brightness = undefined;

  // Tvinga rätt state baserat på typ
  if (rawType === "robot_vacuum") {
    isOn = d.state?.cleaning ?? false;
  } else if (rawType === "fan") {
    isOn = d.state?.power ?? false;
    speed = d.state?.speed || 1;
  } else if (rawType === "light") {
    isOn = d.state?.power ?? false;
    brightness = d.state?.brightness;
  }

  // Manuella namn-fixar
  if (d.device_uuid === "pir-1") displayName = "Motion Sensor";
  if (d.device_uuid === "arduino-1") displayName = "Arduino Bridge";
  if (d.device_uuid === "door-1") displayName = "Door Sensor";
  if (d.device_uuid === "buzzer-1") displayName = "Buzzer";

  return {
    id: d.device_uuid,
    name: displayName,
    type: rawType,
    room: d.room || "Home",
    isOn,
    brightness,
    speed,
  };
}

export default function DashboardPage() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [activeRoom, setActiveRoom] = useState("All");
  const [loading, setLoading] = useState(true);
  const [usingFallback, setUsingFallback] = useState(false);
  const router = useRouter();

  async function loadDevices() {
    try {
      const data = await getDevices();
      setDevices(data.map(mapDevice));
      setUsingFallback(false);
    } catch (err) {
      setDevices((prev) => (prev.length === 0 ? fallbackDevices : prev));
      setUsingFallback(true);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDevices();
    const interval = setInterval(loadDevices, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/login");
  };

  const toggle = async (id: string) => {
    const currentDevice = devices.find((d) => d.id === id);
    if (!currentDevice) return;

    const newPower = !currentDevice.isOn;

    // UI-uppdatering med speed 4 logik
    setDevices((prev) =>
      prev.map((d) => {
        if (d.id === id) {
          return { 
            ...d, 
            isOn: newPower, 
            speed: (d.type === "fan" && newPower) ? 4 : d.speed 
          };
        }
        return d;
      })
    );

    if (usingFallback) return;

    try {
      if (currentDevice.type === "light") {
        await sendDeviceCommand(id, { power: newPower });
      } else if (currentDevice.type === "fan") {
        await sendDeviceCommand(id, { power: newPower, speed: newPower ? 4 : 0 });
      } else if (currentDevice.type === "robot_vacuum") {
        await sendDeviceCommand(id, { cleaning: newPower });
      }
      await loadDevices();
    } catch (err) {
      console.error(err);
      await loadDevices();
    }
  };

  const setSpeed = async (id: string, value: number) => {
    setDevices((prev) => prev.map((d) => (d.id === id ? { ...d, speed: value } : d)));
    if (!usingFallback) {
      try {
        await sendDeviceCommand(id, { power: true, speed: value });
        await loadDevices();
      } catch (err) { console.error(err); }
    }
  };

  const rooms = ["All", ...Array.from(new Set(devices.map((d) => d.room)))];
  const filtered = activeRoom === "All" ? devices : devices.filter((d) => d.room === activeRoom);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-teal-100 text-teal-600">
              <Home className="h-5 w-5" />
            </div>
            <h1 className="text-lg font-bold text-gray-900">My Home</h1>
          </div>
          <button onClick={handleLogout} className="text-sm font-medium text-gray-600 hover:text-red-600">
            Logout
          </button>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6">
        <div className="flex gap-2 mb-6 overflow-x-auto pb-1">
          {rooms.map((room) => (
            <button
              key={room}
              onClick={() => setActiveRoom(room)}
              className={`shrink-0 rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
                activeRoom === room ? "bg-teal-500 text-white" : "bg-gray-200 text-gray-600"
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
              onBrightnessChange={() => {}}
              onSpeedChange={setSpeed}
            />
          ))}
        </div>
      </main>
    </div>
  );
}