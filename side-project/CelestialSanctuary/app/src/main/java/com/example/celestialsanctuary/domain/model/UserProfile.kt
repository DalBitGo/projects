package com.example.celestialsanctuary.domain.model

data class UserProfile(
    val name: String? = null,
    val birthDateTime: Long,    // Unix timestamp
    val birthLocation: String
)
