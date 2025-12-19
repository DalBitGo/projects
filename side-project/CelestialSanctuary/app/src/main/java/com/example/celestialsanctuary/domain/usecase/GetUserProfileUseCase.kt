package com.example.celestialsanctuary.domain.usecase

import com.example.celestialsanctuary.data.repository.ChartRepository
import com.example.celestialsanctuary.data.repository.UserRepository
import com.example.celestialsanctuary.domain.model.Planet
import com.example.celestialsanctuary.domain.model.Result
import com.example.celestialsanctuary.domain.model.UserProfile
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.map
import javax.inject.Inject

/**
 * 사용자 프로필과 차트 정보를 가져오는 UseCase
 *
 * 책임:
 * - 사용자 프로필 조회
 * - 차트 정보 (태양/달/상승) 조회
 * - 오늘의 운세 생성
 */
class GetUserProfileUseCase @Inject constructor(
    private val userRepository: UserRepository,
    private val chartRepository: ChartRepository
) {
    /**
     * 사용자 프로필과 차트 정보 반환
     */
    operator fun invoke(): Flow<Result<UserProfileWithChart>> {
        return userRepository.userProfile.map { profile ->
            if (profile == null) {
                Result.error("프로필이 없습니다. 온보딩을 완료해주세요.")
            } else {
                val chart = chartRepository.getUserChart()
                // 달의 별자리는 planetPlacements에서 찾기
                val moonSign = chart?.planetPlacements
                    ?.find { it.planet == Planet.MOON }
                    ?.sign?.displayName
                Result.success(
                    UserProfileWithChart(
                        profile = profile,
                        sunSign = chart?.sunSign?.displayName,
                        moonSign = moonSign,
                        ascendant = chart?.ascendant?.displayName,
                        dailyFortune = generateDailyFortune()
                    )
                )
            }
        }.catch { e ->
            emit(Result.error("프로필을 불러올 수 없습니다", e))
        }
    }

    /**
     * 오늘의 운세 메시지 생성 (날짜 기반)
     */
    private fun generateDailyFortune(): String {
        val fortunes = listOf(
            "오늘은 창의적인 에너지가 넘치는 날입니다. 새로운 아이디어를 실행해보세요.",
            "주변 사람들과의 소통이 행운을 가져올 것입니다. 마음을 열어보세요.",
            "내면의 직감을 믿으세요. 별들이 당신의 편입니다.",
            "작은 것에서 기쁨을 찾는 날입니다. 감사의 마음을 가져보세요.",
            "변화의 기운이 감지됩니다. 새로운 기회에 열린 자세를 유지하세요.",
            "자신을 돌보는 시간을 가지세요. 휴식도 중요한 일입니다.",
            "숨겨진 재능이 빛날 수 있는 날입니다. 도전을 두려워하지 마세요.",
            "과거의 노력이 결실을 맺기 시작합니다. 인내심을 가지세요.",
            "우주가 당신에게 특별한 메시지를 보내고 있습니다. 주의 깊게 살펴보세요.",
            "사랑과 조화의 에너지가 당신을 감싸고 있습니다.",
            "목표를 향해 한 걸음 더 나아갈 때입니다. 용기를 내세요.",
            "오늘의 선택이 미래를 밝게 할 것입니다. 현명하게 결정하세요."
        )

        val dayOfYear = java.util.Calendar.getInstance().get(java.util.Calendar.DAY_OF_YEAR)
        return fortunes[dayOfYear % fortunes.size]
    }
}

/**
 * 사용자 프로필 + 차트 정보
 */
data class UserProfileWithChart(
    val profile: UserProfile,
    val sunSign: String?,
    val moonSign: String?,
    val ascendant: String?,
    val dailyFortune: String
)
