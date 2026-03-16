package com.interactivehouse.mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.interactivehouse.mobile.ui.screens.AuthScreen
import com.interactivehouse.mobile.ui.theme.MobileTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            MobileTheme {
                AuthScreen(
                    onLogin = { username, password ->
                        // login logic later
                    },
                    onSignup = { username, email, password ->
                        // signup logic later
                        println("Signup pressed: $username $email")
                    }
                )
            }
        }
    }
}
