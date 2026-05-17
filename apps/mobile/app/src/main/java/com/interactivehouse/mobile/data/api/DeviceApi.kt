package com.interactivehouse.mobile.data.api

import com.interactivehouse.mobile.data.model.Device
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

/**
 * This interface defines all HTTP calls related to devices.
 * Retrofit uses this to generate the actual network code.
 */
interface DeviceApi {
    //Fetches all devices from the server.
    @GET("devices")
    suspend fun getDevices(): List<Device>

    // * Fetch a single device by its UUID.
    @GET("devices/{uuid}")
    suspend fun getDevice(
        @Path("uuid") uuid: String // replaces {uuid} in the URL
    ): Device

    @POST("devices/{uuid}/commands")
    suspend fun sendCommand(
        @Path("uuid") uuid: String,
        @Body body: StateCommandRequest
    ): StateCommandResponse

    /**
     * Command request/response for writable capabilities (boolean, integer, etc.).
     *
     * API contract:
     * POST /api/v1/devices/{device_uuid}/commands
     * body: { "state": { "<key>": <value>, ... } }
     */
    data class StateCommandRequest(
        val state: Map<String, @JvmSuppressWildcards Any>
    )

    data class StateCommandResponse(
        val status: String,
        val state: Map<String, @JvmSuppressWildcards Any>? = null,
        val error: String? = null,
        val message: String? = null
    )
}