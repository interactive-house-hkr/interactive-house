package com.interactivehouse.mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.*
import com.interactivehouse.mobile.data.api.RetrofitClient
import com.interactivehouse.mobile.data.repository.AuthRepository
import com.interactivehouse.mobile.data.repository.TokenManager
import com.interactivehouse.mobile.ui.screens.AuthScreen
import com.interactivehouse.mobile.ui.screens.DeviceListScreen
import com.interactivehouse.mobile.ui.theme.MobileTheme
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        RetrofitClient.init(applicationContext)
        val tokenManager = TokenManager(applicationContext)

        setContent {
            MobileTheme {
                var showDeviceList by remember { mutableStateOf(false) }
                var authMessage by remember { mutableStateOf<String?>(null) }
                var isLoading by remember { mutableStateOf(false) }

                val scope = rememberCoroutineScope()

                val authRepository = remember {
                    AuthRepository(
                        RetrofitClient.authApi,
                        tokenManager
                    )
                }

                if (showDeviceList) {
                    DeviceListScreen()
                } else {
                    AuthScreen(
                        onLogin = { username, password ->
                            authMessage = null
                            isLoading = true

                            scope.launch {
                                try {
                                    val result = authRepository.login(username, password)

                                    if (result.isSuccess) {
                                        authMessage = "Login successful"
                                        showDeviceList = true
                                    } else {
                                        authMessage = result.exceptionOrNull()?.message ?: "Login failed"
                                    }
                                } finally {
                                    isLoading = false
                                }
                            }
                        },
                        onSignup = { username, email, password ->
                            authMessage = null
                            isLoading = true

                            scope.launch {
                                try {
                                    val result = authRepository.signup(username, email, password)

                                    if (result.isSuccess) {
                                        authMessage = "Signup successful"
                                        showDeviceList = true
                                    } else {
                                        authMessage = result.exceptionOrNull()?.message ?: "Signup failed"
                                    }
                                } finally {
                                    isLoading = false
                                }
                            }
                        },
                        authMessage = authMessage,
                        isLoading = isLoading,
                        onClearMessage = {
                            authMessage = null
                            isLoading = false
                        }
                    )
                }
            }
        }
    }
}