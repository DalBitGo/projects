package com.example.celestialsanctuary.domain.model

import androidx.compose.ui.graphics.Color

enum class Planet(
    val displayName: String,
    val symbol: String,
    val color: Color
) {
    SUN("Sun", "☉", Color(0xFFFFD700)),
    MOON("Moon", "☽", Color(0xFFC0C0C0)),
    MERCURY("Mercury", "☿", Color(0xFF87CEEB)),
    VENUS("Venus", "♀", Color(0xFFFFB6C1)),
    MARS("Mars", "♂", Color(0xFFFF4500)),
    JUPITER("Jupiter", "♃", Color(0xFF4169E1)),
    SATURN("Saturn", "♄", Color(0xFF8B4513)),
    URANUS("Uranus", "♅", Color(0xFF00CED1)),
    NEPTUNE("Neptune", "♆", Color(0xFF9370DB)),
    PLUTO("Pluto", "♇", Color(0xFF2F4F4F))
}
