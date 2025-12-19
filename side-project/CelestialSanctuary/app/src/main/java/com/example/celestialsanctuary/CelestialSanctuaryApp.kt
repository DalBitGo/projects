package com.example.celestialsanctuary

import android.app.Application
import com.example.celestialsanctuary.notification.DailyReminderScheduler
import com.example.celestialsanctuary.notification.NotificationHelper
import com.example.celestialsanctuary.notification.NotificationPreferences
import com.example.celestialsanctuary.notification.notificationDataStore
import dagger.hilt.android.HiltAndroidApp
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch

@HiltAndroidApp
class CelestialSanctuaryApp : Application() {

    override fun onCreate() {
        super.onCreate()

        // 알림 채널 생성
        NotificationHelper.createNotificationChannel(this)

        // 알림 스케줄링 (설정이 켜져 있으면)
        CoroutineScope(Dispatchers.IO).launch {
            val isEnabled = notificationDataStore.data.first()[NotificationPreferences.NOTIFICATIONS_ENABLED] ?: true

            if (isEnabled && !DailyReminderScheduler.isReminderScheduled(this@CelestialSanctuaryApp)) {
                val hour = notificationDataStore.data.first()[NotificationPreferences.NOTIFICATION_HOUR] ?: 9
                val minute = notificationDataStore.data.first()[NotificationPreferences.NOTIFICATION_MINUTE] ?: 0
                DailyReminderScheduler.scheduleDailyReminder(this@CelestialSanctuaryApp, hour, minute)
            }
        }
    }
}
