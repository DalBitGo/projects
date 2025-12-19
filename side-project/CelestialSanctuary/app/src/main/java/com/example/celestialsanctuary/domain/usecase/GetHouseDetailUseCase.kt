package com.example.celestialsanctuary.domain.usecase

import com.example.celestialsanctuary.data.repository.ChartRepository
import com.example.celestialsanctuary.data.repository.UserRepository
import com.example.celestialsanctuary.domain.model.HouseDetail
import com.example.celestialsanctuary.domain.model.Result
import javax.inject.Inject

/**
 * 특정 하우스의 상세 정보를 가져오는 UseCase
 *
 * 책임:
 * - 하우스 상세 정보 조회
 * - 방문 기록 저장
 *
 * 사용 예:
 * ```
 * val result = getHouseDetailUseCase(houseIndex = 1)
 * result.onSuccess { detail -> showDetail(detail) }
 *        .onError { msg, _ -> showError(msg) }
 * ```
 */
class GetHouseDetailUseCase @Inject constructor(
    private val chartRepository: ChartRepository,
    private val userRepository: UserRepository
) {
    /**
     * 하우스 상세 정보 조회 및 방문 기록
     *
     * @param houseIndex 하우스 번호 (1-12)
     * @param markAsVisited 방문 기록 여부 (기본: true)
     */
    suspend operator fun invoke(
        houseIndex: Int,
        markAsVisited: Boolean = true
    ): Result<HouseDetail> {
        return try {
            // 유효성 검사
            if (houseIndex !in 1..12) {
                return Result.error("유효하지 않은 하우스 번호입니다: $houseIndex")
            }

            // 상세 정보 조회
            val detail = chartRepository.getHouseDetail(houseIndex)

            // 방문 기록
            if (markAsVisited) {
                userRepository.markHouseVisited(houseIndex)
            }

            Result.success(detail)
        } catch (e: Exception) {
            Result.error("하우스 정보를 불러올 수 없습니다", e)
        }
    }
}
