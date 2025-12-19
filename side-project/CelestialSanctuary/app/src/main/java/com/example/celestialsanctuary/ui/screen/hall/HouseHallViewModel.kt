package com.example.celestialsanctuary.ui.screen.hall

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.celestialsanctuary.domain.model.House
import com.example.celestialsanctuary.domain.model.HouseState
import com.example.celestialsanctuary.domain.model.Planet
import com.example.celestialsanctuary.domain.model.Result
import com.example.celestialsanctuary.domain.usecase.GetAllHousesUseCase
import com.example.celestialsanctuary.domain.usecase.GetUserProfileUseCase
import com.example.celestialsanctuary.domain.usecase.HouseWithVisitState
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * UI 표시용 하우스 상태
 */
data class HouseWithState(
    val house: House,
    val state: HouseState,
    val planet: Planet? = null,
    val isVisited: Boolean = false
)

/**
 * Hall 화면 UI 상태
 */
data class HouseHallUiState(
    val houses: List<HouseWithState> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
    val userName: String? = null,
    val sunSign: String? = null,
    val moonSign: String? = null,
    val ascendant: String? = null,
    val dailyFortune: String = "",
    val visitedCount: Int = 0,
    val totalHouses: Int = 12,
    val isAllExplored: Boolean = false
)

/**
 * House Hall 화면의 ViewModel
 *
 * UseCase를 통해 비즈니스 로직을 위임
 */
@HiltViewModel
class HouseHallViewModel @Inject constructor(
    private val getAllHousesUseCase: GetAllHousesUseCase,
    private val getUserProfileUseCase: GetUserProfileUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(HouseHallUiState(isLoading = true))
    val uiState: StateFlow<HouseHallUiState> = _uiState.asStateFlow()

    init {
        loadData()
    }

    /**
     * 하우스 데이터와 사용자 프로필 로드
     */
    private fun loadData() {
        viewModelScope.launch {
            combine(
                getAllHousesUseCase(),
                getUserProfileUseCase()
            ) { housesResult, profileResult ->

                // 하우스 데이터 처리
                val houses = when (housesResult) {
                    is Result.Success -> housesResult.data.map { it.toUiModel() }
                    is Result.Error -> {
                        // 에러 시 빈 하우스 표시
                        House.ALL_HOUSES.map { HouseWithState(it, HouseState.EMPTY) }
                    }
                    is Result.Loading -> emptyList()
                }

                // 프로필 데이터 처리
                val profile = profileResult.getOrNull()

                // 에러 메시지
                val error = when {
                    housesResult is Result.Error -> housesResult.message
                    profileResult is Result.Error -> profileResult.message
                    else -> null
                }

                HouseHallUiState(
                    houses = houses,
                    isLoading = false,
                    error = error,
                    userName = profile?.profile?.name,
                    sunSign = profile?.sunSign,
                    moonSign = profile?.moonSign,
                    ascendant = profile?.ascendant,
                    dailyFortune = profile?.dailyFortune ?: "",
                    visitedCount = houses.count { it.isVisited },
                    totalHouses = 12,
                    isAllExplored = houses.count { it.isVisited } >= 12
                )
            }.collect { state ->
                _uiState.value = state
            }
        }
    }

    /**
     * 데이터 새로고침
     */
    fun refresh() {
        _uiState.value = _uiState.value.copy(isLoading = true, error = null)
        loadData()
    }

    /**
     * 에러 메시지 확인 완료
     */
    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }
}

/**
 * UseCase 모델 → UI 모델 변환
 */
private fun HouseWithVisitState.toUiModel(): HouseWithState {
    return HouseWithState(
        house = this.house,
        state = this.state,
        planet = this.planet,
        isVisited = this.isVisited
    )
}
