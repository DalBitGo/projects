package com.example.celestialsanctuary.ui.screen.fortune

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.celestialsanctuary.data.FortuneRepository
import com.example.celestialsanctuary.util.SoundManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import java.util.Calendar
import javax.inject.Inject
import kotlin.random.Random

/**
 * 일일 운세 UI 상태
 */
data class DailyFortuneUiState(
    // 수정구슬
    val crystalBallResult: CrystalBallResult? = null,
    val crystalBallRevealed: Boolean = false,

    // 타로카드
    val tarotCards: List<TarotCard> = emptyList(),
    val selectedTarotIndex: Int? = null,
    val tarotRevealed: Boolean = false,

    // 주사위
    val diceResult: DiceResult? = null,
    val diceRolled: Boolean = false,

    // 추가 정보
    val isNewDay: Boolean = true,
    val streakDays: Int = 0,
    val allFortuneRevealed: Boolean = false
)

/**
 * 수정구슬 결과
 */
data class CrystalBallResult(
    val message: String,
    val luckyNumbers: List<Int>,
    val luckyColor: String,
    val luckyDirection: String
)

/**
 * 타로카드
 */
data class TarotCard(
    val id: Int,
    val name: String,
    val symbol: String,
    val meaning: String
) {
    companion object {
        val defaultDeck = listOf(
            TarotCard(0, "바보", "🃏", "새로운 시작과 무한한 가능성. 두려움 없이 첫 발을 내딛으세요."),
            TarotCard(1, "마법사", "🎭", "당신 안에 모든 것을 창조할 힘이 있습니다. 의지를 행동으로 옮기세요."),
            TarotCard(2, "여사제", "🌙", "직감을 믿으세요. 답은 이미 당신 안에 있습니다."),
            TarotCard(3, "여황제", "👑", "풍요와 창조의 에너지가 당신을 감싸고 있습니다."),
            TarotCard(4, "황제", "🏰", "리더십을 발휘할 때입니다. 구조와 질서를 세우세요."),
            TarotCard(5, "교황", "📿", "전통과 지혜를 존중하세요. 멘토의 조언에 귀 기울이세요."),
            TarotCard(6, "연인", "💕", "중요한 선택의 기로에 섰습니다. 마음의 소리를 따르세요."),
            TarotCard(7, "전차", "⚔️", "승리가 가까이 있습니다. 결단력 있게 전진하세요."),
            TarotCard(8, "힘", "🦁", "내면의 힘을 믿으세요. 부드러움이 진정한 강함입니다."),
            TarotCard(9, "은둔자", "🏮", "내면을 들여다볼 시간입니다. 고요 속에서 답을 찾으세요."),
            TarotCard(10, "운명의 수레바퀴", "☸️", "변화의 바람이 불고 있습니다. 흐름에 몸을 맡기세요."),
            TarotCard(11, "정의", "⚖️", "공정함과 균형을 추구하세요. 진실이 드러날 것입니다."),
            TarotCard(12, "매달린 사람", "🙃", "다른 관점에서 바라보세요. 희생이 깨달음을 가져옵니다."),
            TarotCard(13, "죽음", "🦋", "변화를 두려워하지 마세요. 끝은 새로운 시작입니다."),
            TarotCard(14, "절제", "⚗️", "균형과 조화를 찾으세요. 인내가 열매를 맺습니다."),
            TarotCard(15, "악마", "⛓️", "두려움에서 벗어나세요. 당신을 묶는 것은 환상입니다."),
            TarotCard(16, "탑", "🗼", "갑작스러운 변화가 해방을 가져옵니다. 낡은 것을 버리세요."),
            TarotCard(17, "별", "⭐", "희망을 잃지 마세요. 빛은 어둠 속에서 더 빛납니다."),
            TarotCard(18, "달", "🌕", "직감에 귀 기울이세요. 숨겨진 것이 드러날 것입니다."),
            TarotCard(19, "태양", "☀️", "기쁨과 성공이 당신을 기다립니다. 빛나는 시간입니다."),
            TarotCard(20, "심판", "📯", "과거를 돌아보고 새로운 결심을 하세요. 부활의 때입니다."),
            TarotCard(21, "세계", "🌍", "완성과 성취의 순간입니다. 다음 여정을 준비하세요.")
        )
    }
}

/**
 * 주사위 결과
 */
data class DiceResult(
    val numbers: List<Int>,
    val interpretation: String,
    val luckyLevel: Int // 1-5
)

@HiltViewModel
class DailyFortuneViewModel @Inject constructor(
    application: Application
) : AndroidViewModel(application) {

    private val repository = FortuneRepository(application)
    private val soundManager = SoundManager.getInstance(application)

    private val _uiState = MutableStateFlow(DailyFortuneUiState())
    val uiState: StateFlow<DailyFortuneUiState> = _uiState.asStateFlow()

    // 일관된 결과를 위한 시드 (날짜 기반)
    private val dailySeed = Calendar.getInstance().run {
        get(Calendar.YEAR) * 10000 + get(Calendar.DAY_OF_YEAR)
    }

    init {
        loadSavedFortunes()
    }

    /**
     * 저장된 운세 데이터 로드
     */
    private fun loadSavedFortunes() {
        viewModelScope.launch {
            // 일일 접속 업데이트
            repository.updateDailyAccess()

            // 타로 카드 초기화 (날짜 기반 시드로 섞기)
            val shuffledCards = TarotCard.defaultDeck.shuffled(Random(dailySeed)).take(3)

            // 저장된 데이터 로드
            val isNewDay = repository.isNewDay.first()
            val streakDays = repository.streakDays.first()
            val crystalRevealed = repository.crystalBallRevealed.first()
            val tarotRevealed = repository.tarotRevealed.first()
            val diceRolled = repository.diceRolled.first()
            val allRevealed = repository.allFortuneRevealed.first()

            // 저장된 결과 로드
            val savedCrystal = repository.savedCrystalBallResult.first()
            val savedTarot = repository.savedTarotResult.first()
            val savedDice = repository.savedDiceResult.first()

            // 타로 카드 - 저장된 카드 ID가 있으면 그것 사용
            val tarotCards = if (savedTarot != null) {
                savedTarot.cardIds.map { id ->
                    TarotCard.defaultDeck.find { it.id == id } ?: shuffledCards[0]
                }
            } else {
                shuffledCards
            }

            _uiState.value = DailyFortuneUiState(
                crystalBallResult = savedCrystal?.let {
                    CrystalBallResult(
                        message = it.message,
                        luckyNumbers = it.luckyNumbers,
                        luckyColor = it.luckyColor,
                        luckyDirection = it.luckyDirection
                    )
                },
                crystalBallRevealed = crystalRevealed,
                tarotCards = tarotCards,
                selectedTarotIndex = savedTarot?.selectedIndex,
                tarotRevealed = tarotRevealed,
                diceResult = savedDice?.let {
                    DiceResult(
                        numbers = it.numbers,
                        interpretation = it.interpretation,
                        luckyLevel = it.luckyLevel
                    )
                },
                diceRolled = diceRolled,
                isNewDay = isNewDay,
                streakDays = streakDays,
                allFortuneRevealed = allRevealed
            )
        }
    }

    /**
     * 수정구슬 흔들기 햅틱 피드백
     */
    fun onCrystalBallShake() {
        soundManager.hapticShake()
    }

    /**
     * 수정구슬 결과 공개
     */
    fun revealCrystalBall() {
        soundManager.hapticSuccess()
        val random = Random(dailySeed)

        val messages = listOf(
            "오늘은 당신의 직감이 특별히 날카로운 날입니다. 첫 번째 느낌을 믿으세요.",
            "예상치 못한 좋은 소식이 찾아올 것입니다. 마음을 열고 기다리세요.",
            "과거의 노력이 결실을 맺기 시작합니다. 조금만 더 인내하세요.",
            "새로운 만남이 당신의 인생을 바꿀 수 있습니다. 열린 마음을 가지세요.",
            "창의적인 에너지가 넘치는 날입니다. 새로운 아이디어를 실행해보세요.",
            "내면의 평화를 찾는 것이 중요한 날입니다. 잠시 멈추고 호흡하세요.",
            "당신의 말에 힘이 실리는 날입니다. 진심을 담아 표현하세요.",
            "숨겨진 기회가 모습을 드러낼 것입니다. 주의 깊게 살펴보세요.",
            "오래된 관계가 새롭게 피어날 수 있습니다. 먼저 손을 내밀어보세요.",
            "자신을 돌보는 시간을 가지세요. 휴식도 성장의 일부입니다.",
            "도전을 두려워하지 마세요. 별들이 당신의 용기를 응원합니다.",
            "작은 변화가 큰 결과를 가져올 것입니다. 한 걸음씩 나아가세요."
        )

        val colors = listOf("보라색", "금색", "은색", "파란색", "초록색", "분홍색", "하얀색", "주황색")
        val directions = listOf("동쪽", "서쪽", "남쪽", "북쪽", "동북", "동남", "서북", "서남")

        val message = messages[random.nextInt(messages.size)]
        val luckyNumbers = List(3) { random.nextInt(1, 46) }.sorted()
        val luckyColor = colors[random.nextInt(colors.size)]
        val luckyDirection = directions[random.nextInt(directions.size)]

        val result = CrystalBallResult(
            message = message,
            luckyNumbers = luckyNumbers,
            luckyColor = luckyColor,
            luckyDirection = luckyDirection
        )

        _uiState.value = _uiState.value.copy(
            crystalBallResult = result,
            crystalBallRevealed = true
        )

        // 저장
        viewModelScope.launch {
            repository.saveCrystalBallResult(
                message = message,
                luckyNumbers = luckyNumbers,
                luckyColor = luckyColor,
                luckyDirection = luckyDirection
            )
            checkAllRevealed()
        }
    }

    /**
     * 타로카드 선택
     */
    fun selectTarotCard(index: Int) {
        soundManager.hapticCardFlip()
        _uiState.value = _uiState.value.copy(
            selectedTarotIndex = index,
            tarotRevealed = true
        )

        // 저장
        viewModelScope.launch {
            repository.saveTarotResult(
                cardIds = _uiState.value.tarotCards.map { it.id },
                selectedIndex = index
            )
            checkAllRevealed()
        }
    }

    /**
     * 주사위 굴리기
     */
    fun rollDice() {
        soundManager.hapticDiceRoll()
        val random = Random(dailySeed + 100) // 수정구슬과 다른 결과를 위해

        val numbers = List(3) { random.nextInt(1, 7) }
        val sum = numbers.sum()

        val (interpretation, level) = when {
            numbers.distinct().size == 1 -> "트리플! 대단한 행운의 날입니다. 무엇이든 시도해보세요!" to 5
            sum >= 15 -> "높은 숫자! 적극적으로 행동하면 좋은 결과가 있을 것입니다." to 4
            sum >= 11 -> "균형 잡힌 에너지. 차분하게 계획을 실행하세요." to 3
            sum >= 7 -> "조심스러운 하루. 중요한 결정은 미루는 것이 좋겠습니다." to 2
            else -> "휴식이 필요한 날. 무리하지 말고 에너지를 충전하세요." to 1
        }

        val result = DiceResult(
            numbers = numbers,
            interpretation = interpretation,
            luckyLevel = level
        )

        _uiState.value = _uiState.value.copy(
            diceResult = result,
            diceRolled = true
        )

        // 저장
        viewModelScope.launch {
            repository.saveDiceResult(
                numbers = numbers,
                interpretation = interpretation,
                luckyLevel = level
            )
            checkAllRevealed()
        }
    }

    /**
     * 모든 운세 확인 여부 체크
     */
    private suspend fun checkAllRevealed() {
        val allRevealed = repository.allFortuneRevealed.first()
        _uiState.value = _uiState.value.copy(allFortuneRevealed = allRevealed)
    }

    /**
     * 모든 결과 리셋 (다음 날 자동 리셋용)
     */
    fun resetAll() {
        val shuffledCards = TarotCard.defaultDeck.shuffled(Random(dailySeed)).take(3)
        _uiState.value = DailyFortuneUiState(tarotCards = shuffledCards)
    }
}
