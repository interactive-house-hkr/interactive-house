package com.interactivehouse.mobile.data.repository

import com.interactivehouse.mobile.data.api.RetrofitClient
import com.interactivehouse.mobile.data.model.Device

//wrap API calls, repository is the single place reponsible for data
class DeviceRepository {
    suspend fun getDevices(): List<Device> {
        return RetrofitClient.deviceApi.getDevices()
    }

    suspend fun getDevice(uuid: String): Device {
        return RetrofitClient.deviceApi.getDevice(uuid)
    }
}