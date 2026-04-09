package com.interactivehouse.mobile.ui.device

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Slider
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.interactivehouse.mobile.data.model.CapabilitySpec
import com.interactivehouse.mobile.data.model.Device
import kotlin.math.roundToInt

/**
 * Capability-driven controls for a single device (detail screen).
 */
@Composable
fun DeviceCapabilityControls(
    device: Device,
    isCommandInFlight: Boolean,
    onBooleanCapability: (String, Boolean) -> Unit,
    onIntegerCapability: (String, Int) -> Unit
) {
    val writableCaps = device.capabilities.entries
        .filter { it.value.writable }
        .sortedBy { it.key }
    if (writableCaps.isEmpty()) {
        Text(
            text = "No writable capabilities",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        return
    }
    writableCaps.forEach { (key, spec) ->
        CapabilityControlRow(
            device = device,
            capabilityKey = key,
            spec = spec,
            isCommandInFlight = isCommandInFlight,
            onBooleanCapability = onBooleanCapability,
            onIntegerCapability = onIntegerCapability
        )
    }
}

@Composable
private fun CapabilityControlRow(
    device: Device,
    capabilityKey: String,
    spec: CapabilitySpec,
    isCommandInFlight: Boolean,
    onBooleanCapability: (String, Boolean) -> Unit,
    onIntegerCapability: (String, Int) -> Unit
) {
    when (spec.type) {
        "boolean" -> {
            val current = (device.stateOrEmpty[capabilityKey] as? Boolean) ?: false
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.padding(top = 12.dp)
            ) {
                Text(
                    text = capabilityKey.replaceFirstChar { it.uppercase() },
                    style = MaterialTheme.typography.bodyLarge,
                    modifier = Modifier.width(112.dp)
                )
                Switch(
                    checked = current,
                    onCheckedChange = { onBooleanCapability(capabilityKey, it) },
                    enabled = !isCommandInFlight
                )
            }
        }
        "integer" -> {
            val min = spec.min ?: 0
            val max = spec.max ?: 100
            val fallback = ((min + max) / 2).coerceIn(min, max)
            val current = device.stateOrEmpty[capabilityKey].toUiInt(fallback, min, max)
            Column(modifier = Modifier.padding(top = 12.dp)) {
                Text(
                    text = "${capabilityKey.replaceFirstChar { it.uppercase() }} — $current",
                    style = MaterialTheme.typography.bodyLarge
                )
                Slider(
                    value = current.toFloat(),
                    onValueChange = { raw ->
                        val rounded = raw.roundToInt().coerceIn(min, max)
                        onIntegerCapability(capabilityKey, rounded)
                    },
                    valueRange = min.toFloat()..max.toFloat(),
                    steps = sliderSteps(min, max),
                    enabled = !isCommandInFlight,
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }
        else -> {
            Text(
                text = "$capabilityKey (${spec.type}) — unsupported control type",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(top = 12.dp)
            )
        }
    }
}

fun formatStateValue(value: Any?): String = when (value) {
    null -> "—"
    is Boolean -> if (value) "on" else "off"
    is Number -> value.toInt().toString()
    else -> value.toString()
}

fun sliderSteps(min: Int, max: Int): Int {
    val span = max - min
    return if (span in 1..10) span else 0
}

fun Any?.toUiInt(fallback: Int, min: Int, max: Int): Int {
    val n = when (this) {
        is Int -> this
        is Double -> this.toInt()
        is Float -> this.toInt()
        is Number -> this.toInt()
        else -> null
    } ?: return fallback
    return n.coerceIn(min, max)
}


