export type Device = {
  device_uuid: string;
  name: string;
  room: string;
  type: string;

  capabilities?: {
    power?: {
      type: string;
      writable: boolean;
    };
    brightness?: {
      type: string;
      min: number;
      max: number;
      writable: boolean;
    };
  };

  state: {
    power: boolean;
    brightness?: number;
  };
};