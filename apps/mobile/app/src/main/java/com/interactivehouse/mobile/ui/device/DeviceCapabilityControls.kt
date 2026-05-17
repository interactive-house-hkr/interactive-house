package com.interactivehouse.mobile.ui.device

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.interactivehouse.mobile.data.model.Device
import com.interactivehouse.mobile.ui.theme.*
import kotlin.math.roundToInt

/**
 * Dynamic Control Renderer:
 * Builds the UI based on device type and capabilities.
 */
@Composable
fun DeviceCapabilityControls(
    device: Device,
    isCommandInFlight: Boolean,
    onBooleanCapability: (String, Boolean) -> Unit,
    onIntegerCapability: (String, Int) -> Unit
) {
    val controlsEnabled = !isCommandInFlight
    val isPoweredOn = device.isPoweredOn

    // Extract capabilities that are marked "writable"
    val writableCaps = device.capabilitiesOrEmpty.entries
        .filter { it.value.writable }
        .sortedBy { it.key }

    Column(
        modifier = Modifier.fillMaxWidth().padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(24.dp)
    ) {
        if (writableCaps.isEmpty()) {
            Text(text = "No controls available", color = TextGrey)
        }

        // --- 1. Power Control (Primary) ---
        val powerCap = writableCaps.find { it.key == "power" }
        if (powerCap != null) {
            PowerButtonControl(
                label = "Power",
                isOn = isPoweredOn,
                enabled = controlsEnabled,
                onToggle = { onBooleanCapability("power", it) }
            )
        }

        // --- 2. Secondary Controls ---
        val secondaryCaps = writableCaps.filter { it.key != "power" }
        val shouldHideSecondary = powerCap != null && !isPoweredOn

        if (shouldHideSecondary && secondaryCaps.isNotEmpty()) {
            Text(
                text = "Turn device on to adjust more settings.",
                color = TextGrey,
                fontSize = 12.sp
            )
        } else {
            secondaryCaps.forEach { (key, spec) ->
                when (spec.type.lowercase()) {
                    "integer" -> {
                        // FAN SPECIAL CASE
                        if (device.type?.lowercase() == "fan" && key.lowercase() == "speed") {
                            FanSpeedControl(
                                currentSpeed = device.stateOrEmpty[key].toUiInt(0, 0, spec.max ?: 3),
                                maxSpeed = spec.max ?: 3,
                                enabled = controlsEnabled,
                                onSpeedChange = { onIntegerCapability(key, it) }
                            )
                        } else {
                            // Standard Slider (Brightness, etc)
                            IntegerSliderCard(
                                label = key.replaceFirstChar { it.uppercase() },
                                value = device.stateOrEmpty[key].toUiInt(spec.min ?: 0, spec.min ?: 0, spec.max ?: 100),
                                min = spec.min ?: 0,
                                max = spec.max ?: 100,
                                enabled = controlsEnabled,
                                onValueChange = { onIntegerCapability(key, it) }
                            )
                        }
                    }
                    "boolean" -> {
                        PowerButtonControl(
                            label = key.replaceFirstChar { it.uppercase() },
                            isOn = (device.stateOrEmpty[key] as? Boolean) ?: false,
                            enabled = controlsEnabled,
                            onToggle = { onBooleanCapability(key, it) }
                        )
                    }
                }
            }
        }
    }
}

/**
 * Custom Control for Fans: A row of buttons for discrete speeds.
 */
@Composable
private fun FanSpeedControl(
    currentSpeed: Int,
    maxSpeed: Int,
    enabled: Boolean,
    onSpeedChange: (Int) -> Unit
) {
    Card(
        shape = RoundedCornerShape(24.dp),
        colors = CardDefaults.cardColors(containerColor = CardSurface),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(24.dp)) {
            Text(text = "Fan Speed", fontWeight = FontWeight.Bold, fontSize = 18.sp, color = TextDark)
            Spacer(modifier = Modifier.height(16.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                (0..maxSpeed).forEach { speed ->
                    val isSelected = currentSpeed == speed
                    Button(
                        onClick = { onSpeedChange(speed) },
                        enabled = enabled,
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(12.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = if (isSelected) BrandPurple else Color(0xFFE5E7EB)
                        )
                    ) {
                        Text(
                            text = if (speed == 0) "OFF" else speed.toString(),
                            color = if (isSelected) Color.White else TextDark,
                            fontSize = 12.sp
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun PowerButtonControl(
    label: String,
    isOn: Boolean,
    enabled: Boolean,
    onToggle: (Boolean) -> Unit
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(text = label, fontWeight = FontWeight.Medium, color = if (enabled) TextDark else TextGrey)
        Spacer(modifier = Modifier.height(12.dp))
        Button(
            onClick = { onToggle(!isOn) },
            enabled = enabled,
            modifier = Modifier.fillMaxWidth().height(64.dp),
            shape = RoundedCornerShape(16.dp),
            colors = ButtonDefaults.buttonColors(containerColor = Color.Transparent),
            contentPadding = PaddingValues()
        ) {
            val alpha by animateFloatAsState(if (enabled) 1f else 0.5f)
            Box(
                modifier = Modifier.fillMaxSize().alpha(alpha).background(
                    brush = if (isOn) Brush.linearGradient(listOf(BrandBlue, BrandPurple))
                    else Brush.linearGradient(listOf(Color(0xFFE5E7EB), Color(0xFFD1D5DB))),
                    shape = RoundedCornerShape(16.dp)
                ),
                contentAlignment = Alignment.Center
            ) {
                Text(text = if (isOn) "ON" else "OFF", fontWeight = FontWeight.Bold, color = if (isOn) Color.White else TextDark)
            }
        }
    }
}

@Composable
private fun IntegerSliderCard(
    label: String,
    value: Int,
    min: Int,
    max: Int,
    enabled: Boolean,
    onValueChange: (Int) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        colors = CardDefaults.cardColors(containerColor = CardSurface)
    ) {
        Column(modifier = Modifier.padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            Row(modifier = Modifier.fillMaxWidth()) {
                Text(text = label, fontSize = 18.sp, fontWeight = FontWeight.Bold, color = if (enabled) TextDark else TextGrey)
            }
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = if (label.lowercase() == "brightness") "$value%" else "$value",
                fontSize = 48.sp,
                fontWeight = FontWeight.Bold,
                style = MaterialTheme.typography.headlineLarge.copy(
                    brush = if (enabled) Brush.linearGradient(listOf(BrandBlue, BrandPurple)) else Brush.linearGradient(listOf(TextGrey, TextGrey))
                )
            )
            Slider(
                value = value.toFloat(),
                onValueChange = { onValueChange(it.roundToInt()) },
                valueRange = min.toFloat()..max.toFloat(),
                enabled = enabled,
                colors = SliderDefaults.colors(thumbColor = BrandBlue, activeTrackColor = BrandBlue)
            )
        }
    }
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
