package com.interactivehouse.mobile.data.repository

import android.util.Log
import com.interactivehouse.mobile.data.api.AuthApi
import com.interactivehouse.mobile.data.model.LoginRequest
import com.interactivehouse.mobile.data.model.SignupRequest
import org.json.JSONObject

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
                Log.d("AUTH_DEBUG", "Signup body: ${response.body()}")

                val token = response.body()?.token
                if (!token.isNullOrBlank()) {
                    tokenManager.saveToken(token)
                    Result.success(token)
                } else {
                    Result.failure(Exception("Signup succeeded but no token returned"))
                }
            } else {
                val errorBody = response.errorBody()?.string()
                Log.d("AUTH_DEBUG", "Signup error code: ${response.code()}")
                Log.d("AUTH_DEBUG", "Signup error body: $errorBody")

                val message = parseErrorMessage(errorBody, "Signup failed (${response.code()})")
                Result.failure(Exception(message))
            }

        } catch (e: Exception) {
            Result.failure(Exception("Network error: ${e.message}"))
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
                    tokenManager.saveToken(token)
                    Result.success(token)
                } else {
                    Result.failure(Exception("Login succeeded but no token returned"))
                }
            } else {
                val errorBody = response.errorBody()?.string()

                val message = parseErrorMessage(errorBody, "Login failed (${response.code()})")
                Result.failure(Exception(message))
            }

        } catch (e: Exception) {
            Result.failure(Exception("Network error: ${e.message}"))
        }
    }

    private fun parseErrorMessage(errorBody: String?, fallback: String): String {
        return try {
            val json = JSONObject(errorBody ?: "")
            val detail = json.optString("detail")

            when {
                detail.contains("exists", true) -> "User already exists"
                detail.contains("invalid", true) -> "Invalid username or password"
                detail.isNotBlank() -> detail
                else -> fallback
            }
        } catch (e: Exception) {
            fallback
        }
    }
}