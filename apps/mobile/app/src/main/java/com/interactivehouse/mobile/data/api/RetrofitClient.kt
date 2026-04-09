package com.interactivehouse.mobile.data.api

import android.content.Context
import com.interactivehouse.mobile.data.repository.TokenManager
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object RetrofitClient {

    // Use local when you run the backend on your machine:
    // private const val BASE_URL = "http://10.0.2.2:8000/api/v1/"

    // Use ngrok when the backend has been started:
    private const val BASE_URL = "https://knolly-svetlana-beribboned.ngrok-free.dev/api/v1/"

    lateinit var tokenManager: TokenManager

    fun init(context: Context) {
        tokenManager = TokenManager(context)
    }

    // Print every network request and response in Android log
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    private val httpClient by lazy {
        OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .addInterceptor(AuthInterceptor(tokenManager))
            .build()
    }

    private val retrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(httpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    val deviceApi: DeviceApi by lazy {
        retrofit.create(DeviceApi::class.java)
    }

    val authApi: AuthApi by lazy {
        retrofit.create(AuthApi::class.java)
    }
}