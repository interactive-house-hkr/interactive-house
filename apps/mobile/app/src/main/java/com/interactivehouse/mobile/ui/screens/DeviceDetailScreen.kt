package com.interactivehouse.mobile.ui.screens

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.interactivehouse.mobile.data.DemoModeConfig
import com.interactivehouse.mobile.ui.device.DeviceCapabilityControls
import com.interactivehouse.mobile.ui.device.formatStateValue
import com.interactivehouse.mobile.viewmodel.DeviceListViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DeviceDetailScreen(
    deviceUuid: String,
    viewModel: DeviceListViewModel,
    onBack: () -> Unit
) {
    val devices by viewModel.devices.collectAsState()
    val errorMessage by viewModel.errorMessage.collectAsState()
    val commandSuccessMessage by viewModel.commandSuccessMessage.collectAsState()
    val commandErrorMessage by viewModel.commandErrorMessage.collectAsState()
    val isCommandInFlight by viewModel.isCommandInFlight.collectAsState()

    val device = devices.find { it.deviceUuid == deviceUuid }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = device?.let { d ->
                            d.name?.takeIf { it.isNotBlank() }
                                ?: d.type.replaceFirstChar { it.uppercase() }
                        } ?: "Device"
                    )
                },
                navigationIcon = {
                    TextButton(onClick = onBack) {
                        Text("Back")
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = 20.dp, vertical = 16.dp)
        ) {
            if (DemoModeConfig.USE_DEMO_MODE) {
                Text(
                    text = "DEMO MODE — local state only",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.tertiary,
                    modifier = Modifier.padding(bottom = 12.dp)
                )
            }

            errorMessage?.let { msg ->
                Card(
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer),
                    modifier = Modifier.padding(bottom = 8.dp)
                ) {
                    Text(msg, Modifier.padding(12.dp), color = MaterialTheme.colorScheme.onErrorContainer)
                }
            }
            commandSuccessMessage?.let { msg ->
                Card(
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer),
                    modifier = Modifier.padding(bottom = 8.dp)
                ) {
                    Text(msg, Modifier.padding(12.dp), color = MaterialTheme.colorScheme.onPrimaryContainer)
                }
            }
            commandErrorMessage?.let { msg ->
                Card(
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer),
                    modifier = Modifier.padding(bottom = 8.dp)
                ) {
                    Text(msg, Modifier.padding(12.dp), color = MaterialTheme.colorScheme.onErrorContainer)
                }
            }

            if (device == null) {
                Text(
                    text = "Device not found or still loading.",
                    style = MaterialTheme.typography.bodyLarge
                )
                return@Column
            }

            Text(
                text = "Room: ${device.room?.takeIf { it.isNotBlank() } ?: "—"}",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = "Type: ${device.type}",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(top = 4.dp)
            )
            Text(
                text = "ID: ${device.deviceUuid}",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(top = 2.dp, bottom = 16.dp)
            )

            Text(
                text = "Current values",
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(bottom = 8.dp)
            )
            if (device.state.isEmpty()) {
                Text(
                    text = "No state reported",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            } else {
                device.state.entries.sortedBy { it.key }.forEach { (key, value) ->
                    Text(
                        text = "$key: ${formatStateValue(value)}",
                        style = MaterialTheme.typography.bodyLarge,
                        modifier = Modifier.padding(vertical = 4.dp)
                    )
                }
            }

            Text(
                text = "Controls",
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(top = 24.dp, bottom = 8.dp)
            )
            DeviceCapabilityControls(
                device = device,
                isCommandInFlight = isCommandInFlight,
                onBooleanCapability = { key, value ->
                    viewModel.sendDeviceState(device, mapOf(key to value))
                },
                onIntegerCapability = { key, value ->
                    viewModel.setIntegerCapability(device, key, value)
                }
            )
        }
    }
}
