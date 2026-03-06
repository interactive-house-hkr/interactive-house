package com.interactivehouse.mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.interactivehouse.mobile.ui.screens.LoginScreen
import com.interactivehouse.mobile.ui.theme.MobileTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            MobileTheme {
                LoginScreen(
                    onLogin = { _, _ -> },
                    onGoToSignup = { }
                )
            }
        }
    }
}
