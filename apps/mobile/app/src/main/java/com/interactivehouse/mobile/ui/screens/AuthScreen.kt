package com.interactivehouse.mobile.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.interactivehouse.mobile.ui.components.LoginForm
import com.interactivehouse.mobile.ui.components.SignupForm

@Composable
fun AuthScreen(
    onLogin: (String, String) -> Unit,
    onSignup: (String, String, String) -> Unit
) {
    var isLoginMode by remember { mutableStateOf(true) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = if (isLoginMode) "Login" else "Sign Up",
            style = MaterialTheme.typography.headlineMedium
        )

        Spacer(modifier = Modifier.height(16.dp))

        if (isLoginMode) {
            LoginForm(onLogin = onLogin)
        } else {
            SignupForm(onSignup = onSignup)
        }

        Spacer(modifier = Modifier.height(12.dp))

        TextButton(
            onClick = { isLoginMode = !isLoginMode }
        ) {
            Text(
                if (isLoginMode) "No account? Sign up"
                else "Already have an account? Login"
            )
        }
    }
}