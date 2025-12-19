package com.example.celestialsanctuary.domain.model

data class House(
    val index: Int,           // 1-12
    val nameEn: String,       // "The Self"
    val nameKo: String,       // "자아"
    val ownerPlanet: Planet   // 전통적인 주인 행성
) {
    companion object {
        val ALL_HOUSES = listOf(
            House(1, "The Self", "자아", Planet.MARS),
            House(2, "Possessions", "소유", Planet.VENUS),
            House(3, "Communication", "소통", Planet.MERCURY),
            House(4, "Home", "가정", Planet.MOON),
            House(5, "Pleasure", "즐거움", Planet.SUN),
            House(6, "Health", "건강", Planet.MERCURY),
            House(7, "Partnership", "관계", Planet.VENUS),
            House(8, "Transformation", "변화", Planet.PLUTO),
            House(9, "Philosophy", "철학", Planet.JUPITER),
            House(10, "Career", "직업", Planet.SATURN),
            House(11, "Community", "커뮤니티", Planet.URANUS),
            House(12, "Subconscious", "무의식", Planet.NEPTUNE)
        )
    }
}
