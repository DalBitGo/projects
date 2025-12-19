package com.example.celestialsanctuary.ui.screen.monthly

import androidx.lifecycle.ViewModel
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.Calendar
import javax.inject.Inject
import kotlin.random.Random

/**
 * 월간 운세 데이터
 */
data class MonthlyFortune(
    val year: Int,
    val month: Int,
    val monthName: String,
    val theme: String,
    val overallFortune: String,
    val fortuneLevel: Int,  // 1-5
    val weeklyHighlights: List<WeekHighlight>,
    val luckyDays: List<Int>,
    val cautionDays: List<Int>,
    val luckyColor: String,
    val luckyNumber: Int,
    val luckyItem: String,
    val specialEvent: String?
)

/**
 * 주차별 하이라이트
 */
data class WeekHighlight(
    val weekNumber: Int,
    val dateRange: String,
    val focus: String,
    val advice: String,
    val energyLevel: Int  // 1-5
)

/**
 * 월간 운세 UI 상태
 */
data class MonthlyFortuneUiState(
    val currentMonth: MonthlyFortune? = null,
    val nextMonth: MonthlyFortune? = null,
    val selectedTab: Int = 0  // 0: 이번 달, 1: 다음 달
)

@HiltViewModel
class MonthlyFortuneViewModel @Inject constructor() : ViewModel() {

    private val _uiState = MutableStateFlow(MonthlyFortuneUiState())
    val uiState: StateFlow<MonthlyFortuneUiState> = _uiState.asStateFlow()

    private val monthNames = listOf(
        "1월", "2월", "3월", "4월", "5월", "6월",
        "7월", "8월", "9월", "10월", "11월", "12월"
    )

    private val themes = listOf(
        "새로운 시작", "성장과 발전", "관계의 깊이", "창의적 에너지",
        "안정과 평화", "도전과 모험", "내면의 성찰", "풍요와 수확",
        "변화의 바람", "완성과 마무리", "희망의 빛", "감사와 나눔"
    )

    private val luckyItems = listOf(
        "자수정", "호박 목걸이", "은반지", "행운의 동전", "사엽 클로버",
        "수정 구슬", "별 모양 액세서리", "달 펜던트", "태양석", "터키석",
        "장미 쿼츠", "라벤더 향초"
    )

    private val specialEvents = listOf(
        "보름달 - 소원을 빌기 좋은 날",
        "수성 역행 종료 - 커뮤니케이션이 원활해집니다",
        "금성이 사자자리 진입 - 로맨스 운이 상승합니다",
        "목성과 토성의 합 - 큰 결정을 내리기 좋은 시기",
        "개기 월식 - 감정의 정화가 일어납니다",
        null, null, null // 일부 달에는 특별 이벤트 없음
    )

    init {
        generateMonthlyForecasts()
    }

    private fun generateMonthlyForecasts() {
        val calendar = Calendar.getInstance()
        val currentYear = calendar.get(Calendar.YEAR)
        val currentMonth = calendar.get(Calendar.MONTH)

        val currentMonthFortune = generateMonthFortune(currentYear, currentMonth)

        // 다음 달 계산
        val nextMonthCal = Calendar.getInstance().apply {
            add(Calendar.MONTH, 1)
        }
        val nextYear = nextMonthCal.get(Calendar.YEAR)
        val nextMonth = nextMonthCal.get(Calendar.MONTH)
        val nextMonthFortune = generateMonthFortune(nextYear, nextMonth)

        _uiState.value = MonthlyFortuneUiState(
            currentMonth = currentMonthFortune,
            nextMonth = nextMonthFortune
        )
    }

    private fun generateMonthFortune(year: Int, month: Int): MonthlyFortune {
        val seed = year * 100 + month
        val random = Random(seed)

        val theme = themes[random.nextInt(themes.size)]
        val fortuneLevel = random.nextInt(3, 6) // 3-5

        val overallFortune = generateOverallFortune(theme, fortuneLevel, random)
        val weeklyHighlights = generateWeeklyHighlights(year, month, random)

        // 행운의 날 (3-5개)
        val luckyDays = List(random.nextInt(3, 6)) {
            random.nextInt(1, getDaysInMonth(year, month) + 1)
        }.distinct().sorted()

        // 주의할 날 (2-3개)
        val cautionDays = List(random.nextInt(2, 4)) {
            random.nextInt(1, getDaysInMonth(year, month) + 1)
        }.filter { it !in luckyDays }.distinct().sorted()

        val luckyColors = listOf("보라색", "금색", "은색", "파란색", "초록색", "분홍색", "하얀색", "남색")

        return MonthlyFortune(
            year = year,
            month = month + 1,
            monthName = monthNames[month],
            theme = theme,
            overallFortune = overallFortune,
            fortuneLevel = fortuneLevel,
            weeklyHighlights = weeklyHighlights,
            luckyDays = luckyDays,
            cautionDays = cautionDays,
            luckyColor = luckyColors[random.nextInt(luckyColors.size)],
            luckyNumber = random.nextInt(1, 100),
            luckyItem = luckyItems[random.nextInt(luckyItems.size)],
            specialEvent = specialEvents[random.nextInt(specialEvents.size)]
        )
    }

    private fun generateOverallFortune(theme: String, level: Int, random: Random): String {
        val fortunes = when {
            level >= 4 -> listOf(
                "이번 달은 '$theme'의 에너지가 강하게 흐르는 시기입니다. 별들이 당신의 편에 서서 원하는 바를 이루도록 도울 것입니다.",
                "'$theme'이라는 주제 아래, 이번 달은 당신에게 특별한 기회를 선사합니다. 직감을 믿고 과감히 행동하세요.",
                "우주가 '$theme'의 메시지를 보내고 있습니다. 이번 달은 긍정적인 변화와 성장이 기대되는 시기입니다."
            )
            else -> listOf(
                "'$theme'의 에너지가 조용히 흐르는 달입니다. 서두르지 말고 차분히 상황을 관찰하세요.",
                "이번 달은 '$theme'에 대해 깊이 생각해볼 시간입니다. 내면의 목소리에 귀 기울이세요.",
                "'$theme'의 흐름 속에서 균형을 찾아가는 시기입니다. 무리하지 않는 것이 중요합니다."
            )
        }
        return fortunes[random.nextInt(fortunes.size)]
    }

    private fun generateWeeklyHighlights(year: Int, month: Int, random: Random): List<WeekHighlight> {
        val calendar = Calendar.getInstance().apply {
            set(Calendar.YEAR, year)
            set(Calendar.MONTH, month)
            set(Calendar.DAY_OF_MONTH, 1)
        }

        val weeksInMonth = getWeeksInMonth(year, month)
        val focuses = listOf(
            "자기 계발", "인간관계", "재정 관리", "건강 관리", "창의성",
            "커뮤니케이션", "휴식과 충전", "목표 설정", "결단력", "감사 실천"
        )

        val advices = listOf(
            "새로운 것을 배우기 시작하세요",
            "오래된 친구에게 연락하세요",
            "지출 내역을 점검하세요",
            "규칙적인 운동을 시작하세요",
            "취미 활동에 시간을 투자하세요",
            "중요한 대화를 미루지 마세요",
            "충분한 수면을 취하세요",
            "이번 주의 목표를 명확히 하세요",
            "결정을 내려야 할 때입니다",
            "주변에 감사를 표현하세요"
        )

        return (1..weeksInMonth).map { weekNum ->
            val startDay = (weekNum - 1) * 7 + 1
            val endDay = minOf(weekNum * 7, getDaysInMonth(year, month))

            WeekHighlight(
                weekNumber = weekNum,
                dateRange = "${startDay}일 - ${endDay}일",
                focus = focuses[random.nextInt(focuses.size)],
                advice = advices[random.nextInt(advices.size)],
                energyLevel = random.nextInt(2, 6)
            )
        }
    }

    private fun getDaysInMonth(year: Int, month: Int): Int {
        val calendar = Calendar.getInstance().apply {
            set(Calendar.YEAR, year)
            set(Calendar.MONTH, month)
        }
        return calendar.getActualMaximum(Calendar.DAY_OF_MONTH)
    }

    private fun getWeeksInMonth(year: Int, month: Int): Int {
        val days = getDaysInMonth(year, month)
        return (days + 6) / 7
    }

    fun selectTab(tab: Int) {
        _uiState.value = _uiState.value.copy(selectedTab = tab)
    }
}
