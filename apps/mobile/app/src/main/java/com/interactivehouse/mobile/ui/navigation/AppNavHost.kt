package com.interactivehouse.mobile.ui.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.navigation
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.interactivehouse.mobile.data.api.RetrofitClient
import com.interactivehouse.mobile.data.repository.AuthRepository
import com.interactivehouse.mobile.data.repository.TokenManager
import com.interactivehouse.mobile.ui.screens.AuthScreen
import com.interactivehouse.mobile.ui.screens.DeviceDetailScreen
import com.interactivehouse.mobile.ui.screens.DeviceListScreen
import com.interactivehouse.mobile.viewmodel.DeviceListViewModel
import kotlinx.coroutines.launch

object NavRoutes {
    const val Auth = "auth"
    const val Login = Auth
    const val DevicesGraph = "devices_graph"
    const val DeviceList = "device_list"
    const val DeviceDetail = "device_detail"
    const val DeviceDetailPattern = "device_detail/{uuid}"
}

@Composable
fun AppNavHost(
    modifier: Modifier = Modifier,
    navController: NavHostController = rememberNavController()
) {
    val context = LocalContext.current
    val tokenManager = remember { TokenManager(context) }
    val authRepository = remember {
        AuthRepository(
            RetrofitClient.authApi,
            tokenManager
        )
    }
    val scope = rememberCoroutineScope()

    var authMessage by remember { mutableStateOf<String?>(null) }
    var isLoading by remember { mutableStateOf(false) }

    NavHost(
        navController = navController,
        startDestination = NavRoutes.Auth,
        //startDestination = NavRoutes.DevicesGraph,
        modifier = modifier
    ) {
        composable(NavRoutes.Auth) {
            AuthScreen(
                onLogin = { username, password ->
                    authMessage = null
                    isLoading = true

                    scope.launch {
                        try {
                            val result = authRepository.login(username, password)

                            if (result.isSuccess) {
                                navController.navigate(NavRoutes.DevicesGraph) {
                                    popUpTo(NavRoutes.Auth) { inclusive = true }
                                }
                            } else {
                                authMessage =
                                    result.exceptionOrNull()?.message ?: "Login failed"
                            }
                        } finally {
                            isLoading = false
                        }
                    }
                },
                onSignup = { username, email, password ->
                    authMessage = null
                    isLoading = true

                    scope.launch {
                        try {
                            val result = authRepository.signup(username, email, password)

                            if (result.isSuccess) {
                                navController.navigate(NavRoutes.DevicesGraph) {
                                    popUpTo(NavRoutes.Auth) { inclusive = true }
                                }
                            } else {
                                authMessage =
                                    result.exceptionOrNull()?.message ?: "Signup failed"
                            }
                        } finally {
                            isLoading = false
                        }
                    }
                },
                authMessage = authMessage,
                isLoading = isLoading,
                onClearMessage = {
                    authMessage = null
                    isLoading = false
                }
            )
        }

        navigation(
            route = NavRoutes.DevicesGraph,
            startDestination = NavRoutes.DeviceList
        ) {
            composable(NavRoutes.DeviceList) { entry ->
                val graphEntry = remember(entry) {
                    navController.getBackStackEntry(NavRoutes.DevicesGraph)
                }
                val vm: DeviceListViewModel = viewModel(graphEntry)

                LaunchedEffect(Unit) {
                    vm.loadDevices(showLoading = true)
                    vm.startPeriodicRefresh()
                }

                DeviceListScreen(
                    viewModel = vm,
                    onDeviceClick = { device ->
                        navController.navigate("${NavRoutes.DeviceDetail}/${device.deviceUuid}")
                    },
                    onLogout = {
                        RetrofitClient.tokenManager.clearToken()
                        navController.navigate(NavRoutes.Login) {
                            popUpTo(NavRoutes.DevicesGraph) { inclusive = true }
                        }
                    }
                )
            }

            composable(
                route = NavRoutes.DeviceDetailPattern,
                arguments = listOf(
                    navArgument("uuid") { type = NavType.StringType }
                )
            ) { entry ->
                val graphEntry = remember(entry) {
                    navController.getBackStackEntry(NavRoutes.DevicesGraph)
                }
                val vm: DeviceListViewModel = viewModel(graphEntry)
                val uuid = entry.arguments?.getString("uuid").orEmpty()

                DeviceDetailScreen(
                    deviceUuid = uuid,
                    viewModel = vm,
                    onBack = { navController.popBackStack() }
                )
            }
        }
    }
}
