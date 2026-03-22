package com.interactivehouse.mobile.data.model

/**
 * Represents a smart device from the backend API.
 * Capabilities are optional; the API may include them for lights, sensors, etc.
 */
data class Device(
    val deviceUuid: String,
    val type: String,
    val capabilities: Map<String, CapabilitySpec>? = null
)

/**
 * Describes a device capability (e.g. "power": { "type": "boolean", "writable": true }).
 */
data class CapabilitySpec(
    val type: String? = null,
    val writable: Boolean? = null
)