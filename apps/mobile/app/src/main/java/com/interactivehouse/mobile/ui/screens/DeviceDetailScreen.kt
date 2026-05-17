package com.interactivehouse.mobile.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.DeviceUnknown
import androidx.compose.material.icons.filled.Lightbulb
import androidx.compose.material.icons.filled.Thermostat
import androidx.compose.material.icons.filled.WindPower
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.interactivehouse.mobile.data.DemoModeConfig
import com.interactivehouse.mobile.data.model.Device
import com.interactivehouse.mobile.ui.device.DeviceCapabilityControls
import com.interactivehouse.mobile.ui.theme.*
import com.interactivehouse.mobile.viewmodel.DeviceListViewModel

/**
 * Detailed view for a specific device.
 * Allows users to toggle power and adjust settings like brightness or temperature.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DeviceDetailScreen(
    deviceUuid: String,
    viewModel: DeviceListViewModel,
    onBack: () -> Unit //callback to return to list screen
) {

    // Observe the list of device
    val devices by viewModel.devices.collectAsState()
    val isCommandInFlight by viewModel.isCommandInFlight.collectAsState()

    // When the screen opens (or the device ID changes), refresh the data
    LaunchedEffect(deviceUuid) {
        viewModel.loadDevices(showLoading = false)
        viewModel.startPeriodicRefresh()
    }
    // Clean things up when the user leave the screen
    DisposableEffect(Unit) {
        onDispose {
            viewModel.stopPeriodicRefresh()
        }
    }

    val device = devices.find { it.deviceUuid == deviceUuid }

    // Find the specific device object from the current list using the UUID
    Scaffold(
        containerColor = BackgroundLight,
        topBar = {
            CenterAlignedTopAppBar(
                colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                    containerColor = Color.Transparent
                ),
                title = {
                    // Display the device name, or fall back to its type if no name exists
                    Text(
                        text = device?.let { d ->
                            d.name?.takeIf { it.isNotBlank() }
                                ?: (d.type ?: "unknown").replaceFirstChar { it.uppercase() }
                        } ?: "Device",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = TextDark
                    )
                },
                navigationIcon = {
                    Surface(
                        onClick = onBack,
                        modifier = Modifier.padding(start = 16.dp),
                        shape = RoundedCornerShape(12.dp),
                        color = Color(0xFFF1F4F8)
                    ) {
                        Box(modifier = Modifier.size(48.dp), contentAlignment = Alignment.Center) {
                            Icon(
                                imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                                contentDescription = "Back",
                                tint = TextDark
                            )
                        }
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = 24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // If device is not available yet, show loading instead of crashing
            if (device == null) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator(color = BrandBlue)
                }
                return@Column
            }

            //visual feedback:
            val isActiveVisual = device.isPoweredOn

            Spacer(modifier = Modifier.height(32.dp))

            // --- Large Hero Icon ---
            val backgroundBrush = if (isActiveVisual) {
                Brush.linearGradient(colors = listOf(BrandBlue, BrandPurple))
            } else {
                Brush.linearGradient(colors = listOf(Color(0xFFE5E7EB), Color(0xFFE5E7EB)))
            }

            Box(
                modifier = Modifier
                    .size(140.dp)
                    .background(
                        brush = backgroundBrush,
                        shape = RoundedCornerShape(40.dp)
                    ),
                contentAlignment = Alignment.Center
            ) {
                DeviceDetailIcon(
                    type = device.type ?: "unknown",
                    tint = if (isActiveVisual) Color.White else TextGrey.copy(alpha = 0.6f)
                )
            }

            Spacer(modifier = Modifier.height(48.dp))

            // --- Control Panel ---

            // Generates switches/sliders
            DeviceCapabilityControls(
                device = device,
                isCommandInFlight = isCommandInFlight,
                //Boolean switches
                onBooleanCapability = { key, value ->
                    viewModel.sendDeviceState(device, mapOf(key to value)) //send new value to server
                },
                //sliders, numbers
                onIntegerCapability = { key, value ->
                    viewModel.setIntegerCapability(device, key, value)
                }
            )

            // ----Reminder for development mode---
            if (DemoModeConfig.USE_DEMO_MODE) {
                Spacer(modifier = Modifier.weight(1f))
                Text(
                    text = "DEMO MODE ACTIVE",
                    style = MaterialTheme.typography.labelSmall,
                    color = BrandPurple.copy(alpha = 0.5f),
                    modifier = Modifier.padding(bottom = 16.dp)
                )
            }
        }
    }
}

/**
 * Selecting correct large icon for the detail view.
 */
@Composable
private fun DeviceDetailIcon(type: String, tint: Color) {
    val icon = when (type.lowercase()) {
        "light", "lamp" -> Icons.Default.Lightbulb
        "fan" -> Icons.Default.WindPower
        "thermostat" -> Icons.Default.Thermostat
        else -> Icons.Default.DeviceUnknown //generic device icon
    }
    Icon(
        imageVector = icon,
        contentDescription = null,
        tint = tint,
        modifier = Modifier.size(56.dp)
    )
}
