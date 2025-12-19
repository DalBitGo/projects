package com.example.celestialsanctuary.data.repository

import com.example.celestialsanctuary.data.local.UserPreferencesDataStore
import com.example.celestialsanctuary.domain.model.UserProfile
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class UserRepository @Inject constructor(
    private val dataStore: UserPreferencesDataStore
) {
    val isOnboardingCompleted: Flow<Boolean> = dataStore.isOnboardingCompleted

    val userProfile: Flow<UserProfile?> = combine(
        dataStore.userName,
        dataStore.birthDateTime,
        dataStore.birthLocation
    ) { name, birthDateTime, birthLocation ->
        if (birthDateTime != null && birthLocation != null) {
            UserProfile(
                name = name,
                birthDateTime = birthDateTime,
                birthLocation = birthLocation
            )
        } else {
            null
        }
    }

    suspend fun saveUserProfile(profile: UserProfile) {
        dataStore.saveUserProfile(
            name = profile.name,
            birthDateTime = profile.birthDateTime,
            birthLocation = profile.birthLocation
        )
    }

    // 탐험 진행도
    val visitedHouses: Flow<Set<Int>> = dataStore.visitedHouses

    suspend fun markHouseVisited(houseIndex: Int) {
        dataStore.markHouseVisited(houseIndex)
    }

    suspend fun resetExploration() {
        dataStore.resetExploration()
    }
}
