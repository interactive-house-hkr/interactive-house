package com.interactivehouse.mobile.ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp

@Composable
fun LoginForm(
    onLogin: (String, String) -> Unit,
    isLoading: Boolean = false
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
        placeholder = { Text("Enter username") },
        singleLine = true,
        enabled = !isLoading,
        shape = RoundedCornerShape(18.dp),
        modifier = Modifier.fillMaxWidth(),
        colors = OutlinedTextFieldDefaults.colors(
            focusedContainerColor = Color(0xFFF3F4F6),
            unfocusedContainerColor = Color(0xFFF3F4F6),
            focusedBorderColor = Color(0xFFE5E7EB),
            unfocusedBorderColor = Color(0xFFE5E7EB)
        )
    )

    Spacer(modifier = Modifier.height(12.dp))

    OutlinedTextField(
        value = password,
        onValueChange = {
            password = it
            errorMessage = ""
        },
        label = { Text("Password") },
        placeholder = { Text("Enter password") },
        visualTransformation = PasswordVisualTransformation(),
        singleLine = true,
        enabled = !isLoading,
        shape = RoundedCornerShape(18.dp),
        modifier = Modifier.fillMaxWidth(),
        colors = OutlinedTextFieldDefaults.colors(
            focusedContainerColor = Color(0xFFF3F4F6),
            unfocusedContainerColor = Color(0xFFF3F4F6),
            focusedBorderColor = Color(0xFFE5E7EB),
            unfocusedBorderColor = Color(0xFFE5E7EB)
        )
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
            val trimmedUsername = username.trim()

            if (trimmedUsername.isBlank() || password.isBlank()) {
                errorMessage = "Please enter username and password"
            } else {
                onLogin(trimmedUsername, password)
            }
        },
        enabled = !isLoading,
        modifier = Modifier
            .fillMaxWidth()
            .height(54.dp),
        shape = RoundedCornerShape(18.dp)
    ) {
        Text(if (isLoading) "Logging in..." else "Login")
    }
}