package com.interactivehouse.mobile.data.model

data class SignupRequest(
    val username: String,
    val email: String,
    val password: String
)

data class SignupResponse(
    val status: String,
    val userId: String?,
    val token: String?
)

data class LoginRequest(
    val username: String,
    val password: String,
)

data class LoginResponse(
    val status: String,
    val token: String?,
    val userId: String?
)