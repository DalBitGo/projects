package com.example.celestialsanctuary.widget

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.content.Intent
import android.widget.RemoteViews
import com.example.celestialsanctuary.MainActivity
import com.example.celestialsanctuary.R
import java.util.Calendar
import kotlin.random.Random

/**
 * 오늘의 운세 앱 위젯
 * 홈 화면에서 간단한 운세 메시지와 행운의 숫자를 표시
 */
class DailyFortuneWidget : AppWidgetProvider() {

    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        for (appWidgetId in appWidgetIds) {
            updateAppWidget(context, appWidgetManager, appWidgetId)
        }
    }

    override fun onEnabled(context: Context) {
        // 첫 번째 위젯이 추가될 때
    }

    override fun onDisabled(context: Context) {
        // 마지막 위젯이 제거될 때
    }

    companion object {
        private val shortMessages = listOf(
            "오늘은 직감을 믿으세요 ✨",
            "좋은 소식이 찾아올 거예요 💫",
            "창의적인 에너지가 넘쳐요 🌟",
            "새로운 만남에 열린 마음을 💕",
            "내면의 평화를 찾아보세요 🌙",
            "별들이 당신 편이에요 ⭐",
            "숨겨진 기회를 발견할 거예요 🔮",
            "자신을 돌보는 시간을 가져요 🌸",
            "도전을 두려워하지 마세요 🚀",
            "작은 변화가 큰 결과를 가져와요 ✨"
        )

        private val luckyColors = listOf(
            "보라색", "금색", "은색", "파란색", "초록색", "분홍색"
        )

        fun updateAppWidget(
            context: Context,
            appWidgetManager: AppWidgetManager,
            appWidgetId: Int
        ) {
            // 날짜 기반 시드로 일관된 결과 생성
            val dailySeed = Calendar.getInstance().run {
                get(Calendar.YEAR) * 10000 + get(Calendar.DAY_OF_YEAR)
            }
            val random = Random(dailySeed)

            // 오늘의 메시지
            val message = shortMessages[random.nextInt(shortMessages.size)]

            // 행운의 숫자 (1-45 중 3개)
            val luckyNumbers = List(3) { random.nextInt(1, 46) }.sorted()

            // 행운의 색상
            val luckyColor = luckyColors[random.nextInt(luckyColors.size)]

            // 날짜 포맷
            val calendar = Calendar.getInstance()
            val month = calendar.get(Calendar.MONTH) + 1
            val day = calendar.get(Calendar.DAY_OF_MONTH)
            val dateText = "${month}월 ${day}일"

            // RemoteViews 생성
            val views = RemoteViews(context.packageName, R.layout.widget_daily_fortune)

            // 데이터 설정
            views.setTextViewText(R.id.widget_date, dateText)
            views.setTextViewText(R.id.widget_message, message)
            views.setTextViewText(R.id.widget_lucky_numbers, "행운 숫자: ${luckyNumbers.joinToString(", ")}")
            views.setTextViewText(R.id.widget_lucky_color, "행운 색상: $luckyColor")

            // 위젯 클릭 시 앱 실행
            val intent = Intent(context, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            }
            val pendingIntent = PendingIntent.getActivity(
                context,
                0,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
            views.setOnClickPendingIntent(R.id.widget_container, pendingIntent)

            // 위젯 업데이트
            appWidgetManager.updateAppWidget(appWidgetId, views)
        }
    }
}
