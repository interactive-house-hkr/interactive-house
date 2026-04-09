package com.interactivehouse.mobile.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.interactivehouse.mobile.data.DemoModeConfig
import com.interactivehouse.mobile.data.model.Device
import com.interactivehouse.mobile.ui.device.formatStateValue
import com.interactivehouse.mobile.viewmodel.DeviceListViewModel

@Composable
fun DeviceListScreen(
    viewModel: DeviceListViewModel,
    onDeviceClick: (Device) -> Unit
) {
    val devices by viewModel.devices.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val errorMessage by viewModel.errorMessage.collectAsState() // fetching error
    val commandSuccessMessage by viewModel.commandSuccessMessage.collectAsState()
    val commandErrorMessage by viewModel.commandErrorMessage.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 20.dp, vertical = 24.dp)
    ) {
        Text(
            text = "My home",
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(bottom = 4.dp)
        )
        Text(
            text = "Devices",
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(bottom = 20.dp)
        )

        // If demo mode is on show a banner
        if (DemoModeConfig.USE_DEMO_MODE) {
            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.tertiaryContainer),
                shape = RoundedCornerShape(16.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 16.dp)
            ) {
                Text(
                    text = "DEMO MODE — devices and commands are local (no server).",
                    color = MaterialTheme.colorScheme.onTertiaryContainer,
                    style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier.padding(14.dp)
                )
            }
        }

        // If there is an error, show error card
        errorMessage?.let { message ->
            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer),
                shape = RoundedCornerShape(16.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 12.dp)
            ) {
                Text(
                    text = message,
                    color = MaterialTheme.colorScheme.onErrorContainer,
                    modifier = Modifier.padding(14.dp)
                )
            }
        }

        // Success related feedback
        commandSuccessMessage?.let { message ->
            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer),
                shape = RoundedCornerShape(16.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 12.dp)
            ) {
                Text(
                    text = message,
                    color = MaterialTheme.colorScheme.onPrimaryContainer,
                    modifier = Modifier.padding(14.dp)
                )
            }
        }

        // Command related failures
        commandErrorMessage?.let { message ->
            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer),
                shape = RoundedCornerShape(16.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 12.dp)
            ) {
                Text(
                    text = message,
                    color = MaterialTheme.colorScheme.onErrorContainer,
                    modifier = Modifier.padding(14.dp)
                )
            }
        }

        // What action to show next
        when {
            isLoading -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }
            devices.isEmpty() && errorMessage == null -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "No devices found",
                        style = MaterialTheme.typography.bodyLarge
                    )
                }
            }
            else -> {
                LazyColumn(
                    verticalArrangement = Arrangement.spacedBy(14.dp)
                ) {
                    items(devices, key = { it.deviceUuid }) { device ->
                        DeviceSummaryCard(
                            device = device,
                            onClick = { onDeviceClick(device) }
                        )
                    }
                }
            }
        }
    }
}

// draws device card
@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun DeviceSummaryCard(
    device: Device,
    onClick: () -> Unit
) {
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceContainerHigh
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(18.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // show visual marker based on device type
            DeviceTypeIconPlaceholder(type = device.type)
            Column(modifier = Modifier.padding(start = 16.dp)) { //Contain textual info
                // device display name
                Text(
                    text = device.name?.takeIf { it.isNotBlank() }
                        ?: device.type.replaceFirstChar { it.uppercase() },
                    style = MaterialTheme.typography.titleMedium
                )
                // room
                Text(
                    text = device.room?.takeIf { it.isNotBlank() }?.let { "Room: $it" } ?: "Room: —",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(top = 4.dp)
                )
                // status
                Text(
                    text = deviceSummaryStatus(device),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.padding(top = 6.dp)
                )
            }
        }
    }
}

// Creates symbol shown on each card
@Composable
private fun DeviceTypeIconPlaceholder(type: String) {
    val symbol = when (type.lowercase()) {
        "light", "lamp" -> "◯"
        "fan" -> "⌁"
        else -> type.take(1).uppercase()  //Use the first letter
    }
    // background colour behind the symbol
    Surface(
        modifier = Modifier.size(52.dp),
        shape = CircleShape,
        color = MaterialTheme.colorScheme.primaryContainer
    ) {
        Box(contentAlignment = Alignment.Center) {
            Text(
                text = symbol,
                style = MaterialTheme.typography.titleLarge,
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )
        }
    }
}

// Short status string shown on the card
private fun deviceSummaryStatus(device: Device): String {
    val state = device.stateOrEmpty
    // checks whether the device state contains a power value
    val power = state["power"]
    if (power is Boolean) {
        val extra = state.entries
            .filter { it.key != "power" }
            .sortedBy { it.key }
            .take(1)
            .joinToString { "${it.key} ${formatStateValue(it.value)}" }
        return if (extra.isNotEmpty()) {
            "${if (power) "On" else "Off"} · $extra"
        } else {
            if (power) "On" else "Off"
        }
    }
    if (state.isEmpty()) return "No status"
    return state.entries.sortedBy { it.key }.take(2)
        .joinToString(" · ") { "${it.key}: ${formatStateValue(it.value)}" }
}
