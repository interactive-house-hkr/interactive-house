package com.interactivehouse.mobile.data.api

import com.interactivehouse.mobile.data.model.Device
import retrofit2.http.GET
import retrofit2.http.Path

interface DeviceApi {
    // To return a list of devices
    @GET("devices")
    suspend fun getDevices(): List<Device>

    @GET("devices/{uuid}")
    suspend fun getDevice(
        @Path("uuid") uuid: String
    ): Device
}
