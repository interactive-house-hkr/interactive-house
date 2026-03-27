import { Device } from "../types/device";

type Props = {
  device: Device;
  onToggle: (deviceUuid: string) => void;
};

export default function DeviceCard({ device, onToggle }: Props) {
  return (
    <div
      style={{
        borderRadius: "16px",
        padding: "1.5rem",
        backgroundColor: "#ffffff",
        boxShadow: "0 4px 16px rgba(0,0,0,0.06)",
        transition: "0.2s",
      }}
    >
      <h2 style={{ marginBottom: "0.8rem", fontSize: "1.2rem" }}>
        {device.name}
      </h2>

      <p>
        <strong>Room:</strong> {device.room}
      </p>

      <p>
        <strong>Type:</strong> {device.type}
      </p>

      <p>
        <strong>Status:</strong>{" "}
        <span style={{ color: device.state.power ? "green" : "red" }}>
          {device.state.power ? "On" : "Off"}
        </span>
      </p>

      {device.type === "light" && (
        <button
          onClick={() => onToggle(device.device_uuid)}
          style={{
            marginTop: "1rem",
            padding: "0.6rem 1rem",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
            backgroundColor: device.state.power ? "#222" : "#ddd",
            color: device.state.power ? "#fff" : "#000",
          }}
        >
          Turn {device.state.power ? "Off" : "On"}
        </button>
      )}
    </div>
  );
}