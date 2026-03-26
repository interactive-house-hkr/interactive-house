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
fun SignupForm(
    onSignup: (String, String, String) -> Unit
) {
    var username by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var confirmPassword by remember { mutableStateOf("") }

    var errorMessage by remember { mutableStateOf("") }

    val textFieldColors = OutlinedTextFieldDefaults.colors(
        focusedContainerColor = Color(0xFFF3F4F6),
        unfocusedContainerColor = Color(0xFFF3F4F6),
        focusedBorderColor = Color(0xFFE5E7EB),
        unfocusedBorderColor = Color(0xFFE5E7EB)
    )

    OutlinedTextField(
        value = username,
        onValueChange = {
            username = it
            errorMessage = ""
        },
        label = { Text("Username") },
        placeholder = { Text("Enter username") },
        singleLine = true,
        shape = RoundedCornerShape(18.dp),
        modifier = Modifier.fillMaxWidth(),
        colors = textFieldColors
    )

    Spacer(modifier = Modifier.height(12.dp))

    OutlinedTextField(
        value = email,
        onValueChange = {
            email = it
            errorMessage = ""
        },
        label = { Text("Email") },
        placeholder = { Text("Enter email") },
        singleLine = true,
        shape = RoundedCornerShape(18.dp),
        modifier = Modifier.fillMaxWidth(),
        colors = textFieldColors
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
        shape = RoundedCornerShape(18.dp),
        modifier = Modifier.fillMaxWidth(),
        colors = textFieldColors
    )

    Spacer(modifier = Modifier.height(12.dp))

    OutlinedTextField(
        value = confirmPassword,
        onValueChange = {
            confirmPassword = it
            errorMessage = ""
        },
        label = { Text("Confirm Password") },
        placeholder = { Text("Confirm password") },
        visualTransformation = PasswordVisualTransformation(),
        singleLine = true,
        shape = RoundedCornerShape(18.dp),
        modifier = Modifier.fillMaxWidth(),
        colors = textFieldColors
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
            val trimmedEmail = email.trim()

            if (trimmedUsername.isBlank() || trimmedEmail.isBlank() || password.isBlank() || confirmPassword.isBlank()) {
                errorMessage = "Please fill in all fields"
                return@Button
            }

            if (!trimmedEmail.contains("@") || !trimmedEmail.contains(".")) {
                errorMessage = "Please enter a valid email"
                return@Button
            }

            if (password.length < 6) {
                errorMessage = "Password must be at least 6 characters"
                return@Button
            }

            if (password != confirmPassword) {
                errorMessage = "Passwords do not match"
                return@Button
            }

            onSignup(trimmedUsername, trimmedEmail, password)
        },
        modifier = Modifier
            .fillMaxWidth()
            .height(54.dp),
        shape = RoundedCornerShape(18.dp)
    ) {
        Text("Sign Up")
    }
}