package com.interactivehouse.mobile.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.filled.DeviceUnknown
import androidx.compose.material.icons.filled.ExitToApp
import androidx.compose.material.icons.filled.Lightbulb
import androidx.compose.material.icons.filled.Thermostat
import androidx.compose.material.icons.filled.WindPower
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
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
import com.interactivehouse.mobile.ui.theme.*
import com.interactivehouse.mobile.viewmodel.DeviceListViewModel

/**
 * Main Screen for displaying the list of smart home devices.
 *
 * @param viewModel Handles the business logic and state for this screen.
 * @param onDeviceClick Callback for when a user selects a device to see details.
 * @param onLogout Callback to handle session termination.
 */
@Composable
fun DeviceListScreen(
    viewModel: DeviceListViewModel,
    onDeviceClick: (Device) -> Unit,
    onLogout: () -> Unit
) {

    //observe stateFlows  from Viemodel
    val devices by viewModel.devices.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val errorMessage by viewModel.errorMessage.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundLight)
            .padding(horizontal = 24.dp, vertical = 32.dp)
    ) {
        // Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = "My Devices",
                    fontSize = 28.sp,
                    fontWeight = FontWeight.Bold,
                    color = TextDark
                )
                Text(
                    text = "${devices.size} devices connected",
                    fontSize = 16.sp,
                    color = TextGrey,
                    modifier = Modifier.padding(top = 4.dp)
                )
            }

            //Logout Button
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = Color(0xFFE2E8F0)
            ) {
                IconButton(onClick = onLogout) {
                    Icon(
                        imageVector = Icons.Default.ExitToApp,
                        contentDescription = "Logout",
                        tint = TextDark
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(32.dp))

        // --- Demo Mode Banner ---
        if (DemoModeConfig.USE_DEMO_MODE) {
            Card(
                colors = CardDefaults.cardColors(containerColor = BrandPurple.copy(alpha = 0.1f)),
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp)
            ) {
                Text(
                    text = "Demo Mode Active",
                    color = BrandPurple,
                    style = MaterialTheme.typography.labelSmall,
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                )
            }
        }

        // --- Main Content Area ---
        if (isLoading) {
            // show spinner when data is fetched
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = BrandBlue)
            }
        } else if (devices.isEmpty() && errorMessage == null) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text("No devices found", color = TextGrey)
            }
        } else {
            // Scrollable list of devices
            LazyColumn(
                verticalArrangement = Arrangement.spacedBy(16.dp),
                contentPadding = PaddingValues(bottom = 16.dp)
            ) {
                items(devices, key = { it.deviceUuid }) { device ->
                    DeviceSummaryCard(
                        device = device,
                        onClick = { onDeviceClick(device) }
                    )
                }
            }
        }

        // --- Error Feedback ---
        errorMessage?.let { message ->
            Text(
                text = if (message.contains("422")) "Server Error (422): Check Authentication" else message,
                color = MaterialTheme.colorScheme.error,
                modifier = Modifier.padding(top = 16.dp)
            )
        }
    }
}

/**
 * card representing a single device's status summary.
 * Changes visual style
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun DeviceSummaryCard(
    device: Device,
    onClick: () -> Unit
) {

    // Logic to determine "Active" visual state: Online AND turned On
    val isPoweredOn = device.isPoweredOn     //check if the device is toggled "on"
    val isActiveVisual = isPoweredOn

    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        colors = CardDefaults.cardColors(containerColor = CardSurface),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Icon Background for when device is active or inactive
            val backgroundBrush = if (isActiveVisual) {
                Brush.linearGradient(colors = listOf(BrandBlue, BrandPurple))
            } else {
                Brush.linearGradient(colors = listOf(Color(0xFFF1F5F9), Color(0xFFF1F5F9)))
            }

            Box(
                modifier = Modifier
                    .size(64.dp)
                    .background(
                        brush = backgroundBrush,
                        shape = RoundedCornerShape(18.dp)
                    ),
                contentAlignment = Alignment.Center
            ) {
                DeviceIcon(
                    type = device.type,
                    tint = if (isPoweredOn) Color.White else TextGrey.copy(alpha = 0.4f)
                )
            }

            // --- Device Info ---
            Spacer(modifier = Modifier.width(20.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = device.name?.takeIf { it.isNotBlank() }
                        ?: (device.type ?: "unknown").replaceFirstChar { it.uppercase() },
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    //color = if (isPoweredOn) TextDark else TextGrey
                )

                // Connection Status indicator
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.padding(top = 6.dp)
                ) {
                    Surface(
                        modifier = Modifier.size(8.dp),
                        shape = CircleShape,
                        color = if (isPoweredOn) StatusGreen else Color(0xFF94A3B8)
                    ) {}
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = if (isPoweredOn) "Active" else "Off",
                        // status label shown to user
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Medium,
                        color = if (isPoweredOn) StatusGreen else Color(0xFF94A3B8)
                    )
                }
            }

            // Arrow to indicate the card is clickable
            Icon(
                imageVector = Icons.AutoMirrored.Filled.KeyboardArrowRight,
                contentDescription = null,
                tint = Color(0xFFCBD5E1)
            )
        }
    }
}

/**
 * Selecting the appropriate icon based on the device type string.
 */
@Composable
private fun DeviceIcon(type: String?, tint: Color) {
    val icon = when (type?.lowercase()) {
        "light", "lamp" -> Icons.Default.Lightbulb
        "fan" -> Icons.Default.WindPower
        "thermostat" -> Icons.Default.Thermostat
        else -> Icons.Default.DeviceUnknown
    }
    Icon(
        imageVector = icon,
        contentDescription = null,
        tint = tint,
        modifier = Modifier.size(32.dp)
    )
}
