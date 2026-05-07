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

class DeviceListViewModel : ViewModel() {

    private val repository = DeviceRepository() // Object to talk to the data layer

    private val _devices = MutableStateFlow<List<Device>>(emptyList()) //internal mutable list of device
    val devices: StateFlow<List<Device>> = _devices.asStateFlow() // devices exposed to the UI

    private val _isLoading = MutableStateFlow(false) // stores whether the app is currently loading devices, starts as false then changes
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()

    private val _commandSuccessMessage = MutableStateFlow<String?>(null)
    val commandSuccessMessage: StateFlow<String?> = _commandSuccessMessage.asStateFlow()

    private val _commandErrorMessage = MutableStateFlow<String?>(null) //holds error message for device loading problems
    val commandErrorMessage: StateFlow<String?> = _commandErrorMessage.asStateFlow()

    private val _isCommandInFlight = MutableStateFlow(false) // to tracks if a command is sent
    val isCommandInFlight: StateFlow<Boolean> = _isCommandInFlight.asStateFlow()

    private var refreshJob: Job? = null

    /**
     * 5s polling aligned with API guidance.
     */
    fun startPeriodicRefresh() {
        if (refreshJob?.isActive == true) return // is polling running? -> exit
        refreshJob = viewModelScope.launch {
            while (isActive) {
                delay(5_000)
                loadDevices(showLoading = false)
            }
        }
    }

    override fun onCleared() {
        refreshJob?.cancel()
        super.onCleared()
    }


    fun loadDevices(showLoading: Boolean = true) {
        viewModelScope.launch {
            _errorMessage.value = null // clear any old error
            if (showLoading) _isLoading.value = true
            try {
                val result = repository.getDevices() // call repository for devices
                _devices.value = result
            } catch (e: Exception) {
                _errorMessage.value = e.message ?: "Failed to load devices" // save error message into state
            } finally {
                if (showLoading) _isLoading.value = false
            }
        }
    }

    fun clearError() {
        _errorMessage.value = null
    }

    fun refreshDevices() {
        loadDevices(showLoading = false)
    }

    /**
     * Sends a partial state update (same contract as POST .../commands body `state`).
     */
    fun sendDeviceState(device: Device, statePatch: Map<String, Any>) {
        if (statePatch.isEmpty()) return
        viewModelScope.launch {
            _commandSuccessMessage.value = null
            _commandErrorMessage.value = null
            _isCommandInFlight.value = true

            try {
                val response = repository.sendCommand(
                    uuid = device.deviceUuid,
                    state = statePatch
                )

                if (response.status == "success") {
                    _commandSuccessMessage.value = formatCommandSuccess(statePatch)

                    val result = repository.getDevices()
                    _devices.value = result
                } else {
                    _commandErrorMessage.value =
                        response.message ?: response.error ?: "Command failed"
                }
            } catch (e: Exception) {
                _commandErrorMessage.value = e.message ?: "Command failed"
            } finally {
                _isCommandInFlight.value = false
            }
        }
    }

    fun setPower(device: Device, power: Boolean) {
        sendDeviceState(device, mapOf("power" to power))
    }

    fun setIntegerCapability(device: Device, key: String, value: Int) {
        sendDeviceState(device, mapOf(key to value))
    }

    private fun formatCommandSuccess(patch: Map<String, Any>): String =
        patch.entries.joinToString(prefix = "Updated: ", separator = ", ") { (k, v) ->
            "$k → $v"
        }
}
