package com.example.celestialsanctuary.domain.usecase

import com.example.celestialsanctuary.data.repository.UserRepository
import com.example.celestialsanctuary.domain.model.Result
import com.example.celestialsanctuary.domain.model.UserProfile
import java.text.SimpleDateFormat
import java.util.Locale
import java.util.TimeZone
import javax.inject.Inject

/**
 * 사용자 프로필을 저장하는 UseCase
 *
 * 책임:
 * - 입력값 유효성 검증
 * - 날짜/시간 파싱
 * - 프로필 저장
 */
class SaveUserProfileUseCase @Inject constructor(
    private val userRepository: UserRepository
) {
    /**
     * 사용자 프로필 저장
     *
     * @param userName 사용자 이름 (선택)
     * @param birthDate 생년월일 (YYYYMMDD)
     * @param birthTime 출생 시간 (HHmm)
     * @param birthLocation 출생 장소
     */
    suspend operator fun invoke(
        userName: String?,
        birthDate: String,
        birthTime: String,
        birthLocation: String
    ): Result<Unit> {
        // 유효성 검증
        val validation = validate(birthDate, birthTime, birthLocation)
        if (validation is Result.Error) {
            return validation
        }

        return try {
            // 날짜/시간 파싱
            val dateTimeString = "$birthDate $birthTime"
            val formatter = SimpleDateFormat("yyyyMMdd HHmm", Locale.getDefault())
            formatter.timeZone = TimeZone.getDefault()
            val timestamp = formatter.parse(dateTimeString)?.time
                ?: return Result.error("날짜 형식이 올바르지 않습니다")

            // 프로필 생성 및 저장
            val profile = UserProfile(
                name = userName?.takeIf { it.isNotBlank() },
                birthDateTime = timestamp,
                birthLocation = birthLocation
            )

            userRepository.saveUserProfile(profile)
            Result.success(Unit)

        } catch (e: Exception) {
            Result.error("프로필 저장 중 오류가 발생했습니다", e)
        }
    }

    /**
     * 입력값 유효성 검증
     */
    private fun validate(
        birthDate: String,
        birthTime: String,
        birthLocation: String
    ): Result<Unit> {
        // 생년월일 검증
        if (birthDate.length != 8) {
            return Result.error("생년월일 8자리를 입력해주세요 (예: 19901215)")
        }

        if (!birthDate.all { it.isDigit() }) {
            return Result.error("생년월일은 숫자만 입력해주세요")
        }

        val year = birthDate.substring(0, 4).toIntOrNull() ?: 0
        val month = birthDate.substring(4, 6).toIntOrNull() ?: 0
        val day = birthDate.substring(6, 8).toIntOrNull() ?: 0

        if (year !in 1900..2100) {
            return Result.error("유효한 연도를 입력해주세요 (1900-2100)")
        }

        if (month !in 1..12) {
            return Result.error("유효한 월을 입력해주세요 (01-12)")
        }

        if (day !in 1..31) {
            return Result.error("유효한 일을 입력해주세요 (01-31)")
        }

        // 출생 시간 검증
        if (birthTime.length != 4) {
            return Result.error("출생 시간 4자리를 입력해주세요 (예: 1430)")
        }

        if (!birthTime.all { it.isDigit() }) {
            return Result.error("출생 시간은 숫자만 입력해주세요")
        }

        val hour = birthTime.substring(0, 2).toIntOrNull() ?: -1
        val minute = birthTime.substring(2, 4).toIntOrNull() ?: -1

        if (hour !in 0..23) {
            return Result.error("유효한 시간을 입력해주세요 (00-23)")
        }

        if (minute !in 0..59) {
            return Result.error("유효한 분을 입력해주세요 (00-59)")
        }

        // 출생 장소 검증
        if (birthLocation.isBlank()) {
            return Result.error("출생 장소를 입력해주세요")
        }

        return Result.success(Unit)
    }
}
