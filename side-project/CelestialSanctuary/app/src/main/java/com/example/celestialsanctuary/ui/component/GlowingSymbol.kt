package com.example.celestialsanctuary.ui.component

import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp
import com.example.celestialsanctuary.ui.theme.Gold
import com.example.celestialsanctuary.ui.theme.GoldLight

/**
 * 빛나는 심볼 컴포넌트
 * 펄스 효과와 함께 빛을 발산하는 심볼
 */
@Composable
fun GlowingSymbol(
    symbol: String,
    modifier: Modifier = Modifier,
    color: Color = Gold,
    glowColor: Color = GoldLight
) {
    val infiniteTransition = rememberInfiniteTransition(label = "glow")

    // 펄스 효과
    val glowAlpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 0.8f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000),
            repeatMode = RepeatMode.Reverse
        ),
        label = "glow_alpha"
    )

    val glowRadius by infiniteTransition.animateFloat(
        initialValue = 0.4f,
        targetValue = 0.6f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000),
            repeatMode = RepeatMode.Reverse
        ),
        label = "glow_radius"
    )

    Box(
        modifier = modifier,
        contentAlignment = Alignment.Center
    ) {
        // 빛 효과 (여러 레이어)
        Canvas(modifier = Modifier.fillMaxSize()) {
            val center = Offset(size.width / 2, size.height / 2)

            // 외곽 글로우 (가장 연함)
            drawCircle(
                brush = Brush.radialGradient(
                    colors = listOf(
                        glowColor.copy(alpha = glowAlpha * 0.2f),
                        glowColor.copy(alpha = glowAlpha * 0.1f),
                        Color.Transparent
                    ),
                    center = center,
                    radius = size.minDimension * glowRadius * 1.5f
                ),
                center = center,
                radius = size.minDimension * glowRadius * 1.5f
            )

            // 중간 글로우
            drawCircle(
                brush = Brush.radialGradient(
                    colors = listOf(
                        color.copy(alpha = glowAlpha * 0.4f),
                        color.copy(alpha = glowAlpha * 0.2f),
                        Color.Transparent
                    ),
                    center = center,
                    radius = size.minDimension * glowRadius
                ),
                center = center,
                radius = size.minDimension * glowRadius
            )

            // 내부 글로우 (가장 밝음)
            drawCircle(
                brush = Brush.radialGradient(
                    colors = listOf(
                        Color.White.copy(alpha = glowAlpha * 0.3f),
                        color.copy(alpha = glowAlpha * 0.5f),
                        Color.Transparent
                    ),
                    center = center,
                    radius = size.minDimension * glowRadius * 0.5f
                ),
                center = center,
                radius = size.minDimension * glowRadius * 0.5f
            )
        }

        // 심볼 텍스트
        Text(
            text = symbol,
            fontSize = 72.sp,
            fontWeight = FontWeight.Bold,
            color = color
        )
    }
}
