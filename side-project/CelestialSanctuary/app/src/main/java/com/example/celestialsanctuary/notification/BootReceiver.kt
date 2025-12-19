package com.example.celestialsanctuary.notification

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch

/**
 * 기기 재부팅 후 알림을 다시 예약하는 BroadcastReceiver
 */
class BootReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            // 알림 채널 생성
            NotificationHelper.createNotificationChannel(context)

            // 알림 설정이 켜져 있으면 재예약
            CoroutineScope(Dispatchers.IO).launch {
                val dataStore = context.notificationDataStore
                val isEnabled = dataStore.data.first()[NotificationPreferences.NOTIFICATIONS_ENABLED] ?: true

                if (isEnabled) {
                    val hour = dataStore.data.first()[NotificationPreferences.NOTIFICATION_HOUR] ?: 9
                    val minute = dataStore.data.first()[NotificationPreferences.NOTIFICATION_MINUTE] ?: 0

                    DailyReminderScheduler.scheduleDailyReminder(context, hour, minute)
                }
            }
        }
    }
}
