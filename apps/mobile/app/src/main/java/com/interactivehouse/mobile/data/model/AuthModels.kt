package com.interactivehouse.mobile.data.model

import com.google.gson.annotations.SerializedName

data class SignupRequest(
    val username: String,
    val email: String,
    val password: String
)

data class SignupResponse(
    val status: String,

    @SerializedName("user_id")
    val userId: String?,

    @SerializedName("access_token")
    val token: String?,

    @SerializedName("refresh_token")
    val refreshToken: String?
)

data class LoginRequest(
    val username: String,
    val password: String,
)

data class LoginResponse(
    val status: String,

    @SerializedName("access_token")
    val token: String?,

    @SerializedName("user_id")
    val userId: String?,

    @SerializedName("refresh_token")
    val refreshToken: String?
)