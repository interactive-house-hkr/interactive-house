package com.interactivehouse.mobile.data

/**
 * When true, [com.interactivehouse.mobile.data.repository.DeviceRepository] serves fake devices
 * and applies commands in memory. Set to false to use the real Retrofit backend.
 */
object DemoModeConfig {
    //const val USE_DEMO_MODE: Boolean = true
    const val USE_DEMO_MODE: Boolean = false
}
