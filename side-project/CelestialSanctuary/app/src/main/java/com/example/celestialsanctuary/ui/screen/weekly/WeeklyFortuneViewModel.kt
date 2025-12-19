package com.example.celestialsanctuary.ui.screen.weekly

import androidx.lifecycle.ViewModel
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale
import javax.inject.Inject
import kotlin.random.Random

/**
 * 일별 운세 데이터
 */
data class DayFortune(
    val dayOfWeek: String,
    val dayOfMonth: Int,
    val fullDate: String,
    val fortuneLevel: Int, // 1-5
    val generalFortune: String,
    val loveFortune: String,
    val moneyFortune: String,
    val healthFortune: String,
    val advice: String,
    val luckyColor: String,
    val luckyNumber: Int,
    val luckyDirection: String
)

/**
 * 주간 운세 UI 상태
 */
data class WeeklyFortuneUiState(
    val weekRange: String = "",
    val days: List<DayFortune> = emptyList(),
    val todayIndex: Int = 0
)

@HiltViewModel
class WeeklyFortuneViewModel @Inject constructor() : ViewModel() {

    private val _uiState = MutableStateFlow(WeeklyFortuneUiState())
    val uiState: StateFlow<WeeklyFortuneUiState> = _uiState.asStateFlow()

    private val koreanDays = listOf("일", "월", "화", "수", "목", "금", "토")

    private val generalFortuneMessages = listOf(
        "오늘은 새로운 기회가 찾아오는 날입니다. 주변을 잘 살펴보세요.",
        "차분하게 하루를 시작하면 좋은 일이 생길 것입니다.",
        "작은 변화가 큰 행운을 불러올 수 있습니다.",
        "직감을 믿으세요. 오늘 당신의 선택은 옳습니다.",
        "긍정적인 에너지가 가득한 하루가 될 것입니다.",
        "예상치 못한 곳에서 도움의 손길이 올 것입니다.",
        "오래된 관계에서 새로운 발견을 할 수 있는 날입니다.",
        "창의력이 빛나는 하루입니다. 아이디어를 적어두세요.",
        "인내심이 보상받는 날입니다. 조금만 더 힘내세요.",
        "오늘 시작한 일은 좋은 결실을 맺을 것입니다."
    )

    private val loveFortuneMessages = listOf(
        "연인과 깊은 대화를 나누기 좋은 날입니다.",
        "새로운 만남의 기회가 있을 수 있습니다.",
        "솔직한 감정 표현이 관계를 더 깊게 할 것입니다.",
        "오래된 친구에게서 설렘을 느낄 수도 있습니다.",
        "혼자만의 시간도 사랑의 일부입니다.",
        "작은 배려가 큰 감동을 줄 수 있는 날입니다.",
        "과거의 상처를 치유할 수 있는 기회가 올 것입니다.",
        "진심 어린 관심이 상대방에게 전해질 것입니다.",
        "사랑에 대한 고정관념을 버려보세요.",
        "오늘의 만남이 특별한 인연이 될 수 있습니다."
    )

    private val moneyFortuneMessages = listOf(
        "예상치 못한 금전적 이득이 있을 수 있습니다.",
        "절약보다는 현명한 투자에 집중하세요.",
        "작은 지출도 신중하게 생각하는 것이 좋습니다.",
        "재물 운이 상승하고 있습니다.",
        "새로운 수입원을 찾아볼 좋은 시기입니다.",
        "빌려준 돈이 돌아올 수 있는 날입니다.",
        "충동구매를 자제하면 좋을 것 같습니다.",
        "사업적 결정에 좋은 날입니다.",
        "금전 관련 좋은 소식이 올 수 있습니다.",
        "장기적인 재무 계획을 세우기 좋은 날입니다."
    )

    private val healthFortuneMessages = listOf(
        "가벼운 운동이 활력을 불어넣어 줄 것입니다.",
        "충분한 수면이 필요한 하루입니다.",
        "스트레스 관리에 신경 쓰세요.",
        "건강한 식단이 몸과 마음을 회복시킬 것입니다.",
        "야외 활동이 도움이 되는 날입니다.",
        "무리하지 말고 휴식을 취하세요.",
        "명상이나 요가를 시도해보면 좋겠습니다.",
        "규칙적인 생활 리듬이 중요한 날입니다.",
        "몸의 신호에 귀 기울여 주세요.",
        "건강 검진을 미루고 있다면 예약해보세요."
    )

    private val adviceMessages = listOf(
        "하루를 마무리하며 감사한 일 세 가지를 떠올려보세요.",
        "지금 이 순간에 집중하세요. 과거와 미래는 잠시 내려놓으세요.",
        "당신은 생각보다 강한 사람입니다.",
        "작은 성취도 축하받을 자격이 있습니다.",
        "실패는 성공의 디딤돌입니다. 두려워하지 마세요.",
        "변화를 두려워하지 마세요. 성장의 기회입니다.",
        "당신의 가치는 타인의 평가로 결정되지 않습니다.",
        "오늘 하루도 최선을 다한 자신을 칭찬해주세요.",
        "어려운 상황에서도 유머를 잃지 마세요.",
        "완벽하지 않아도 괜찮습니다. 당신은 이미 충분합니다."
    )

    private val colors = listOf("빨강", "주황", "노랑", "초록", "파랑", "보라", "분홍", "하양", "금색", "은색")
    private val directions = listOf("동쪽", "서쪽", "남쪽", "북쪽", "동북", "동남", "서북", "서남")

    init {
        generateWeeklyFortune()
    }

    private fun generateWeeklyFortune() {
        val calendar = Calendar.getInstance()
        val dateFormat = SimpleDateFormat("M월 d일 (E)", Locale.KOREAN)
        val rangeFormat = SimpleDateFormat("M/d", Locale.KOREAN)

        // 이번 주 월요일로 이동
        val dayOfWeek = calendar.get(Calendar.DAY_OF_WEEK)
        val daysFromMonday = if (dayOfWeek == Calendar.SUNDAY) 6 else dayOfWeek - Calendar.MONDAY
        calendar.add(Calendar.DAY_OF_MONTH, -daysFromMonday)

        val weekStart = rangeFormat.format(calendar.time)
        val todayCalendar = Calendar.getInstance()
        var todayIndex = 0

        val days = mutableListOf<DayFortune>()

        for (i in 0 until 7) {
            if (i > 0) {
                calendar.add(Calendar.DAY_OF_MONTH, 1)
            }

            // 오늘인지 확인
            if (calendar.get(Calendar.YEAR) == todayCalendar.get(Calendar.YEAR) &&
                calendar.get(Calendar.DAY_OF_YEAR) == todayCalendar.get(Calendar.DAY_OF_YEAR)
            ) {
                todayIndex = i
            }

            // 날짜 기반 시드로 일관된 결과 생성
            val seed = calendar.get(Calendar.YEAR) * 10000 + calendar.get(Calendar.DAY_OF_YEAR)
            val random = Random(seed)

            days.add(
                DayFortune(
                    dayOfWeek = koreanDays[(calendar.get(Calendar.DAY_OF_WEEK) + 5) % 7],
                    dayOfMonth = calendar.get(Calendar.DAY_OF_MONTH),
                    fullDate = dateFormat.format(calendar.time),
                    fortuneLevel = random.nextInt(1, 6),
                    generalFortune = generalFortuneMessages[random.nextInt(generalFortuneMessages.size)],
                    loveFortune = loveFortuneMessages[random.nextInt(loveFortuneMessages.size)],
                    moneyFortune = moneyFortuneMessages[random.nextInt(moneyFortuneMessages.size)],
                    healthFortune = healthFortuneMessages[random.nextInt(healthFortuneMessages.size)],
                    advice = adviceMessages[random.nextInt(adviceMessages.size)],
                    luckyColor = colors[random.nextInt(colors.size)],
                    luckyNumber = random.nextInt(1, 100),
                    luckyDirection = directions[random.nextInt(directions.size)]
                )
            )
        }

        // 주 범위 설정
        calendar.add(Calendar.DAY_OF_MONTH, -6) // 다시 월요일로
        calendar.add(Calendar.DAY_OF_MONTH, 6) // 일요일로
        val weekEnd = rangeFormat.format(calendar.time)

        _uiState.value = WeeklyFortuneUiState(
            weekRange = "$weekStart ~ $weekEnd",
            days = days,
            todayIndex = todayIndex
        )
    }
}
