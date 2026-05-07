package com.interactivehouse.mobile.data.mock

import com.interactivehouse.mobile.data.model.CapabilitySpec
import com.interactivehouse.mobile.data.model.Device

/**
 * Seed data matching the /api/v1 devices contract (capabilities + state).
 */
object FakeDevices {

    fun seedDevices(): List<Device> = listOf(demoLight(), demoFan())

    private fun demoLight(): Device = Device(
        deviceUuid = "demo-light-001",
        name = "Living Room Lamp",
        room = "Living Room",
        type = "light",
        capabilities = mapOf(
            "power" to CapabilitySpec(type = "boolean", writable = true),
            "brightness" to CapabilitySpec(type = "integer", writable = true, min = 0, max = 100)
        ),
        state = mapOf(
            "power" to false,
            "brightness" to 50
        )
    )

    private fun demoFan(): Device = Device(
        deviceUuid = "demo-fan-001",
        name = "Bedroom Fan",
        room = "Bedroom",
        type = "fan",
        capabilities = mapOf(
            "power" to CapabilitySpec(type = "boolean", writable = true),
            "speed" to CapabilitySpec(type = "integer", writable = true, min = 0, max = 3)
        ),
        state = mapOf(
            "power" to true,
            "speed" to 1
        )
    )
}
