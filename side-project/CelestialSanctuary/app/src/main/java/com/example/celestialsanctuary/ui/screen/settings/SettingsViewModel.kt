package com.example.celestialsanctuary.ui.screen.settings

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.celestialsanctuary.notification.NotificationSettingsRepository
import com.example.celestialsanctuary.util.SoundManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SettingsUiState(
    val notificationsEnabled: Boolean = true,
    val notificationHour: Int = 9,
    val notificationMinute: Int = 0,
    val soundEnabled: Boolean = true,
    val hapticEnabled: Boolean = true
)

@HiltViewModel
class SettingsViewModel @Inject constructor(
    application: Application
) : AndroidViewModel(application) {

    private val repository = NotificationSettingsRepository(application)
    private val soundManager = SoundManager.getInstance(application)

    private val _uiState = MutableStateFlow(SettingsUiState())
    val uiState: StateFlow<SettingsUiState> = _uiState.asStateFlow()

    init {
        loadSettings()
    }

    private fun loadSettings() {
        viewModelScope.launch {
            launch {
                repository.isNotificationsEnabled.collect { enabled ->
                    _uiState.update { it.copy(notificationsEnabled = enabled) }
                }
            }
            launch {
                repository.notificationHour.collect { hour ->
                    _uiState.update { it.copy(notificationHour = hour) }
                }
            }
            launch {
                repository.notificationMinute.collect { minute ->
                    _uiState.update { it.copy(notificationMinute = minute) }
                }
            }
        }

        // 사운드/햅틱 설정 로드
        _uiState.update {
            it.copy(
                soundEnabled = soundManager.isSoundEnabled(),
                hapticEnabled = soundManager.isHapticEnabled()
            )
        }
    }

    fun setNotificationsEnabled(enabled: Boolean) {
        viewModelScope.launch {
            repository.setNotificationsEnabled(enabled)
        }
    }

    fun setNotificationTime(hour: Int, minute: Int) {
        viewModelScope.launch {
            repository.setNotificationTime(hour, minute)
        }
    }

    fun setSoundEnabled(enabled: Boolean) {
        viewModelScope.launch {
            soundManager.setSoundEnabled(enabled)
            _uiState.update { it.copy(soundEnabled = enabled) }
        }
    }

    fun setHapticEnabled(enabled: Boolean) {
        viewModelScope.launch {
            soundManager.setHapticEnabled(enabled)
            _uiState.update { it.copy(hapticEnabled = enabled) }
        }
    }
}
