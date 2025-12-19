package com.example.celestialsanctuary.ui.screen.onboarding

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.celestialsanctuary.domain.model.Result
import com.example.celestialsanctuary.domain.usecase.SaveUserProfileUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * 온보딩 화면 UI 상태
 */
data class OnboardingUiState(
    val userName: String = "",
    val birthDate: String = "",
    val birthTime: String = "",
    val birthLocation: String = "",
    val isLoading: Boolean = false,
    val errorMessage: String? = null
)

/**
 * 온보딩 이벤트
 */
sealed class OnboardingEvent {
    data object NavigateToHall : OnboardingEvent()
}

/**
 * 온보딩 화면의 ViewModel
 *
 * SaveUserProfileUseCase를 통해 프로필 저장 및 유효성 검증
 */
@HiltViewModel
class OnboardingViewModel @Inject constructor(
    private val saveUserProfileUseCase: SaveUserProfileUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(OnboardingUiState())
    val uiState: StateFlow<OnboardingUiState> = _uiState.asStateFlow()

    private val _events = MutableSharedFlow<OnboardingEvent>()
    val events: SharedFlow<OnboardingEvent> = _events.asSharedFlow()

    fun updateUserName(name: String) {
        _uiState.value = _uiState.value.copy(userName = name, errorMessage = null)
    }

    fun updateBirthDate(date: String) {
        _uiState.value = _uiState.value.copy(birthDate = date, errorMessage = null)
    }

    fun updateBirthTime(time: String) {
        _uiState.value = _uiState.value.copy(birthTime = time, errorMessage = null)
    }

    fun updateBirthLocation(location: String) {
        _uiState.value = _uiState.value.copy(birthLocation = location, errorMessage = null)
    }

    /**
     * 프로필 저장
     * UseCase가 유효성 검증 및 저장을 담당
     */
    fun saveProfile() {
        val state = _uiState.value
        _uiState.value = state.copy(isLoading = true, errorMessage = null)

        viewModelScope.launch {
            val result = saveUserProfileUseCase(
                userName = state.userName,
                birthDate = state.birthDate,
                birthTime = state.birthTime,
                birthLocation = state.birthLocation
            )

            when (result) {
                is Result.Success -> {
                    _events.emit(OnboardingEvent.NavigateToHall)
                }
                is Result.Error -> {
                    _uiState.value = state.copy(
                        isLoading = false,
                        errorMessage = result.message
                    )
                }
                is Result.Loading -> { /* 무시 */ }
            }
        }
    }

    /**
     * 에러 메시지 확인 완료
     */
    fun clearError() {
        _uiState.value = _uiState.value.copy(errorMessage = null)
    }
}
