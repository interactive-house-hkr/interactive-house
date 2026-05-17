package com.interactivehouse.mobile.data.mock

import com.interactivehouse.mobile.data.api.DeviceApi
import com.interactivehouse.mobile.data.model.CapabilitySpec
import com.interactivehouse.mobile.data.model.Device
import kotlin.collections.iterator

/**
 * In-memory device list and command handling for demo mode.
 * Thread-safe for coroutine access from the repository.
 */
object DemoDeviceStore {

    private val lock = Any()
    private val devices: MutableList<Device> =
        FakeDevices.seedDevices().map { it.copyForMutation() }.toMutableList()

    fun snapshot(): List<Device> = synchronized(lock) {
        devices.map { it.copyForMutation() }
    }

    fun getDevice(uuid: String): Device? = synchronized(lock) {
        devices.find { it.deviceUuid == uuid }?.copyForMutation()
    }

    /**
     * Validates [patch] keys against writable capabilities, merges into local state,
     * and returns a response in the same shape as the real API.
     */
    fun applyStatePatch(uuid: String, patch: Map<String, Any>): DeviceApi.StateCommandResponse {
        if (patch.isEmpty()) {
            return DeviceApi.StateCommandResponse(
                status = "error",
                error = "invalid_state",
                message = "empty state patch"
            )
        }
        synchronized(lock) {
            val index = devices.indexOfFirst { it.deviceUuid == uuid }
            if (index < 0) {
                return DeviceApi.StateCommandResponse(
                    status = "error",
                    error = "not_found",
                    message = "Device not found"
                )
            }
            val device = devices[index]
            val caps = device.capabilitiesOrEmpty

            for ((key, raw) in patch) {
                val spec = caps[key]
                    ?: return DeviceApi.StateCommandResponse(
                        status = "error",
                        error = "unknown_capability",
                        message = "Unknown capability: $key"
                    )
                if (!spec.writable) {
                    return DeviceApi.StateCommandResponse(
                        status = "error",
                        error = "read_only",
                        message = "Capability is not writable: $key"
                    )
                }
                val coerced = coerceValue(raw, spec)
                    ?: return DeviceApi.StateCommandResponse(
                        status = "error",
                        error = "invalid_state",
                        message = "Invalid value for $key"
                    )
                if (!validateRange(coerced, spec)) {
                    return DeviceApi.StateCommandResponse(
                        status = "error",
                        error = "invalid_state",
                        message = "Value out of range for $key"
                    )
                }
            }
            val newState = LinkedHashMap<String, Any>(device.stateOrEmpty)
            for ((key, raw) in patch) {
                val spec = caps.getValue(key)
                newState[key] = coerceValue(raw, spec)!!
            }
            val updated = device.copy(state = newState)
            devices[index] = updated
            val responseState = LinkedHashMap<String, Any>()
            for (key in patch.keys) {
                responseState[key] = newState[key]!!
            }
            return DeviceApi.StateCommandResponse(
                status = "success",
                state = responseState
            )
        }
    }

    private fun coerceValue(raw: Any, spec: CapabilitySpec): Any? {
        return when (spec.type) {
            "boolean" -> when (raw) {
                is Boolean -> raw
                else -> null
            }
            "integer" -> when (raw) {
                is Int -> raw
                is Number -> raw.toInt()
                else -> null
            }
            else -> null
        }
    }

    private fun validateRange(value: Any, spec: CapabilitySpec): Boolean {
        if (spec.type != "integer") return true
        val v = (value as? Number)?.toInt() ?: return false
        val min = spec.min
        val max = spec.max
        if (min != null && v < min) return false
        if (max != null && v > max) return false
        return true
    }

    private fun Device.copyForMutation(): Device =
        copy(
            capabilities = LinkedHashMap(capabilitiesOrEmpty),
            state = LinkedHashMap(stateOrEmpty)
        )
}