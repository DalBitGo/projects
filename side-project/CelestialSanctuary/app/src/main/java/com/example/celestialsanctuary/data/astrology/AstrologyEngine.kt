package com.example.celestialsanctuary.data.astrology

import com.example.celestialsanctuary.domain.model.House
import com.example.celestialsanctuary.domain.model.HouseState
import com.example.celestialsanctuary.domain.model.Planet
import com.example.celestialsanctuary.domain.model.PlanetPlacement
import com.example.celestialsanctuary.domain.model.ZodiacSign
import java.util.Calendar
import javax.inject.Inject
import javax.inject.Singleton

/**
 * 점성술 계산 엔진
 *
 * Phase 1: Whole Sign House 시스템 + 간단한 행성 위치 계산
 * Phase 2 (추후): Swiss Ephemeris 통합 또는 외부 API
 */
@Singleton
class AstrologyEngine @Inject constructor() {

    /**
     * 출생 날짜로 태양 별자리 계산
     */
    fun getSunSign(birthDateTime: Long): ZodiacSign {
        val calendar = Calendar.getInstance().apply { timeInMillis = birthDateTime }
        val month = calendar.get(Calendar.MONTH) + 1 // 0-based → 1-based
        val day = calendar.get(Calendar.DAY_OF_MONTH)

        return when {
            (month == 3 && day >= 21) || (month == 4 && day <= 19) -> ZodiacSign.ARIES
            (month == 4 && day >= 20) || (month == 5 && day <= 20) -> ZodiacSign.TAURUS
            (month == 5 && day >= 21) || (month == 6 && day <= 20) -> ZodiacSign.GEMINI
            (month == 6 && day >= 21) || (month == 7 && day <= 22) -> ZodiacSign.CANCER
            (month == 7 && day >= 23) || (month == 8 && day <= 22) -> ZodiacSign.LEO
            (month == 8 && day >= 23) || (month == 9 && day <= 22) -> ZodiacSign.VIRGO
            (month == 9 && day >= 23) || (month == 10 && day <= 22) -> ZodiacSign.LIBRA
            (month == 10 && day >= 23) || (month == 11 && day <= 21) -> ZodiacSign.SCORPIO
            (month == 11 && day >= 22) || (month == 12 && day <= 21) -> ZodiacSign.SAGITTARIUS
            (month == 12 && day >= 22) || (month == 1 && day <= 19) -> ZodiacSign.CAPRICORN
            (month == 1 && day >= 20) || (month == 2 && day <= 18) -> ZodiacSign.AQUARIUS
            else -> ZodiacSign.PISCES
        }
    }

    /**
     * 출생 시간으로 Ascendant(상승궁) 추정
     *
     * 간단한 추정: 일출 시간에 태양 별자리가 상승, 2시간마다 다음 별자리
     * (실제로는 위도/경도에 따라 다름 - Phase 2에서 개선)
     */
    fun getAscendant(birthDateTime: Long): ZodiacSign {
        val calendar = Calendar.getInstance().apply { timeInMillis = birthDateTime }
        val hour = calendar.get(Calendar.HOUR_OF_DAY)
        val sunSign = getSunSign(birthDateTime)

        // 일출 시간을 6시로 가정 (간단한 추정)
        // 일출 시 태양 별자리가 Ascendant
        // 2시간마다 다음 별자리로 이동
        val hoursFromSunrise = if (hour >= 6) hour - 6 else hour + 18
        val signOffset = hoursFromSunrise / 2

        val signs = ZodiacSign.entries
        val sunSignIndex = signs.indexOf(sunSign)
        val ascendantIndex = (sunSignIndex + signOffset) % 12

        return signs[ascendantIndex]
    }

    /**
     * Whole Sign House 시스템으로 하우스별 별자리 매핑
     * Ascendant 별자리 = 1st House
     */
    fun getHouseSigns(ascendant: ZodiacSign): Map<Int, ZodiacSign> {
        val signs = ZodiacSign.entries
        val startIndex = signs.indexOf(ascendant)

        return (1..12).associateWith { houseIndex ->
            signs[(startIndex + houseIndex - 1) % 12]
        }
    }

    /**
     * 간단한 행성 위치 계산
     *
     * Phase 1: 출생 날짜 기반 추정 (정확하지 않음)
     * - 태양: 태양 별자리
     * - 달: 태양 별자리에서 약간 오프셋 (출생일 기반)
     * - 수성/금성: 태양 근처 (±1 별자리)
     * - 화성~명왕성: 연도 기반 추정
     */
    fun getPlanetPlacements(birthDateTime: Long, houseSigns: Map<Int, ZodiacSign>): List<PlanetPlacement> {
        val calendar = Calendar.getInstance().apply { timeInMillis = birthDateTime }
        val year = calendar.get(Calendar.YEAR)
        val month = calendar.get(Calendar.MONTH)
        val day = calendar.get(Calendar.DAY_OF_MONTH)

        val sunSign = getSunSign(birthDateTime)
        val signs = ZodiacSign.entries
        val sunIndex = signs.indexOf(sunSign)

        // 간단한 행성 위치 추정
        val placements = mutableListOf<PlanetPlacement>()

        // Sun - 태양 별자리에 위치
        placements.add(createPlacement(Planet.SUN, sunSign, houseSigns))

        // Moon - 출생일에 따라 다른 별자리 (대략 2.5일마다 별자리 이동)
        val moonOffset = (day / 3) % 12
        placements.add(createPlacement(Planet.MOON, signs[(sunIndex + moonOffset) % 12], houseSigns))

        // Mercury - 태양 근처 (±1 별자리)
        val mercuryOffset = ((month + day) % 3) - 1
        placements.add(createPlacement(Planet.MERCURY, signs[(sunIndex + mercuryOffset + 12) % 12], houseSigns))

        // Venus - 태양 근처 (±2 별자리)
        val venusOffset = ((year + month) % 5) - 2
        placements.add(createPlacement(Planet.VENUS, signs[(sunIndex + venusOffset + 12) % 12], houseSigns))

        // Mars - 약 2년 주기
        val marsOffset = (year / 2 + month) % 12
        placements.add(createPlacement(Planet.MARS, signs[marsOffset], houseSigns))

        // Jupiter - 약 12년 주기 (1별자리당 1년)
        val jupiterOffset = year % 12
        placements.add(createPlacement(Planet.JUPITER, signs[jupiterOffset], houseSigns))

        // Saturn - 약 29년 주기 (1별자리당 2.5년)
        val saturnOffset = (year / 2) % 12
        placements.add(createPlacement(Planet.SATURN, signs[saturnOffset], houseSigns))

        // Uranus - 약 84년 주기 (1별자리당 7년)
        val uranusOffset = (year / 7) % 12
        placements.add(createPlacement(Planet.URANUS, signs[uranusOffset], houseSigns))

        // Neptune - 약 165년 주기 (1별자리당 14년)
        val neptuneOffset = (year / 14) % 12
        placements.add(createPlacement(Planet.NEPTUNE, signs[neptuneOffset], houseSigns))

        // Pluto - 약 248년 주기 (불규칙)
        val plutoOffset = (year / 20) % 12
        placements.add(createPlacement(Planet.PLUTO, signs[plutoOffset], houseSigns))

        return placements
    }

    private fun createPlacement(
        planet: Planet,
        sign: ZodiacSign,
        houseSigns: Map<Int, ZodiacSign>
    ): PlanetPlacement {
        // 해당 별자리가 몇 번째 하우스인지 찾기
        val houseIndex = houseSigns.entries.find { it.value == sign }?.key ?: 1
        return PlanetPlacement(planet, sign, houseIndex)
    }

    /**
     * 하우스 상태 결정
     */
    fun getHouseState(house: House, planetsInHouse: List<Planet>): HouseState {
        if (planetsInHouse.isEmpty()) {
            return HouseState.EMPTY
        }

        // 주인 행성이 자기 집에 있는지 확인
        return if (planetsInHouse.contains(house.ownerPlanet)) {
            HouseState.OWNER_HOME
        } else {
            HouseState.TENANT
        }
    }

    /**
     * 전체 차트 생성
     */
    fun generateChart(birthDateTime: Long): BirthChart {
        val sunSign = getSunSign(birthDateTime)
        val ascendant = getAscendant(birthDateTime)
        val houseSigns = getHouseSigns(ascendant)
        val planetPlacements = getPlanetPlacements(birthDateTime, houseSigns)

        return BirthChart(
            sunSign = sunSign,
            ascendant = ascendant,
            houseSigns = houseSigns,
            planetPlacements = planetPlacements
        )
    }
}

/**
 * 출생 차트 데이터
 */
data class BirthChart(
    val sunSign: ZodiacSign,
    val ascendant: ZodiacSign,
    val houseSigns: Map<Int, ZodiacSign>,
    val planetPlacements: List<PlanetPlacement>
) {
    /**
     * 특정 하우스에 있는 행성들 반환
     */
    fun getPlanetsInHouse(houseIndex: Int): List<Planet> {
        return planetPlacements
            .filter { it.houseIndex == houseIndex }
            .map { it.planet }
    }
}
