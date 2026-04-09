package com.interactivehouse.mobile.data.repository

import com.interactivehouse.mobile.data.api.AuthApi
import com.interactivehouse.mobile.data.model.LoginRequest
import com.interactivehouse.mobile.data.model.SignupRequest

class AuthRepository(
    private val authApi: AuthApi,
    private val tokenManager: TokenManager
) {
    suspend fun signup(
        username: String,
        email: String,
        password: String
    ): Result<String> {
        return try {
            val response = authApi.signup(
                SignupRequest(
                    username = username,
                    email = email,
                    password = password
                )
            )

            if (response.isSuccessful) {
                val token = response.body()?.token
                if (!token.isNullOrBlank()) {
                    tokenManager.saveToken(token) //  save token
                    Result.success(token)
                } else {
                    Result.failure(Exception("Token missing in response"))
                }
            } else {
                Result.failure(Exception("Signup failed: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun login(
        username: String,
        password: String
    ): Result<String> {
        return try {
            val response = authApi.login(
                LoginRequest(
                    username = username,
                    password = password
                )
            )

            if (response.isSuccessful) {
                val token = response.body()?.token
                if (!token.isNullOrBlank()) {
                    tokenManager.saveToken(token) // save token
                    Result.success(token)
                } else {
                    Result.failure(Exception("Token missing in response"))
                }
            } else {
                Result.failure(Exception("Login failed: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}