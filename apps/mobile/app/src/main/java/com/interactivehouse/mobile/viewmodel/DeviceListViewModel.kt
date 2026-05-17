package com.interactivehouse.mobile.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.interactivehouse.mobile.data.model.Device
import com.interactivehouse.mobile.data.repository.DeviceRepository
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
/**
 * ViewModel responsible for managing the state of the Device List screen.
 * It handles fetching data from the repository, periodic refreshing (polling),
 * and sending control commands to devices.
 */
class DeviceListViewModel : ViewModel() {

    private val repository = DeviceRepository()

    // --- UI State Variables ---
    // Internal mutable state for the list of devices
    private val _devices = MutableStateFlow<List<Device>>(emptyList())

    // Public read-only stream of devices for the UI to observe
    val devices: StateFlow<List<Device>> = _devices.asStateFlow()

    // Tracks if the initial or a manual full-page reload is happening
    private val _isLoading = MutableStateFlow(false) //
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    // General error message for loading the list
    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()

    private val _commandSuccessMessage = MutableStateFlow<String?>(null)
    val commandSuccessMessage: StateFlow<String?> = _commandSuccessMessage.asStateFlow()

    private val _commandErrorMessage = MutableStateFlow<String?>(null)
    val commandErrorMessage: StateFlow<String?> = _commandErrorMessage.asStateFlow()

    // Tracks if a command is currently being sent to prevent double-clicks/overlapping actions
    private val _isCommandInFlight = MutableStateFlow(false)
    val isCommandInFlight: StateFlow<Boolean> = _isCommandInFlight.asStateFlow()

    // --- Polling Logic ---

    private var refreshJob: Job? = null
    fun startPeriodicRefresh() {
        if (refreshJob?.isActive == true) return // is polling running? -> exit
        refreshJob = viewModelScope.launch {
            while (isActive) {
                delay(5_000)
                loadDevices(showLoading = false)
            }
        }
    }
    //Stop background polling loop
    fun stopPeriodicRefresh() {
        refreshJob?.cancel()
        refreshJob = null
    }

    // Cancel polling to prevent memory leaks when the screen is closed.
    override fun onCleared() {
        refreshJob?.cancel()
        super.onCleared()
    }

    // Fetches the latest device list from the server.
    fun loadDevices(showLoading: Boolean = true) {
        viewModelScope.launch {
            _errorMessage.value = null // Reset previous errors
            if (showLoading) _isLoading.value = true
            try {
                val result = repository.getDevices()
                _devices.value = result
            } catch (e: Exception) {
                _errorMessage.value = e.message ?: "Failed to load devices"
            } finally {
                if (showLoading) _isLoading.value = false
            }
        }
    }

    /**
     * Clears the main loading error message
     */
    fun clearError() {
        _errorMessage.value = null
    }

    /**
     * Convenience method to trigger a refresh without showing a full-screen loading spinner.
     */
    fun refreshDevices() {
        loadDevices(showLoading = false)
    }

    /**
     * Sends a command to change a device's state
     *
     * @param device The device being updated.
     * @param statePatch A map of properties to update (e.g., MapOf("power" to true)).
     */

    fun sendDeviceState(device: Device, statePatch: Map<String, Any>) {
        println("SEND COMMAND CALLED: ${device.deviceUuid} $statePatch")
        if (statePatch.isEmpty()) return

        // Capture the old state in case we need to roll back on failure
        val previousDevices = _devices.value

        // OPTIMISTIC UPDATE: Update the UI immediately
        _devices.value = _devices.value.map { d ->
            if (d.deviceUuid == device.deviceUuid) {
                val newState = d.stateOrEmpty.toMutableMap().apply {
                    putAll(statePatch)
                }
                d.copy(state = newState)
            } else d
        }

        viewModelScope.launch {
            _isCommandInFlight.value = true
            try {
                val wrappedPayload = mapOf("state" to statePatch)
                val response = repository.sendCommand(
                    uuid = device.deviceUuid,
                    state = statePatch
                )

                if (response.status == "success") {
                    _commandSuccessMessage.value = formatCommandSuccess(statePatch)
                    val freshList = repository.getDevices()
                    _devices.value = freshList
                } else {
                    // go back to the old UI state
                    _devices.value = previousDevices
                    _commandErrorMessage.value = response.message ?: "Command failed"
                }
            } catch (e: Exception) {
                // If the network failed, go back to the old UI state
                _devices.value = previousDevices
                _commandErrorMessage.value = e.message ?: "Network error"
            } finally {
                _isCommandInFlight.value = false
            }
        }
    }

    /**
    Toggle power for a device.
     */
    fun setPower(device: Device, power: Boolean) {
        sendDeviceState(device, mapOf("power" to power))
    }


    //Setting a numeric value for a capability.
    fun setIntegerCapability(device: Device, key: String, value: Int) {
        sendDeviceState(device, mapOf(key to value))
    }

    private fun formatCommandSuccess(patch: Map<String, Any>): String =
        patch.entries.joinToString(prefix = "Updated: ", separator = ", ") { (k, v) ->
            "$k → $v"
        }
}

