package com.example.celestialsanctuary.notification

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import com.example.celestialsanctuary.MainActivity
import com.example.celestialsanctuary.R
import kotlin.random.Random

/**
 * 알림 생성 및 표시를 담당하는 헬퍼 클래스
 */
object NotificationHelper {

    private const val CHANNEL_ID = "daily_fortune_channel"
    private const val CHANNEL_NAME = "일일 운세 알림"
    private const val NOTIFICATION_ID = 1001

    /**
     * 알림 채널 생성 (Android 8.0+)
     */
    fun createNotificationChannel(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                CHANNEL_NAME,
                NotificationManager.IMPORTANCE_DEFAULT
            ).apply {
                description = "매일 오늘의 운세를 알려드립니다"
                enableLights(true)
                enableVibration(true)
            }

            val notificationManager = context.getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }
    }

    /**
     * 일일 운세 알림 표시
     */
    fun showDailyFortuneNotification(context: Context) {
        // 앱 실행 인텐트
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }

        val pendingIntent = PendingIntent.getActivity(
            context,
            0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        // 랜덤 메시지 선택
        val (title, message) = getRandomNotificationContent()

        val notification = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_launcher_foreground) // 앱 아이콘
            .setContentTitle(title)
            .setContentText(message)
            .setStyle(NotificationCompat.BigTextStyle().bigText(message))
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .build()

        val notificationManager = context.getSystemService(NotificationManager::class.java)
        notificationManager.notify(NOTIFICATION_ID, notification)
    }

    /**
     * 랜덤 알림 메시지 선택
     */
    private fun getRandomNotificationContent(): Pair<String, String> {
        val contents = listOf(
            "✨ 오늘의 운세가 도착했어요" to "별들이 당신에게 전하는 메시지를 확인하세요!",
            "🔮 수정구슬이 빛나고 있어요" to "오늘의 운명을 확인할 시간입니다.",
            "🃏 타로 카드가 기다리고 있어요" to "운명의 카드가 당신을 부르고 있습니다.",
            "🎲 행운의 주사위를 굴려보세요" to "오늘 당신의 행운 지수는?",
            "⭐ 별자리 운세 업데이트" to "12하우스가 전하는 오늘의 메시지를 확인하세요.",
            "🌙 달이 당신에게 속삭입니다" to "내면의 직감을 믿어보세요.",
            "☀️ 태양이 새로운 하루를 비춥니다" to "오늘의 에너지를 확인해보세요!",
            "🌟 천궁의 성소에서 알림" to "당신만을 위한 운세가 준비되었습니다."
        )

        return contents[Random.nextInt(contents.size)]
    }
}
