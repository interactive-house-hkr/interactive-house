package com.interactivehouse.mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.interactivehouse.mobile.data.api.RetrofitClient
import com.interactivehouse.mobile.ui.navigation.AppNavHost
import com.interactivehouse.mobile.ui.theme.MobileTheme

/**
 * Entry activity. Compose UI must be built inside setContent so @Composable calls are valid.
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        RetrofitClient.init(applicationContext)

        setContent {
            MobileTheme {
                AppNavHost()
            }
        }
    }
}