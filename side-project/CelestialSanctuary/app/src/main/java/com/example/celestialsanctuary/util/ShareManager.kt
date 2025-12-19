package com.example.celestialsanctuary.util

import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.Canvas
import android.net.Uri
import android.view.View
import androidx.core.content.FileProvider
import java.io.File
import java.io.FileOutputStream
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * 결과 공유 관리자
 * 텍스트 및 이미지 공유 기능 제공
 */
object ShareManager {

    /**
     * 텍스트 공유
     */
    fun shareText(context: Context, text: String, title: String = "운세 공유") {
        val intent = Intent(Intent.ACTION_SEND).apply {
            type = "text/plain"
            putExtra(Intent.EXTRA_SUBJECT, title)
            putExtra(Intent.EXTRA_TEXT, text)
        }
        context.startActivity(Intent.createChooser(intent, "공유하기"))
    }

    /**
     * 수정구슬 결과 공유 텍스트 생성
     */
    fun createCrystalBallShareText(
        message: String,
        luckyNumbers: List<Int>,
        luckyColor: String,
        luckyDirection: String
    ): String {
        val dateFormat = SimpleDateFormat("yyyy년 M월 d일", Locale.KOREAN)
        val today = dateFormat.format(Date())

        return buildString {
            appendLine("🔮 오늘의 수정구슬 운세 🔮")
            appendLine("📅 $today")
            appendLine()
            appendLine("✨ 메시지:")
            appendLine("\"$message\"")
            appendLine()
            appendLine("🔢 행운 숫자: ${luckyNumbers.joinToString(", ")}")
            appendLine("🎨 행운 색상: $luckyColor")
            appendLine("🧭 행운 방향: $luckyDirection")
            appendLine()
            appendLine("━━━━━━━━━━━")
            appendLine("📲 Celestial Sanctuary")
            appendLine("#수정구슬운세 #오늘의운세")
        }
    }

    /**
     * 타로카드 결과 공유 텍스트 생성
     */
    fun createTarotShareText(
        cardName: String,
        cardSymbol: String,
        meaning: String
    ): String {
        val dateFormat = SimpleDateFormat("yyyy년 M월 d일", Locale.KOREAN)
        val today = dateFormat.format(Date())

        return buildString {
            appendLine("🃏 오늘의 타로카드 🃏")
            appendLine("📅 $today")
            appendLine()
            appendLine("$cardSymbol $cardName")
            appendLine()
            appendLine("✨ 의미:")
            appendLine("\"$meaning\"")
            appendLine()
            appendLine("━━━━━━━━━━━")
            appendLine("📲 Celestial Sanctuary")
            appendLine("#타로카드 #오늘의운세")
        }
    }

    /**
     * 주사위 결과 공유 텍스트 생성
     */
    fun createDiceShareText(
        numbers: List<Int>,
        interpretation: String,
        luckyLevel: Int
    ): String {
        val dateFormat = SimpleDateFormat("yyyy년 M월 d일", Locale.KOREAN)
        val today = dateFormat.format(Date())
        val stars = "⭐".repeat(luckyLevel) + "☆".repeat(5 - luckyLevel)

        return buildString {
            appendLine("🎲 오늘의 행운 주사위 🎲")
            appendLine("📅 $today")
            appendLine()
            appendLine("🎯 숫자: ${numbers.joinToString(" - ")}")
            appendLine("📊 행운 레벨: $stars")
            appendLine()
            appendLine("✨ 해석:")
            appendLine("\"$interpretation\"")
            appendLine()
            appendLine("━━━━━━━━━━━")
            appendLine("📲 Celestial Sanctuary")
            appendLine("#주사위운세 #오늘의운세")
        }
    }

    /**
     * 주간 운세 공유 텍스트 생성
     */
    fun createWeeklyFortuneShareText(
        date: String,
        fortuneLevel: Int,
        generalFortune: String,
        luckyColor: String,
        luckyNumber: Int,
        luckyDirection: String
    ): String {
        val stars = "⭐".repeat(fortuneLevel) + "☆".repeat(5 - fortuneLevel)

        return buildString {
            appendLine("📅 주간 운세 - $date")
            appendLine()
            appendLine("📊 운세 지수: $stars")
            appendLine()
            appendLine("🌟 종합 운세:")
            appendLine("\"$generalFortune\"")
            appendLine()
            appendLine("🎨 행운 색상: $luckyColor")
            appendLine("🔢 행운 숫자: $luckyNumber")
            appendLine("🧭 행운 방향: $luckyDirection")
            appendLine()
            appendLine("━━━━━━━━━━━")
            appendLine("📲 Celestial Sanctuary")
            appendLine("#주간운세 #별자리운세")
        }
    }

    /**
     * 이미지로 캡처하여 공유 (View 기반)
     * Compose에서는 별도의 방법 필요
     */
    fun shareViewAsImage(context: Context, view: View, fileName: String = "fortune_result") {
        try {
            // View를 Bitmap으로 변환
            val bitmap = Bitmap.createBitmap(view.width, view.height, Bitmap.Config.ARGB_8888)
            val canvas = Canvas(bitmap)
            view.draw(canvas)

            // 파일로 저장
            val cachePath = File(context.cacheDir, "shared_images")
            cachePath.mkdirs()
            val file = File(cachePath, "$fileName.png")
            FileOutputStream(file).use { stream ->
                bitmap.compress(Bitmap.CompressFormat.PNG, 100, stream)
            }

            // URI 생성
            val uri = FileProvider.getUriForFile(
                context,
                "${context.packageName}.fileprovider",
                file
            )

            // 공유 Intent
            val intent = Intent(Intent.ACTION_SEND).apply {
                type = "image/png"
                putExtra(Intent.EXTRA_STREAM, uri)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            context.startActivity(Intent.createChooser(intent, "이미지 공유"))
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}
