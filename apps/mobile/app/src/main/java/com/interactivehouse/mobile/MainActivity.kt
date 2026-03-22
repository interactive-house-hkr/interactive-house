package com.interactivehouse.mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import com.interactivehouse.mobile.ui.screens.DeviceListScreen
import com.interactivehouse.mobile.ui.screens.LoginScreen
import com.interactivehouse.mobile.ui.theme.MobileTheme


class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        var showDeviceList by mutableStateOf(false)

        setContent {
            MobileTheme {
                if (showDeviceList) {
                    DeviceListScreen()
                } else {
                    LoginScreen(
                        onLogin = { _, _ -> showDeviceList = true },
                        onGoToSignup = { }
                    )
                }
            }
        }
    }
}
