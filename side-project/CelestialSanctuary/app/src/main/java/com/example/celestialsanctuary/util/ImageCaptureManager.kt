package com.example.celestialsanctuary.util

import android.content.ContentValues
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import android.widget.Toast
import androidx.core.content.FileProvider
import java.io.File
import java.io.FileOutputStream
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * 이미지 캡처 및 저장 관리자
 * Compose 화면을 캡처하여 갤러리에 저장하거나 공유
 */
object ImageCaptureManager {

    /**
     * 비트맵을 갤러리에 저장
     * @return 저장된 파일의 URI (성공 시) 또는 null (실패 시)
     */
    fun saveBitmapToGallery(
        context: Context,
        bitmap: Bitmap,
        fileName: String = generateFileName()
    ): Uri? {
        return try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                // Android 10 이상: MediaStore 사용
                saveWithMediaStore(context, bitmap, fileName)
            } else {
                // Android 9 이하: 파일 직접 저장
                saveToExternalStorage(context, bitmap, fileName)
            }
        } catch (e: Exception) {
            e.printStackTrace()
            Toast.makeText(context, "이미지 저장에 실패했습니다", Toast.LENGTH_SHORT).show()
            null
        }
    }

    /**
     * Android 10+ MediaStore API를 사용한 저장
     */
    private fun saveWithMediaStore(
        context: Context,
        bitmap: Bitmap,
        fileName: String
    ): Uri? {
        val contentValues = ContentValues().apply {
            put(MediaStore.Images.Media.DISPLAY_NAME, "$fileName.png")
            put(MediaStore.Images.Media.MIME_TYPE, "image/png")
            put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES + "/CelestialSanctuary")
            put(MediaStore.Images.Media.IS_PENDING, 1)
        }

        val resolver = context.contentResolver
        val uri = resolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, contentValues)

        uri?.let {
            resolver.openOutputStream(it)?.use { outputStream ->
                bitmap.compress(Bitmap.CompressFormat.PNG, 100, outputStream)
            }

            contentValues.clear()
            contentValues.put(MediaStore.Images.Media.IS_PENDING, 0)
            resolver.update(uri, contentValues, null, null)
        }

        if (uri != null) {
            Toast.makeText(context, "이미지가 갤러리에 저장되었습니다", Toast.LENGTH_SHORT).show()
        }

        return uri
    }

    /**
     * Android 9 이하 외부 저장소 직접 저장
     */
    @Suppress("DEPRECATION")
    private fun saveToExternalStorage(
        context: Context,
        bitmap: Bitmap,
        fileName: String
    ): Uri? {
        val picturesDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES)
        val appDir = File(picturesDir, "CelestialSanctuary")
        if (!appDir.exists()) {
            appDir.mkdirs()
        }

        val file = File(appDir, "$fileName.png")
        FileOutputStream(file).use { outputStream ->
            bitmap.compress(Bitmap.CompressFormat.PNG, 100, outputStream)
        }

        // 갤러리에 알림
        context.sendBroadcast(Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE, Uri.fromFile(file)))

        Toast.makeText(context, "이미지가 갤러리에 저장되었습니다", Toast.LENGTH_SHORT).show()
        return Uri.fromFile(file)
    }

    /**
     * 비트맵을 캐시에 저장하고 공유
     */
    fun shareBitmap(
        context: Context,
        bitmap: Bitmap,
        title: String = "운세 결과 공유"
    ) {
        try {
            // 캐시 디렉토리에 임시 저장
            val cachePath = File(context.cacheDir, "shared_images")
            cachePath.mkdirs()
            val file = File(cachePath, "${generateFileName()}.png")

            FileOutputStream(file).use { outputStream ->
                bitmap.compress(Bitmap.CompressFormat.PNG, 100, outputStream)
            }

            // FileProvider URI 생성
            val uri = FileProvider.getUriForFile(
                context,
                "${context.packageName}.fileprovider",
                file
            )

            // 공유 Intent
            val shareIntent = Intent(Intent.ACTION_SEND).apply {
                type = "image/png"
                putExtra(Intent.EXTRA_STREAM, uri)
                putExtra(Intent.EXTRA_TEXT, "✨ Celestial Sanctuary에서 확인한 오늘의 운세 ✨")
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }

            context.startActivity(Intent.createChooser(shareIntent, title))
        } catch (e: Exception) {
            e.printStackTrace()
            Toast.makeText(context, "이미지 공유에 실패했습니다", Toast.LENGTH_SHORT).show()
        }
    }

    /**
     * 파일명 생성
     */
    private fun generateFileName(): String {
        val dateFormat = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault())
        return "fortune_${dateFormat.format(Date())}"
    }
}
