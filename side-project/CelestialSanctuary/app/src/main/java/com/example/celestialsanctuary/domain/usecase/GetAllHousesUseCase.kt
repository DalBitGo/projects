package com.example.celestialsanctuary.domain.usecase

import com.example.celestialsanctuary.data.repository.ChartRepository
import com.example.celestialsanctuary.data.repository.HouseWithPlanetState
import com.example.celestialsanctuary.data.repository.UserRepository
import com.example.celestialsanctuary.domain.model.House
import com.example.celestialsanctuary.domain.model.HouseState
import com.example.celestialsanctuary.domain.model.Planet
import com.example.celestialsanctuary.domain.model.Result
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.map
import javax.inject.Inject

/**
 * 모든 하우스 정보를 가져오는 UseCase
 *
 * 책임:
 * - 차트 정보와 방문 기록을 조합
 * - UI에서 사용할 형태로 변환
 *
 * 사용 예:
 * ```
 * val houses = getAllHousesUseCase()
 * houses.collect { result ->
 *     when (result) {
 *         is Result.Success -> showHouses(result.data)
 *         is Result.Error -> showError(result.message)
 *     }
 * }
 * ```
 */
class GetAllHousesUseCase @Inject constructor(
    private val chartRepository: ChartRepository,
    private val userRepository: UserRepository
) {
    /**
     * 하우스 데이터와 방문 정보를 조합하여 반환
     */
    operator fun invoke(): Flow<Result<List<HouseWithVisitState>>> {
        return combine(
            chartRepository.getAllHousesWithState(),
            userRepository.visitedHouses
        ) { housesWithPlanet, visitedSet ->
            val result = housesWithPlanet.map { h ->
                HouseWithVisitState(
                    house = h.house,
                    state = h.state,
                    planet = h.primaryPlanet,
                    isVisited = visitedSet.contains(h.house.index)
                )
            }
            Result.success(result)
        }.catch { e ->
            emit(Result.error("하우스 정보를 불러올 수 없습니다", e))
        }
    }

    /**
     * 방문한 하우스 개수 반환
     */
    fun getVisitedCount(): Flow<Int> {
        return userRepository.visitedHouses.map { it.size }
    }

    /**
     * 모든 하우스 탐험 완료 여부
     */
    fun isAllExplored(): Flow<Boolean> {
        return userRepository.visitedHouses.map { it.size >= 12 }
    }
}

/**
 * 하우스 정보 + 방문 상태
 */
data class HouseWithVisitState(
    val house: House,
    val state: HouseState,
    val planet: Planet? = null,
    val isVisited: Boolean = false
)
