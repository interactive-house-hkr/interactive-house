package com.interactivehouse.mobile.ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp

@Composable
fun LoginForm(
    onLogin: (String, String) -> Unit
) {
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var errorMessage by remember { mutableStateOf("") }

    OutlinedTextField(
        value = username,
        onValueChange = {
            username = it
            errorMessage = ""
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
        visualTransformation = PasswordVisualTransformation(),
        modifier = Modifier.fillMaxWidth()
    )

    Spacer(modifier = Modifier.height(12.dp))

    if (errorMessage.isNotEmpty()) {
        Text(
            text = errorMessage,
            color = MaterialTheme.colorScheme.error
        )
        Spacer(modifier = Modifier.height(12.dp))
    }

    Button(
        onClick = {
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
}