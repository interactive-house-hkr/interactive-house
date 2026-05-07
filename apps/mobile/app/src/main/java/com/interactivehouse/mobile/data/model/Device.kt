package com.interactivehouse.mobile.data.model

import com.google.gson.annotations.SerializedName

/**
 * Represents a smart device from the backend API.
 * Capabilities are optional; the API may include them for lights, sensors, etc.
 */
data class Device(
    @SerializedName("device_uuid")
    val deviceUuid: String,
    val name: String?,
    val room: String?,
    val type: String,
    val capabilities: Map<String, CapabilitySpec>,
    val state: Map<String, Any>? = emptyMap()
) {
    val stateOrEmpty: Map<String, Any>
        get() = state.orEmpty()
}

/**
 * Describes a device capability (e.g. "power": { "type": "boolean", "writable": true }).
 */
data class CapabilitySpec(
    val type: String,
    val writable: Boolean,
    val min: Int? = null,
    val max: Int? = null
)
