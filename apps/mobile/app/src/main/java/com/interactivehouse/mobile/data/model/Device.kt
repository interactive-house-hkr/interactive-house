package com.interactivehouse.mobile.data.model

import com.google.gson.annotations.SerializedName

data class Device(
    @SerializedName("device_uuid")
    val deviceUuid: String,

    val name: String? = null,
    val room: String? = null,
    val type: String? = "unknown",

    val capabilities: Map<String, CapabilitySpec>? = emptyMap(),
    val state: Map<String, Any>? = emptyMap(),

    ) {
    val stateOrEmpty: Map<String, Any>
        get() = state.orEmpty()

    val capabilitiesOrEmpty: Map<String, CapabilitySpec>
        get() = capabilities.orEmpty()

    val isPoweredOn: Boolean
        get() {
            val hasPowerCapability = capabilitiesOrEmpty.containsKey("power")
            return if (hasPowerCapability) {
                (stateOrEmpty["power"] as? Boolean) == true
            } else {
                // active by default, if device doesn't have a power switch
                true
            }
        }

}

data class CapabilitySpec(
    val type: String,
    val writable: Boolean,
    val min: Int? = null,
    val max: Int? = null
)
