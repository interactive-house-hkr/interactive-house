package com.interactivehouse.mobile.data.mock

import com.interactivehouse.mobile.data.model.CapabilitySpec
import com.interactivehouse.mobile.data.model.Device

object FakeDevices {

    fun seedDevices(): List<Device> = listOf(
        demoLight("Kitchen Light", "Kitchen", "demo-light-2", true, power = true),
        demoFan("Office Fan", "Office", "demo-fan-1", true, power = true),
        demoLight("Hallway Light", "Hallway", "demo-light-3", true, power = false),
        demoThermostat("Bedroom Thermostat", "Bedroom", "demo-therm-1", true)      // No power cap
    )

    private fun demoLight(name: String, room: String, uuid: String, isOnline: Boolean, power: Boolean): Device = Device(
        deviceUuid = uuid,
        name = name,
        room = room,
        type = "light",
        capabilities = mapOf(
            "power" to CapabilitySpec(type = "boolean", writable = true),
            "brightness" to CapabilitySpec(type = "integer", writable = true, min = 0, max = 100)
        ),
        state = mapOf(
            "power" to power,
            "brightness" to 75
        )
    )

    private fun demoThermostat(name: String, room: String, uuid: String, isOnline: Boolean): Device = Device(
        deviceUuid = uuid,
        name = name,
        room = room,
        type = "thermostat",
        capabilities = mapOf(
            "temperature" to CapabilitySpec(type = "integer", writable = true, min = 16, max = 30)
        ),
        state = mapOf(
            "temperature" to 22
        )
    )

    private fun demoFan(name: String, room: String, uuid: String, isOnline: Boolean, power: Boolean): Device = Device(
        deviceUuid = uuid,
        name = name,
        room = room,
        type = "fan",
        capabilities = mapOf(
            "power" to CapabilitySpec(type = "boolean", writable = true),
            "speed" to CapabilitySpec(type = "integer", writable = true, min = 0, max = 3)
        ),
        state = mapOf(
            "power" to power,
            "speed" to 0
        )
    )
}
