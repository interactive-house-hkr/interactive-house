"use client";

import { motion } from "framer-motion";
import { Lightbulb, Fan, Power, DoorOpen, Tablet, Box } from "lucide-react";

export interface Device {
  id: string;
  name: string;
  type: string;
  room: string;
  isOn: boolean;
  brightness?: number;
  speed?: number;
}

interface DeviceCardProps {
  device: Device;
  onToggle: (id: string) => void;
  onBrightnessChange: (id: string, value: number) => void;
  onSpeedChange: (id: string, value: number) => void;
}

export function DeviceCard({ device, onToggle, onSpeedChange }: DeviceCardProps) {
  // EXAKTA KOLLER MOT TYP
  const isFan = device.type === "fan";
  const isRobot = device.type === "robot_vacuum";
  const isDoor = device.type === "door";

  // SENSORER ELLER DÖRRAR GÅR INTE ATT STYRA
  const isReadOnly = isDoor || device.name.includes("Sensor") || device.name === "Arduino Bridge";

  return (
    <motion.div
      layout
      className={`rounded-2xl border p-5 transition-all ${
        device.isOn ? "bg-white border-teal-200 shadow-md" : "bg-gray-50 border-gray-200"
      }`}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${
            device.isOn ? "bg-teal-100 text-teal-600" : "bg-gray-200 text-gray-400"
          }`}>
            {isFan ? <Fan className={device.isOn ? "animate-spin" : ""} /> : 
             isRobot ? <Box /> : 
             isDoor ? <DoorOpen /> : <Lightbulb />}
          </div>
          <div>
            <p className="font-semibold text-gray-900 text-sm">{device.name}</p>
            <p className="text-xs text-gray-500">{device.room}</p>
          </div>
        </div>

        {!isReadOnly && (
          <button
            onClick={() => onToggle(device.id)}
            className={`flex h-9 w-9 items-center justify-center rounded-full transition-colors ${
              device.isOn ? "bg-teal-500 text-white" : "bg-gray-200 text-gray-400"
            }`}
          >
            <Power className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* ENBART FLÄKTAR VISAR SPEED-KNAPPAR */}
      {device.isOn && isFan && (
        <div className="pt-3 border-t border-gray-100">
          <p className="text-[10px] text-gray-400 mb-2 font-medium">SPEED CONTROL</p>
          <div className="flex gap-2">
            {[1, 2, 3, 4].map((s) => (
              <button
                key={s}
                onClick={() => onSpeedChange(device.id, s)}
                className={`flex-1 rounded-lg py-1.5 text-xs font-medium transition-colors ${
                  device.speed === s ? "bg-teal-500 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* STATUS-TEXT LÄNGST NER */}
      <div className="flex items-center gap-1.5 mt-3">
        <div className={`h-1.5 w-1.5 rounded-full ${device.isOn ? "bg-teal-500" : "bg-gray-400"}`} />
        <span className="text-[11px] text-gray-500">
          {isRobot ? (device.isOn ? "Cleaning" : "Docked") :
           isDoor ? (device.isOn ? "Open" : "Closed") :
           device.isOn ? "Active" : "Off"}
        </span>
      </div>
    </motion.div>
  );
}