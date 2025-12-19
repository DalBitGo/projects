package com.example.celestialsanctuary.ui.screen.house

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.celestialsanctuary.domain.model.HouseDetail
import com.example.celestialsanctuary.domain.model.Result
import com.example.celestialsanctuary.domain.usecase.GetHouseDetailUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * House Room 화면 UI 상태
 */
data class HouseRoomUiState(
    val houseDetails: List<HouseDetail> = emptyList(),
    val initialHouseIndex: Int = 1,
    val currentHouseIndex: Int = 1,
    val isLoading: Boolean = false,
    val error: String? = null
)

/**
 * House Room 화면의 ViewModel
 *
 * GetHouseDetailUseCase를 통해 하우스 상세 정보 조회 및 방문 기록
 */
@HiltViewModel
class HouseRoomViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle,
    private val getHouseDetailUseCase: GetHouseDetailUseCase
) : ViewModel() {

    private val initialIndex: Int = savedStateHandle.get<Int>("houseIndex") ?: 1

    private val _uiState = MutableStateFlow(
        HouseRoomUiState(
            isLoading = true,
            initialHouseIndex = initialIndex,
            currentHouseIndex = initialIndex
        )
    )
    val uiState: StateFlow<HouseRoomUiState> = _uiState.asStateFlow()

    init {
        loadAllHouseDetails()
    }

    /**
     * 모든 하우스 상세 정보 로드
     */
    private fun loadAllHouseDetails() {
        viewModelScope.launch {
            val details = mutableListOf<HouseDetail>()
            var hasError = false
            var errorMessage: String? = null

            // 12개 하우스 정보 로드
            for (index in 1..12) {
                // 초기 하우스만 방문 기록 (나머지는 스와이프 시 기록)
                val markVisited = (index == initialIndex)

                when (val result = getHouseDetailUseCase(index, markAsVisited = markVisited)) {
                    is Result.Success -> details.add(result.data)
                    is Result.Error -> {
                        hasError = true
                        errorMessage = result.message
                    }
                    is Result.Loading -> { /* 무시 */ }
                }
            }

            _uiState.value = _uiState.value.copy(
                houseDetails = details,
                isLoading = false,
                error = if (hasError) errorMessage else null
            )
        }
    }

    /**
     * 페이지 변경 시 호출 - 방문 기록 업데이트
     */
    fun onPageChanged(houseIndex: Int) {
        if (_uiState.value.currentHouseIndex != houseIndex) {
            _uiState.value = _uiState.value.copy(currentHouseIndex = houseIndex)

            // 방문 기록 (데이터 다시 로드하지 않고 기록만)
            viewModelScope.launch {
                getHouseDetailUseCase(houseIndex, markAsVisited = true)
            }
        }
    }

    /**
     * 에러 메시지 확인 완료
     */
    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }
}
