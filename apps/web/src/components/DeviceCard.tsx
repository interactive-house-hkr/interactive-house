"use client";

import { motion } from "framer-motion";
import { Lightbulb, Fan, Power } from "lucide-react";

export interface Device {
  id: string;
  name: string;
  type: string;
  room: string;
  isOn: boolean;
  brightness?: number;
  speed?: number;
  statusLabel: string;

  uiState: {
    reachable: boolean;
    active: boolean;
    status: string;
  };


  capabilities?: Record<
    string,
    {
      type: string;
      writable: boolean;
    }
  >;
}

interface DeviceCardProps {
  device: Device;
  onToggle: (id: string) => void;
  onBrightnessChange: (id: string, value: number) => void;
  onSpeedChange: (id: string, value: number) => void;
  

  onAction: (
  id: string,
  action: string
) => void;

}

export function DeviceCard({
  device,
  onToggle,
  onBrightnessChange,
  onSpeedChange,
  onAction
}: DeviceCardProps) {
  const hasBrightness =
    device.capabilities?.brightness?.writable;

  const canIncreaseSpeed =
  device.capabilities?.speed_up?.writable;

const canDecreaseSpeed =
  device.capabilities?.speed_down?.writable;

const hasSpeedControls =
  canIncreaseSpeed || canDecreaseSpeed;

const canToggleSwing =
  device.capabilities?.swing_toggle?.writable;

const canCycleMode =
  device.capabilities?.mode_next?.writable;

    const hasWritableCapabilities =
  !!device.capabilities &&
  Object.values(device.capabilities).some(
    (cap) => cap.writable
  );

    const isActive =
  device.uiState.active;

  const Icon = hasBrightness
    ? Lightbulb
    : hasSpeedControls
    ? Fan
    : Power;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-2xl border p-5 transition-shadow ${
        isActive
          ? "bg-white border-teal-200 shadow-lg shadow-teal-500/10"
          : "bg-gray-50 border-gray-200"
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div
            className={`flex h-10 w-10 items-center justify-center rounded-xl ${
              isActive
                ? "bg-teal-100 text-teal-600"
                : "bg-gray-200 text-gray-400"
            }`}
          >
            <Icon
              className={`h-5 w-5 ${
                hasSpeedControls && isActive ? "animate-spin" : ""
              }`}
              style={
                hasSpeedControls && isActive
                  ? {
                      animationDuration: `${4 - (device.speed || 1)}s`,
                    }
                  : {}
              }
            />
          </div>

          <div>
            <p className="font-semibold text-gray-900 text-sm">
              {device.name}
            </p>
            <p className="text-xs text-gray-500">{device.room}</p>
          </div>
        </div>

        {/* Power button */}
        {hasWritableCapabilities && (
        <button
          onClick={() => onToggle(device.id)}
          className={`flex h-9 w-9 items-center justify-center rounded-full transition-colors ${
            isActive
              ? "bg-teal-500 text-white hover:bg-teal-600"
              : "bg-gray-200 text-gray-400 hover:bg-gray-300"
          }`}
        >
          <Power className="h-4 w-4" />
        </button>
        )}
      </div>

      {/* Controls */}
      {isActive && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          className="pt-3 border-t border-gray-100"
        >
          {/* Brightness */}
          {hasBrightness && device.brightness !== undefined && (
            <div>
              <div className="flex justify-between text-xs text-gray-500 mb-2">
                <span>Brightness</span>
                <span>{device.brightness}%</span>
              </div>

              <input
                type="range"
                min={0}
                max={100}
                value={device.brightness}
                onChange={(e) =>
                  onBrightnessChange(
                    device.id,
                    Number(e.target.value)
                  )
                }
                className="w-full h-2 rounded-full appearance-none bg-gray-200 accent-teal-500"
              />
            </div>
          )}

          {hasSpeedControls && (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs text-gray-500">Fan Speed</p>

                  <span className="text-xs font-medium text-gray-700">
                    {device.speed ?? 4}
                  </span>
                </div>

                <div className="flex gap-2">
                  {canDecreaseSpeed && (
                    <button
                      onClick={() =>
                        onSpeedChange(
                          device.id,
                          Math.max(1, (device.speed ?? 4) - 1)
                        )
                      }
className="flex-1 rounded-lg py-2 text-sm font-medium bg-gray-100 text-gray-700 hover:bg-gray-200"
        >
          -
        </button>
      )}

      {canIncreaseSpeed && (
        <button
          onClick={() =>
            onSpeedChange(
              device.id,
              Math.min(8, (device.speed ?? 4) + 1)
            )
          }
          className="flex-1 rounded-lg py-2 text-sm font-medium bg-teal-500 text-white hover:bg-teal-600"
        >
          +
        </button>
      )}
    </div>
  </div>
)}
<div className="flex flex-wrap gap-2 mt-4">
  {canToggleSwing && (
    <button
    onClick={() =>
    onAction(device.id, "swing_toggle")
  }

      className="rounded-lg px-3 py-2 text-xs font-medium bg-gray-100 text-gray-700 hover:bg-gray-200"
    >
      Swing
    </button>
  )}

  {canCycleMode && (
    <button
    onClick={() =>
    onAction(device.id, "mode_next")
  }
      className="rounded-lg px-3 py-2 text-xs font-medium bg-gray-100 text-gray-700 hover:bg-gray-200"
    >
      Mode
    </button>
  )}
</div>
        </motion.div>
      )}

      {/* Status */}
      <div className="flex items-center gap-1.5 mt-3">
        <div
          className={`h-1.5 w-1.5 rounded-full ${
            isActive ? "bg-teal-500" : "bg-gray-400"
          }`}
        />

        <span className="text-[11px] text-gray-500">
          {device.uiState.status}
        </span>
      </div>
    </motion.div>
  );
}
