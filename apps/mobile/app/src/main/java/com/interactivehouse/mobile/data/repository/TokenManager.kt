package com.interactivehouse.mobile.data.repository

import android.content.Context

class TokenManager(context: Context) {

    private val prefs = context.getSharedPreferences(
        "auth_prefs",
        Context.MODE_PRIVATE
    )

    fun saveToken(token: String) {
        prefs.edit().putString("auth_token", token).apply()
    }

    fun getToken(): String? {
        return prefs.getString("auth_token", null)
    }

    fun clearToken() {
        prefs.edit().remove("auth_token").apply()
    }
}