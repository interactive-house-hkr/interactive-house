package com.interactivehouse.mobile.data.api

import com.interactivehouse.mobile.data.model.LoginRequest
import com.interactivehouse.mobile.data.model.LoginResponse
import com.interactivehouse.mobile.data.model.SignupRequest
import com.interactivehouse.mobile.data.model.SignupResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST

interface AuthApi {

    @POST("auth/register")
    suspend fun signup(
        @Body request: SignupRequest
    ): Response<SignupResponse>

    @POST("auth/login")
    suspend fun login(
        @Body request: LoginRequest
    ): Response<LoginResponse>
}