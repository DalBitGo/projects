package com.example.celestialsanctuary.ui.component

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import com.example.celestialsanctuary.ui.theme.DeepNavy
import com.example.celestialsanctuary.ui.theme.Gold
import com.example.celestialsanctuary.ui.theme.RoyalPurple
import kotlin.random.Random

/**
 * 별 데이터 클래스
 */
data class Star(
    val x: Float,           // 0f ~ 1f (화면 비율)
    val y: Float,           // 0f ~ 1f (화면 비율)
    val size: Float,        // 별 크기 (dp 기준)
    val baseAlpha: Float,   // 기본 알파값 (0.3f ~ 1f)
    val blinkSpeed: Int,    // 깜빡임 속도 (ms)
    val blinkPhase: Float   // 깜빡임 위상 차이 (0f ~ 1f)
)

/**
 * 별들을 랜덤하게 생성
 */
private fun generateStars(count: Int, seed: Long = 42L): List<Star> {
    val random = Random(seed)
    return List(count) {
        Star(
            x = random.nextFloat(),
            y = random.nextFloat(),
            size = random.nextFloat() * 2f + 1f,  // 1dp ~ 3dp
            baseAlpha = random.nextFloat() * 0.5f + 0.3f,  // 0.3 ~ 0.8
            blinkSpeed = (random.nextFloat() * 3000 + 2000).toInt(),  // 2000ms ~ 5000ms
            blinkPhase = random.nextFloat()
        )
    }
}

/**
 * 신비로운 별이 반짝이는 배경
 *
 * @param modifier Modifier
 * @param starCount 별 개수 (기본 80개)
 * @param showNebula 성운 효과 표시 여부
 * @param nebulaColor 성운 색상
 * @param content 배경 위에 표시할 콘텐츠
 */
@Composable
fun StarFieldBackground(
    modifier: Modifier = Modifier,
    starCount: Int = 80,
    showNebula: Boolean = true,
    nebulaColor: Color = RoyalPurple,
    content: @Composable BoxScope.() -> Unit
) {
    val stars = remember { generateStars(starCount) }

    // 별 깜빡임을 위한 애니메이션
    val infiniteTransition = rememberInfiniteTransition(label = "star_blink")
    val blinkProgress by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(5000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "blink_progress"
    )

    Box(modifier = modifier.fillMaxSize()) {
        // 배경 그라디언트
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    brush = Brush.verticalGradient(
                        colors = listOf(
                            DeepNavy,
                            if (showNebula) nebulaColor.copy(alpha = 0.3f) else DeepNavy,
                            DeepNavy
                        )
                    )
                )
        )

        // 성운 효과 (선택적)
        if (showNebula) {
            Canvas(modifier = Modifier.fillMaxSize()) {
                // 첫 번째 성운
                drawCircle(
                    brush = Brush.radialGradient(
                        colors = listOf(
                            nebulaColor.copy(alpha = 0.15f),
                            nebulaColor.copy(alpha = 0.05f),
                            Color.Transparent
                        ),
                        center = Offset(size.width * 0.3f, size.height * 0.4f),
                        radius = size.width * 0.5f
                    ),
                    center = Offset(size.width * 0.3f, size.height * 0.4f),
                    radius = size.width * 0.5f
                )

                // 두 번째 성운
                drawCircle(
                    brush = Brush.radialGradient(
                        colors = listOf(
                            Gold.copy(alpha = 0.08f),
                            Gold.copy(alpha = 0.02f),
                            Color.Transparent
                        ),
                        center = Offset(size.width * 0.7f, size.height * 0.6f),
                        radius = size.width * 0.4f
                    ),
                    center = Offset(size.width * 0.7f, size.height * 0.6f),
                    radius = size.width * 0.4f
                )
            }
        }

        // 별 그리기
        Canvas(modifier = Modifier.fillMaxSize()) {
            stars.forEach { star ->
                // 각 별마다 다른 깜빡임 계산
                val adjustedProgress = (blinkProgress + star.blinkPhase) % 1f
                val blinkFactor = kotlin.math.sin(adjustedProgress * 2 * Math.PI).toFloat()
                val alpha = star.baseAlpha + (blinkFactor * 0.3f)

                val x = star.x * size.width
                val y = star.y * size.height

                // 별 빛 (외곽 glow)
                drawCircle(
                    color = Gold.copy(alpha = (alpha * 0.3f).coerceIn(0f, 1f)),
                    radius = star.size * 3f,
                    center = Offset(x, y)
                )

                // 별 중심
                drawCircle(
                    color = Color.White.copy(alpha = alpha.coerceIn(0f, 1f)),
                    radius = star.size,
                    center = Offset(x, y)
                )
            }
        }

        // 콘텐츠
        content()
    }
}

/**
 * 단순 별 배경 (콘텐츠 없이 배경만)
 */
@Composable
fun StarFieldCanvas(
    modifier: Modifier = Modifier,
    starCount: Int = 80,
    showNebula: Boolean = true,
    nebulaColor: Color = RoyalPurple
) {
    StarFieldBackground(
        modifier = modifier,
        starCount = starCount,
        showNebula = showNebula,
        nebulaColor = nebulaColor
    ) {}
}
