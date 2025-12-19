package com.example.celestialsanctuary.util

import android.content.Context
import android.media.AudioAttributes
import android.media.SoundPool
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import com.example.celestialsanctuary.R
import com.example.celestialsanctuary.notification.notificationDataStore
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch

/**
 * 사운드 및 햅틱 피드백 관리자
 * 앱 전체에서 일관된 사운드/진동 효과를 제공
 *
 * 필요한 사운드 파일 (res/raw/ 폴더에 추가):
 * - sound_tap.mp3        : 가벼운 탭 효과음
 * - sound_reveal.mp3     : 결과 공개 효과음 (신비로운 느낌)
 * - sound_card_flip.mp3  : 카드 뒤집는 효과음
 * - sound_dice_roll.mp3  : 주사위 굴리는 효과음
 * - sound_success.mp3    : 성공/축하 효과음
 * - sound_magic.mp3      : 마법 효과음 (수정구슬)
 * - sound_star.mp3       : 별 반짝임 효과음
 */
class SoundManager(private val context: Context) {

    companion object {
        // 설정 키
        val SOUND_ENABLED = booleanPreferencesKey("sound_enabled")
        val HAPTIC_ENABLED = booleanPreferencesKey("haptic_enabled")

        // 사운드 타입
        const val SOUND_TAP = 0
        const val SOUND_REVEAL = 1
        const val SOUND_CARD_FLIP = 2
        const val SOUND_DICE_ROLL = 3
        const val SOUND_SUCCESS = 4
        const val SOUND_MAGIC = 5
        const val SOUND_STAR = 6

        @Volatile
        private var instance: SoundManager? = null

        fun getInstance(context: Context): SoundManager {
            return instance ?: synchronized(this) {
                instance ?: SoundManager(context.applicationContext).also { instance = it }
            }
        }
    }

    private var soundPool: SoundPool? = null
    private val soundIds = mutableMapOf<Int, Int>()
    private var soundsLoaded = false
    private var soundEnabled = true
    private var hapticEnabled = true

    private val vibrator: Vibrator by lazy {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            val vibratorManager = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as VibratorManager
            vibratorManager.defaultVibrator
        } else {
            @Suppress("DEPRECATION")
            context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
        }
    }

    init {
        initializeSoundPool()
        loadSettings()
    }

    private fun initializeSoundPool() {
        val audioAttributes = AudioAttributes.Builder()
            .setUsage(AudioAttributes.USAGE_GAME)
            .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
            .build()

        soundPool = SoundPool.Builder()
            .setMaxStreams(4)
            .setAudioAttributes(audioAttributes)
            .build()

        soundPool?.setOnLoadCompleteListener { _, _, status ->
            if (status == 0) {
                soundsLoaded = true
            }
        }

        // 사운드 파일 로드 (리소스 파일이 있으면 로드)
        loadSoundIfExists(SOUND_TAP, "sound_tap")
        loadSoundIfExists(SOUND_REVEAL, "sound_reveal")
        loadSoundIfExists(SOUND_CARD_FLIP, "sound_card_flip")
        loadSoundIfExists(SOUND_DICE_ROLL, "sound_dice_roll")
        loadSoundIfExists(SOUND_SUCCESS, "sound_success")
        loadSoundIfExists(SOUND_MAGIC, "sound_magic")
        loadSoundIfExists(SOUND_STAR, "sound_star")
    }

    /**
     * 리소스가 존재하면 사운드 로드
     */
    private fun loadSoundIfExists(soundType: Int, resourceName: String) {
        try {
            val resId = context.resources.getIdentifier(resourceName, "raw", context.packageName)
            if (resId != 0) {
                soundIds[soundType] = soundPool?.load(context, resId, 1) ?: 0
            }
        } catch (e: Exception) {
            // 리소스가 없으면 무시
        }
    }

    private fun loadSettings() {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val prefs = context.notificationDataStore.data.first()
                soundEnabled = prefs[SOUND_ENABLED] ?: true
                hapticEnabled = prefs[HAPTIC_ENABLED] ?: true
            } catch (e: Exception) {
                // 기본값 사용
            }
        }
    }

    /**
     * 사운드 재생
     */
    fun playSound(soundType: Int, volume: Float = 1.0f) {
        if (!soundEnabled) return

        val soundId = soundIds[soundType] ?: return
        soundPool?.play(soundId, volume, volume, 1, 0, 1.0f)
    }

    /**
     * 햅틱 피드백 - 탭
     */
    fun hapticTap() {
        playSound(SOUND_TAP, 0.5f)

        if (!hapticEnabled) return

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            vibrator.vibrate(VibrationEffect.createPredefined(VibrationEffect.EFFECT_CLICK))
        } else {
            @Suppress("DEPRECATION")
            vibrator.vibrate(10)
        }
    }

    /**
     * 햅틱 피드백 - 성공/결과 (수정구슬 공개)
     */
    fun hapticSuccess() {
        playSound(SOUND_REVEAL)

        if (!hapticEnabled) return

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            vibrator.vibrate(VibrationEffect.createPredefined(VibrationEffect.EFFECT_HEAVY_CLICK))
        } else {
            @Suppress("DEPRECATION")
            vibrator.vibrate(50)
        }
    }

    /**
     * 햅틱 피드백 - 주사위 굴림
     */
    fun hapticDiceRoll() {
        playSound(SOUND_DICE_ROLL)

        if (!hapticEnabled) return

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val pattern = longArrayOf(0, 30, 50, 30, 50, 30, 50, 30, 100, 50)
            vibrator.vibrate(VibrationEffect.createWaveform(pattern, -1))
        } else {
            @Suppress("DEPRECATION")
            vibrator.vibrate(longArrayOf(0, 30, 50, 30, 50, 30, 50, 30, 100, 50), -1)
        }
    }

    /**
     * 햅틱 피드백 - 수정구슬 흔들림
     */
    fun hapticShake() {
        playSound(SOUND_MAGIC, 0.3f)

        if (!hapticEnabled) return

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            vibrator.vibrate(VibrationEffect.createPredefined(VibrationEffect.EFFECT_TICK))
        } else {
            @Suppress("DEPRECATION")
            vibrator.vibrate(5)
        }
    }

    /**
     * 햅틱 피드백 - 카드 뒤집기
     */
    fun hapticCardFlip() {
        playSound(SOUND_CARD_FLIP)

        if (!hapticEnabled) return

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            vibrator.vibrate(VibrationEffect.createPredefined(VibrationEffect.EFFECT_DOUBLE_CLICK))
        } else {
            @Suppress("DEPRECATION")
            vibrator.vibrate(longArrayOf(0, 20, 40, 20), -1)
        }
    }

    /**
     * 별 반짝임 효과음
     */
    fun playStar() {
        playSound(SOUND_STAR, 0.6f)
    }

    /**
     * 성공/축하 효과음
     */
    fun playSuccess() {
        playSound(SOUND_SUCCESS)
    }

    /**
     * 사운드 설정 변경
     */
    suspend fun setSoundEnabled(enabled: Boolean) {
        soundEnabled = enabled
        context.notificationDataStore.edit { prefs ->
            prefs[SOUND_ENABLED] = enabled
        }
    }

    /**
     * 햅틱 설정 변경
     */
    suspend fun setHapticEnabled(enabled: Boolean) {
        hapticEnabled = enabled
        context.notificationDataStore.edit { prefs ->
            prefs[HAPTIC_ENABLED] = enabled
        }
    }

    /**
     * 현재 사운드 설정 상태
     */
    fun isSoundEnabled() = soundEnabled

    /**
     * 현재 햅틱 설정 상태
     */
    fun isHapticEnabled() = hapticEnabled

    /**
     * 리소스 해제
     */
    fun release() {
        soundPool?.release()
        soundPool = null
    }
}
