package com.example.celestialsanctuary.domain.model

data class PlanetPlacement(
    val planet: Planet,
    val sign: ZodiacSign,
    val houseIndex: Int
)
