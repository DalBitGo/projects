package com.example.celestialsanctuary.domain.model

data class HouseDetail(
    val house: House,
    val state: HouseState,
    val tenantPlanet: Planet?,       // TENANT 또는 OWNER_HOME일 때
    val interpretation: String       // 해석 텍스트
)
