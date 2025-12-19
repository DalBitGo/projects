package com.example.celestialsanctuary.notification

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.intPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

/**
 * 알림 설정을 위한 DataStore 확장
 */
val Context.notificationDataStore: DataStore<Preferences> by preferencesDataStore(
    name = "notification_preferences"
)

/**
 * 알림 설정 키 정의
 */
object NotificationPreferences {
    val NOTIFICATIONS_ENABLED = booleanPreferencesKey("notifications_enabled")
    val NOTIFICATION_HOUR = intPreferencesKey("notification_hour")
    val NOTIFICATION_MINUTE = intPreferencesKey("notification_minute")
}

/**
 * 알림 설정 저장소
 */
class NotificationSettingsRepository(private val context: Context) {

    val isNotificationsEnabled: Flow<Boolean> = context.notificationDataStore.data
        .map { preferences ->
            preferences[NotificationPreferences.NOTIFICATIONS_ENABLED] ?: true
        }

    val notificationHour: Flow<Int> = context.notificationDataStore.data
        .map { preferences ->
            preferences[NotificationPreferences.NOTIFICATION_HOUR] ?: 9
        }

    val notificationMinute: Flow<Int> = context.notificationDataStore.data
        .map { preferences ->
            preferences[NotificationPreferences.NOTIFICATION_MINUTE] ?: 0
        }

    suspend fun setNotificationsEnabled(enabled: Boolean) {
        context.notificationDataStore.edit { preferences ->
            preferences[NotificationPreferences.NOTIFICATIONS_ENABLED] = enabled
        }

        if (enabled) {
            DailyReminderScheduler.scheduleDailyReminder(context)
        } else {
            DailyReminderScheduler.cancelDailyReminder(context)
        }
    }

    suspend fun setNotificationTime(hour: Int, minute: Int) {
        context.notificationDataStore.edit { preferences ->
            preferences[NotificationPreferences.NOTIFICATION_HOUR] = hour
            preferences[NotificationPreferences.NOTIFICATION_MINUTE] = minute
        }

        // 새 시간으로 재예약
        DailyReminderScheduler.cancelDailyReminder(context)
        DailyReminderScheduler.scheduleDailyReminder(context, hour, minute)
    }
}
