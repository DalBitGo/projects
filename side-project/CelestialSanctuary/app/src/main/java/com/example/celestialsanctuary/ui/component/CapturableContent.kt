package com.example.celestialsanctuary.ui.component

import android.graphics.Bitmap
import android.view.View
import androidx.compose.foundation.layout.Box
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.ComposeView
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.view.drawToBitmap

/**
 * 캡처 가능한 컨텐츠 상태
 */
class CaptureController {
    internal var captureCallback: (() -> Bitmap?)? = null

    /**
     * 현재 컨텐츠를 비트맵으로 캡처
     * @return 캡처된 비트맵 또는 null
     */
    fun capture(): Bitmap? {
        return captureCallback?.invoke()
    }
}

/**
 * CaptureController를 기억하는 Composable
 */
@Composable
fun rememberCaptureController(): CaptureController {
    return remember { CaptureController() }
}

/**
 * 캡처 가능한 컨텐츠 래퍼
 *
 * 사용 예시:
 * ```
 * val captureController = rememberCaptureController()
 *
 * CapturableContent(
 *     controller = captureController,
 *     modifier = Modifier.fillMaxWidth()
 * ) {
 *     // 캡처할 컨텐츠
 *     ResultCard(...)
 * }
 *
 * Button(onClick = {
 *     val bitmap = captureController.capture()
 *     bitmap?.let { ImageCaptureManager.saveBitmapToGallery(context, it) }
 * }) {
 *     Text("저장")
 * }
 * ```
 */
@Composable
fun CapturableContent(
    controller: CaptureController,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    var viewRef by remember { mutableStateOf<View?>(null) }

    controller.captureCallback = {
        viewRef?.let { view ->
            try {
                view.drawToBitmap()
            } catch (e: Exception) {
                e.printStackTrace()
                null
            }
        }
    }

    AndroidView(
        factory = { context ->
            ComposeView(context).apply {
                setContent {
                    Box {
                        content()
                    }
                }
            }
        },
        modifier = modifier,
        update = { view ->
            viewRef = view
        }
    )
}
