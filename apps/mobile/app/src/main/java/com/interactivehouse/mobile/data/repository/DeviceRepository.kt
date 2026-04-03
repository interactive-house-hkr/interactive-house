package com.interactivehouse.mobile.data.repository

import com.interactivehouse.mobile.data.DemoModeConfig
import com.interactivehouse.mobile.data.api.DeviceApi
import com.interactivehouse.mobile.data.api.RetrofitClient
import com.interactivehouse.mobile.data.mock.DemoDeviceStore
import com.interactivehouse.mobile.data.model.Device

/*
* Repository for interacting with the device API.*/
class DeviceRepository(
    private val api: DeviceApi = RetrofitClient.deviceApi,
    private val demoStore: DemoDeviceStore = DemoDeviceStore
) {

    /**
     * Fetches all devices from the API/server.
     * Calls:
     * GET /api/v1/devices
     */
    suspend fun getDevices(): List<Device> {
        return if (DemoModeConfig.USE_DEMO_MODE) {
            demoStore.snapshot()
        } else {
            api.getDevices()
        }
    }

    //Fetch a single device by UUID
    suspend fun getDevice(uuid: String): Device {
        return if (DemoModeConfig.USE_DEMO_MODE) {
            demoStore.getDevice(uuid)
                ?: throw NoSuchElementException("Device not found: $uuid")
        } else {
            api.getDevice(uuid)
        }
    }

    // send a command to a device
    /* @param uuid Device ID (e.g. "light-1")
     * @param state State payload for the command (partial state map)
     *
     * Calls:
     * POST /api/v1/devices/{uuid}/commands
     */
    suspend fun sendCommand(
        uuid: String,
        state: Map<String, Any>
    ): DeviceApi.StateCommandResponse {
        return if (DemoModeConfig.USE_DEMO_MODE) {
            demoStore.applyStatePatch(uuid, state)
        } else {
            api.sendCommand(
                uuid,
                DeviceApi.StateCommandRequest(state)
            )
        }
    }
}
