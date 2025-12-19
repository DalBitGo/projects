package com.example.celestialsanctuary.data

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.intPreferencesKey
import androidx.datastore.preferences.core.longPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import java.util.Calendar

/**
 * 운세 데이터를 위한 DataStore 확장
 */
val Context.fortuneDataStore: DataStore<Preferences> by preferencesDataStore(
    name = "fortune_preferences"
)

/**
 * 운세 저장 키 정의
 */
object FortunePreferences {
    // 마지막 운세 확인 날짜 (YYYYDDD 형식: 년도 + 일차)
    val LAST_FORTUNE_DATE = intPreferencesKey("last_fortune_date")

    // 수정구슬 관련
    val CRYSTAL_BALL_REVEALED = booleanPreferencesKey("crystal_ball_revealed")
    val CRYSTAL_BALL_MESSAGE = stringPreferencesKey("crystal_ball_message")
    val CRYSTAL_BALL_LUCKY_NUMBERS = stringPreferencesKey("crystal_ball_lucky_numbers")
    val CRYSTAL_BALL_LUCKY_COLOR = stringPreferencesKey("crystal_ball_lucky_color")
    val CRYSTAL_BALL_LUCKY_DIRECTION = stringPreferencesKey("crystal_ball_lucky_direction")

    // 타로카드 관련
    val TAROT_REVEALED = booleanPreferencesKey("tarot_revealed")
    val TAROT_SELECTED_INDEX = intPreferencesKey("tarot_selected_index")
    val TAROT_CARD_IDS = stringPreferencesKey("tarot_card_ids") // 콤마로 구분된 카드 ID

    // 주사위 관련
    val DICE_ROLLED = booleanPreferencesKey("dice_rolled")
    val DICE_NUMBERS = stringPreferencesKey("dice_numbers") // 콤마로 구분된 숫자
    val DICE_INTERPRETATION = stringPreferencesKey("dice_interpretation")
    val DICE_LUCKY_LEVEL = intPreferencesKey("dice_lucky_level")

    // 연속 접속 기록
    val STREAK_DAYS = intPreferencesKey("streak_days")
    val LAST_STREAK_DATE = intPreferencesKey("last_streak_date")
}

/**
 * 운세 저장소 - DataStore를 사용한 일일 운세 데이터 관리
 */
class FortuneRepository(private val context: Context) {

    private val dataStore = context.fortuneDataStore

    /**
     * 현재 날짜 코드 반환 (YYYYDDD 형식)
     */
    private fun getTodayCode(): Int {
        return Calendar.getInstance().run {
            get(Calendar.YEAR) * 1000 + get(Calendar.DAY_OF_YEAR)
        }
    }

    /**
     * 오늘 처음 접속인지 확인
     */
    val isNewDay: Flow<Boolean> = dataStore.data.map { prefs ->
        val lastDate = prefs[FortunePreferences.LAST_FORTUNE_DATE] ?: 0
        lastDate != getTodayCode()
    }

    /**
     * 연속 접속 일수
     */
    val streakDays: Flow<Int> = dataStore.data.map { prefs ->
        prefs[FortunePreferences.STREAK_DAYS] ?: 0
    }

    /**
     * 수정구슬 공개 여부
     */
    val crystalBallRevealed: Flow<Boolean> = dataStore.data.map { prefs ->
        val lastDate = prefs[FortunePreferences.LAST_FORTUNE_DATE] ?: 0
        if (lastDate != getTodayCode()) {
            false // 새로운 날이면 리셋
        } else {
            prefs[FortunePreferences.CRYSTAL_BALL_REVEALED] ?: false
        }
    }

    /**
     * 타로카드 공개 여부
     */
    val tarotRevealed: Flow<Boolean> = dataStore.data.map { prefs ->
        val lastDate = prefs[FortunePreferences.LAST_FORTUNE_DATE] ?: 0
        if (lastDate != getTodayCode()) {
            false
        } else {
            prefs[FortunePreferences.TAROT_REVEALED] ?: false
        }
    }

    /**
     * 주사위 굴림 여부
     */
    val diceRolled: Flow<Boolean> = dataStore.data.map { prefs ->
        val lastDate = prefs[FortunePreferences.LAST_FORTUNE_DATE] ?: 0
        if (lastDate != getTodayCode()) {
            false
        } else {
            prefs[FortunePreferences.DICE_ROLLED] ?: false
        }
    }

    /**
     * 저장된 수정구슬 결과
     */
    data class SavedCrystalBallResult(
        val message: String,
        val luckyNumbers: List<Int>,
        val luckyColor: String,
        val luckyDirection: String
    )

    val savedCrystalBallResult: Flow<SavedCrystalBallResult?> = dataStore.data.map { prefs ->
        val lastDate = prefs[FortunePreferences.LAST_FORTUNE_DATE] ?: 0
        if (lastDate != getTodayCode()) {
            null
        } else {
            val message = prefs[FortunePreferences.CRYSTAL_BALL_MESSAGE]
            if (message != null) {
                SavedCrystalBallResult(
                    message = message,
                    luckyNumbers = prefs[FortunePreferences.CRYSTAL_BALL_LUCKY_NUMBERS]?.split(",")?.map { it.toInt() } ?: emptyList(),
                    luckyColor = prefs[FortunePreferences.CRYSTAL_BALL_LUCKY_COLOR] ?: "",
                    luckyDirection = prefs[FortunePreferences.CRYSTAL_BALL_LUCKY_DIRECTION] ?: ""
                )
            } else null
        }
    }

    /**
     * 저장된 주사위 결과
     */
    data class SavedDiceResult(
        val numbers: List<Int>,
        val interpretation: String,
        val luckyLevel: Int
    )

    val savedDiceResult: Flow<SavedDiceResult?> = dataStore.data.map { prefs ->
        val lastDate = prefs[FortunePreferences.LAST_FORTUNE_DATE] ?: 0
        if (lastDate != getTodayCode()) {
            null
        } else {
            val numbers = prefs[FortunePreferences.DICE_NUMBERS]
            if (numbers != null) {
                SavedDiceResult(
                    numbers = numbers.split(",").map { it.toInt() },
                    interpretation = prefs[FortunePreferences.DICE_INTERPRETATION] ?: "",
                    luckyLevel = prefs[FortunePreferences.DICE_LUCKY_LEVEL] ?: 0
                )
            } else null
        }
    }

    /**
     * 저장된 타로 결과
     */
    data class SavedTarotResult(
        val cardIds: List<Int>,
        val selectedIndex: Int
    )

    val savedTarotResult: Flow<SavedTarotResult?> = dataStore.data.map { prefs ->
        val lastDate = prefs[FortunePreferences.LAST_FORTUNE_DATE] ?: 0
        if (lastDate != getTodayCode()) {
            null
        } else {
            val cardIds = prefs[FortunePreferences.TAROT_CARD_IDS]
            val selectedIndex = prefs[FortunePreferences.TAROT_SELECTED_INDEX]
            if (cardIds != null && selectedIndex != null) {
                SavedTarotResult(
                    cardIds = cardIds.split(",").map { it.toInt() },
                    selectedIndex = selectedIndex
                )
            } else null
        }
    }

    /**
     * 오늘 날짜로 업데이트 및 연속 접속 체크
     */
    suspend fun updateDailyAccess() {
        dataStore.edit { prefs ->
            val todayCode = getTodayCode()
            val lastDate = prefs[FortunePreferences.LAST_FORTUNE_DATE] ?: 0
            val lastStreakDate = prefs[FortunePreferences.LAST_STREAK_DATE] ?: 0

            // 연속 접속 계산
            if (lastDate != todayCode) {
                // 새로운 날
                val yesterdayCode = Calendar.getInstance().run {
                    add(Calendar.DAY_OF_YEAR, -1)
                    get(Calendar.YEAR) * 1000 + get(Calendar.DAY_OF_YEAR)
                }

                val currentStreak = prefs[FortunePreferences.STREAK_DAYS] ?: 0
                val newStreak = if (lastStreakDate == yesterdayCode) {
                    currentStreak + 1  // 연속 접속
                } else {
                    1  // 연속 끊김, 새로 시작
                }

                prefs[FortunePreferences.STREAK_DAYS] = newStreak
                prefs[FortunePreferences.LAST_STREAK_DATE] = todayCode

                // 새로운 날이면 운세 결과 초기화
                prefs[FortunePreferences.CRYSTAL_BALL_REVEALED] = false
                prefs[FortunePreferences.TAROT_REVEALED] = false
                prefs[FortunePreferences.DICE_ROLLED] = false

                prefs[FortunePreferences.LAST_FORTUNE_DATE] = todayCode
            }
        }
    }

    /**
     * 수정구슬 결과 저장
     */
    suspend fun saveCrystalBallResult(
        message: String,
        luckyNumbers: List<Int>,
        luckyColor: String,
        luckyDirection: String
    ) {
        dataStore.edit { prefs ->
            prefs[FortunePreferences.LAST_FORTUNE_DATE] = getTodayCode()
            prefs[FortunePreferences.CRYSTAL_BALL_REVEALED] = true
            prefs[FortunePreferences.CRYSTAL_BALL_MESSAGE] = message
            prefs[FortunePreferences.CRYSTAL_BALL_LUCKY_NUMBERS] = luckyNumbers.joinToString(",")
            prefs[FortunePreferences.CRYSTAL_BALL_LUCKY_COLOR] = luckyColor
            prefs[FortunePreferences.CRYSTAL_BALL_LUCKY_DIRECTION] = luckyDirection
        }
    }

    /**
     * 타로카드 결과 저장
     */
    suspend fun saveTarotResult(cardIds: List<Int>, selectedIndex: Int) {
        dataStore.edit { prefs ->
            prefs[FortunePreferences.LAST_FORTUNE_DATE] = getTodayCode()
            prefs[FortunePreferences.TAROT_REVEALED] = true
            prefs[FortunePreferences.TAROT_CARD_IDS] = cardIds.joinToString(",")
            prefs[FortunePreferences.TAROT_SELECTED_INDEX] = selectedIndex
        }
    }

    /**
     * 주사위 결과 저장
     */
    suspend fun saveDiceResult(numbers: List<Int>, interpretation: String, luckyLevel: Int) {
        dataStore.edit { prefs ->
            prefs[FortunePreferences.LAST_FORTUNE_DATE] = getTodayCode()
            prefs[FortunePreferences.DICE_ROLLED] = true
            prefs[FortunePreferences.DICE_NUMBERS] = numbers.joinToString(",")
            prefs[FortunePreferences.DICE_INTERPRETATION] = interpretation
            prefs[FortunePreferences.DICE_LUCKY_LEVEL] = luckyLevel
        }
    }

    /**
     * 모든 운세 저장 확인 (세 가지 다 했는지)
     */
    val allFortuneRevealed: Flow<Boolean> = dataStore.data.map { prefs ->
        val lastDate = prefs[FortunePreferences.LAST_FORTUNE_DATE] ?: 0
        if (lastDate != getTodayCode()) {
            false
        } else {
            val crystalBall = prefs[FortunePreferences.CRYSTAL_BALL_REVEALED] ?: false
            val tarot = prefs[FortunePreferences.TAROT_REVEALED] ?: false
            val dice = prefs[FortunePreferences.DICE_ROLLED] ?: false
            crystalBall && tarot && dice
        }
    }
}
