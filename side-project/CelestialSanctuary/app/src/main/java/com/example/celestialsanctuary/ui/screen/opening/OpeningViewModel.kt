package com.example.celestialsanctuary.ui.screen.opening

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.celestialsanctuary.data.repository.UserRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class OpeningDestination {
    data object Loading : OpeningDestination()
    data object Onboarding : OpeningDestination()
    data object Hall : OpeningDestination()
}

@HiltViewModel
class OpeningViewModel @Inject constructor(
    private val userRepository: UserRepository
) : ViewModel() {

    private val _destination = MutableStateFlow<OpeningDestination>(OpeningDestination.Loading)
    val destination: StateFlow<OpeningDestination> = _destination.asStateFlow()

    fun checkOnboardingStatus() {
        viewModelScope.launch {
            val isCompleted = userRepository.isOnboardingCompleted.first()
            _destination.value = if (isCompleted) {
                OpeningDestination.Hall
            } else {
                OpeningDestination.Onboarding
            }
        }
    }
}
