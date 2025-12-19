package com.example.celestialsanctuary.data.local

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.longPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.core.stringSetPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "user_preferences")

class UserPreferencesDataStore(private val context: Context) {

    private object PreferencesKeys {
        val IS_ONBOARDING_COMPLETED = booleanPreferencesKey("is_onboarding_completed")
        val USER_NAME = stringPreferencesKey("user_name")
        val BIRTH_DATE_TIME = longPreferencesKey("birth_date_time")
        val BIRTH_LOCATION = stringPreferencesKey("birth_location")
        val VISITED_HOUSES = stringSetPreferencesKey("visited_houses")
    }

    val isOnboardingCompleted: Flow<Boolean> = context.dataStore.data
        .map { preferences ->
            preferences[PreferencesKeys.IS_ONBOARDING_COMPLETED] ?: false
        }

    val userName: Flow<String?> = context.dataStore.data
        .map { preferences ->
            preferences[PreferencesKeys.USER_NAME]
        }

    val birthDateTime: Flow<Long?> = context.dataStore.data
        .map { preferences ->
            preferences[PreferencesKeys.BIRTH_DATE_TIME]
        }

    val birthLocation: Flow<String?> = context.dataStore.data
        .map { preferences ->
            preferences[PreferencesKeys.BIRTH_LOCATION]
        }

    suspend fun saveUserProfile(
        name: String?,
        birthDateTime: Long,
        birthLocation: String
    ) {
        context.dataStore.edit { preferences ->
            name?.let { preferences[PreferencesKeys.USER_NAME] = it }
            preferences[PreferencesKeys.BIRTH_DATE_TIME] = birthDateTime
            preferences[PreferencesKeys.BIRTH_LOCATION] = birthLocation
            preferences[PreferencesKeys.IS_ONBOARDING_COMPLETED] = true
        }
    }

    suspend fun setOnboardingCompleted(completed: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[PreferencesKeys.IS_ONBOARDING_COMPLETED] = completed
        }
    }

    // 탐험 진행도 관련
    val visitedHouses: Flow<Set<Int>> = context.dataStore.data
        .map { preferences ->
            preferences[PreferencesKeys.VISITED_HOUSES]
                ?.mapNotNull { it.toIntOrNull() }
                ?.toSet()
                ?: emptySet()
        }

    suspend fun markHouseVisited(houseIndex: Int) {
        context.dataStore.edit { preferences ->
            val current = preferences[PreferencesKeys.VISITED_HOUSES] ?: emptySet()
            preferences[PreferencesKeys.VISITED_HOUSES] = current + houseIndex.toString()
        }
    }

    suspend fun resetExploration() {
        context.dataStore.edit { preferences ->
            preferences[PreferencesKeys.VISITED_HOUSES] = emptySet()
        }
    }
}
