package com.example.celestialsanctuary.data.repository

import com.example.celestialsanctuary.data.astrology.AstrologyEngine
import com.example.celestialsanctuary.data.astrology.BirthChart
import com.example.celestialsanctuary.domain.model.House
import com.example.celestialsanctuary.domain.model.HouseDetail
import com.example.celestialsanctuary.domain.model.HouseState
import com.example.celestialsanctuary.domain.model.Planet
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ChartRepository @Inject constructor(
    private val userRepository: UserRepository,
    private val astrologyEngine: AstrologyEngine
) {
    /**
     * 사용자 출생정보 기반 차트 생성
     */
    suspend fun getUserChart(): BirthChart? {
        val profile = userRepository.userProfile.first()
        return profile?.let {
            astrologyEngine.generateChart(it.birthDateTime)
        }
    }

    /**
     * 모든 하우스와 상태 반환
     */
    fun getAllHousesWithState(): Flow<List<HouseWithPlanetState>> = flow {
        val chart = getUserChart()

        val result = House.ALL_HOUSES.map { house ->
            val planetsInHouse = chart?.getPlanetsInHouse(house.index) ?: emptyList()
            val state = astrologyEngine.getHouseState(house, planetsInHouse)
            val primaryPlanet = planetsInHouse.firstOrNull()

            HouseWithPlanetState(
                house = house,
                state = state,
                planets = planetsInHouse,
                primaryPlanet = primaryPlanet
            )
        }

        emit(result)
    }

    /**
     * 특정 하우스 상세 정보
     */
    suspend fun getHouseDetail(houseIndex: Int): HouseDetail {
        val house = House.ALL_HOUSES.getOrNull(houseIndex - 1) ?: House.ALL_HOUSES.first()
        val chart = getUserChart()
        val planetsInHouse = chart?.getPlanetsInHouse(houseIndex) ?: emptyList()
        val state = astrologyEngine.getHouseState(house, planetsInHouse)
        val primaryPlanet = planetsInHouse.firstOrNull()

        val interpretation = generateInterpretation(house, state, primaryPlanet, planetsInHouse)

        return HouseDetail(
            house = house,
            state = state,
            tenantPlanet = primaryPlanet,
            interpretation = interpretation
        )
    }

    private fun generateInterpretation(
        house: House,
        state: HouseState,
        primaryPlanet: Planet?,
        allPlanets: List<Planet>
    ): String {
        val baseText = getBaseInterpretation(house.index)

        val stateText = when (state) {
            HouseState.EMPTY -> "\n\n현재 이 하우스에는 행성이 머물지 않습니다. " +
                    "이 영역은 다른 하우스의 영향이나 트랜짓에 의해 활성화됩니다. " +
                    "주인 행성인 ${house.ownerPlanet.displayName}의 위치를 확인해보세요."

            HouseState.TENANT -> {
                val planetNames = allPlanets.joinToString(", ") { it.displayName }
                "\n\n$planetNames 이(가) 이 하우스에 손님으로 머물고 있습니다. " +
                        "${primaryPlanet?.displayName ?: "이 행성"}의 에너지가 ${house.nameKo}의 영역에 " +
                        "특별한 영향을 미치고 있습니다."
            }

            HouseState.OWNER_HOME -> "\n\n🌟 ${house.ownerPlanet.displayName}이(가) 자신의 집에 있습니다! " +
                    "이는 매우 강력한 배치로, ${house.nameKo}의 영역에서 " +
                    "탁월한 능력과 자연스러운 재능을 발휘할 수 있습니다. " +
                    "이 영역에서 당신은 본능적으로 무엇을 해야 하는지 알고 있습니다."
        }

        return baseText + stateText
    }

    private fun getBaseInterpretation(index: Int): String {
        return when (index) {
            1 -> "제1하우스는 자아와 정체성을 나타냅니다. 당신이 세상에 보여주는 첫인상과 외모, 그리고 삶을 대하는 기본적인 태도를 상징합니다. 이 하우스는 당신의 개성과 자기표현의 방식을 결정합니다."
            2 -> "제2하우스는 물질적 소유와 가치관을 나타냅니다. 돈을 버는 방식, 재정 관리 능력, 그리고 자존감과 깊이 연결되어 있습니다. 당신이 무엇을 가치 있게 여기는지 보여줍니다."
            3 -> "제3하우스는 소통과 학습을 나타냅니다. 일상적인 대화, 형제자매 관계, 단기 여행, 그리고 초기 교육을 상징합니다. 당신의 생각을 표현하는 방식과 정보를 처리하는 스타일을 나타냅니다."
            4 -> "제4하우스는 가정과 뿌리를 나타냅니다. 가족, 조상, 감정적 기반, 그리고 삶의 끝에서 찾게 되는 안식처를 상징합니다. 당신의 내면 깊은 곳에 있는 감정적 안정감의 원천입니다."
            5 -> "제5하우스는 창조성과 즐거움을 나타냅니다. 연애, 자녀, 취미, 도박, 그리고 자기표현의 모든 형태를 상징합니다. 당신이 인생에서 기쁨을 찾는 방식을 보여줍니다."
            6 -> "제6하우스는 건강과 일상을 나타냅니다. 직장에서의 봉사, 건강 관리 습관, 그리고 일상적인 루틴을 상징합니다. 당신이 매일의 삶을 어떻게 구조화하는지 나타냅니다."
            7 -> "제7하우스는 파트너십을 나타냅니다. 결혼, 사업 파트너, 그리고 당신이 타인과 맺는 중요한 일대일 관계를 상징합니다. 당신이 관계에서 찾는 것과 끌리는 유형을 보여줍니다."
            8 -> "제8하우스는 변화와 재생을 나타냅니다. 죽음과 부활, 공유 자원, 친밀감, 그리고 심오한 심리적 변화를 상징합니다. 삶의 깊은 미스터리와 변형의 과정을 다룹니다."
            9 -> "제9하우스는 철학과 확장을 나타냅니다. 고등 교육, 해외 여행, 종교, 법률, 그리고 삶의 의미 탐구를 상징합니다. 당신의 세계관과 믿음 체계를 형성합니다."
            10 -> "제10하우스는 커리어와 명성을 나타냅니다. 사회적 지위, 직업적 성취, 권위, 그리고 대중에게 인식되는 이미지를 상징합니다. 당신의 인생 목표와 공적 역할을 나타냅니다."
            11 -> "제11하우스는 커뮤니티와 희망을 나타냅니다. 친구, 그룹 활동, 사회적 이상, 그리고 미래를 향한 꿈을 상징합니다. 당신이 속한 집단과 인류에 대한 비전을 보여줍니다."
            12 -> "제12하우스는 무의식과 영성을 나타냅니다. 숨겨진 적, 자기 파괴적 패턴, 영적 성장, 그리고 카르마를 상징합니다. 눈에 보이지 않는 영역과 내면의 성소를 다룹니다."
            else -> "해석 정보를 불러올 수 없습니다."
        }
    }
}

data class HouseWithPlanetState(
    val house: House,
    val state: HouseState,
    val planets: List<Planet>,
    val primaryPlanet: Planet?
)
