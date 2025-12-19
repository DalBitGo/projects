package com.example.celestialsanctuary.notification

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent

/**
 * 일일 알림을 수신하는 BroadcastReceiver
 * AlarmManager에서 예약된 시간에 호출됨
 */
class DailyReminderReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        // 알림 표시
        NotificationHelper.showDailyFortuneNotification(context)

        // 다음 날 알림 재예약
        DailyReminderScheduler.scheduleDailyReminder(context)
    }
}
