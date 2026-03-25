package com.interactivehouse.mobile.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.runtime.Composable
import androidx.compose.ui.text.input.PasswordVisualTransformation

@Composable
fun LoginScreen(
    onLogin: (String, String) -> Unit,
    onGoToSignup: () -> Unit
) {
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }

    // Ny state för felmeddelande
    var errorMessage by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "Login",
            style = MaterialTheme.typography.headlineMedium
        )

        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = username,
            onValueChange = {
                username = it
                errorMessage = "" // rensa fel när man skriver
            },
            label = { Text("Username") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(12.dp))

        OutlinedTextField(
            value = password,
            onValueChange = {
                password = it
                errorMessage = ""
            },
            label = { Text("Password") },
            visualTransformation = PasswordVisualTransformation(), // 🔹 döljer lösenord
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(12.dp))

        // Visa felmeddelande om något saknas
        if (errorMessage.isNotEmpty()) {
            Text(
                text = errorMessage,
                color = MaterialTheme.colorScheme.error
            )

            Spacer(modifier = Modifier.height(12.dp))
        }

        Spacer(modifier = Modifier.height(8.dp))

        Button(
            onClick = {

                // 🔹 Enkel validering
                if (username.isBlank() || password.isBlank()) {
                    errorMessage = "Please enter username and password"
                } else {
                    onLogin(username, password)
                }

            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Login")
        }

        Spacer(modifier = Modifier.height(12.dp))

        TextButton(
            onClick = { onGoToSignup() }
        ) {
            Text("No account? Sign up")
        }
    }
}