package com.interactivehouse.mobile.ui.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.navigation
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.interactivehouse.mobile.ui.screens.DeviceDetailScreen
import com.interactivehouse.mobile.ui.screens.DeviceListScreen
import com.interactivehouse.mobile.ui.screens.LoginScreen
import com.interactivehouse.mobile.ui.screens.SignupPlaceholderScreen
import com.interactivehouse.mobile.viewmodel.DeviceListViewModel

object NavRoutes {
    const val Login = "login"
    const val SignupPlaceholder = "signup_placeholder"
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
    NavHost(
        navController = navController,
        startDestination = NavRoutes.Login,
        modifier = modifier
    ) {
        composable(NavRoutes.Login) {
            LoginScreen(
                onLogin = { _, _ ->
                    // Navigation-only hook: LoginScreen already validated non-blank fields.
                    // Teammate-owned auth can later gate this navigate call without changing LoginScreen UI.
                    navController.navigate(NavRoutes.DevicesGraph) {
                        popUpTo(NavRoutes.Login) { inclusive = true }
                    }
                },
                onGoToSignup = {
                    navController.navigate(NavRoutes.SignupPlaceholder)
                }
            )
        }
        composable(NavRoutes.SignupPlaceholder) {
            SignupPlaceholderScreen(onBack = { navController.popBackStack() })
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
                LaunchedEffect(Unit) {
                    vm.startPeriodicRefresh()
                }
                DeviceDetailScreen(
                    deviceUuid = uuid,
                    viewModel = vm,
                    onBack = { navController.popBackStack() }
                )
            }
        }
    }
}

