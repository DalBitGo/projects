package com.example.celestialsanctuary.ui.component

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.scaleIn
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.celestialsanctuary.ui.theme.DeepNavy
import com.example.celestialsanctuary.ui.theme.Gold
import com.example.celestialsanctuary.ui.theme.GoldLight
import kotlinx.coroutines.delay
import kotlin.random.Random

/**
 * 파티클 데이터
 */
private data class CelebrationParticle(
    val id: Int,
    var x: Float,
    var y: Float,
    val vx: Float,
    val vy: Float,
    val color: Color,
    val size: Float,
    val progress: Animatable<Float, *>
)

/**
 * 12개 하우스 탐험 완료 시 축하 오버레이
 */
@Composable
fun CelebrationOverlay(
    visible: Boolean,
    onDismiss: () -> Unit
) {
    val particles = remember { mutableStateListOf<CelebrationParticle>() }

    // 파티클 생성
    LaunchedEffect(visible) {
        if (visible) {
            particles.clear()
            val colors = listOf(Gold, GoldLight, Color.White, Color(0xFFFFE44D))

            repeat(50) { i ->
                val particle = CelebrationParticle(
                    id = i,
                    x = Random.nextFloat(),
                    y = Random.nextFloat() * 0.3f + 0.3f,  // 중앙 부분에서 시작
                    vx = (Random.nextFloat() - 0.5f) * 0.02f,
                    vy = (Random.nextFloat() - 0.5f) * 0.015f - 0.005f,  // 위로 올라감
                    color = colors.random(),
                    size = Random.nextFloat() * 6f + 2f,
                    progress = Animatable(0f)
                )
                particles.add(particle)
            }
        }
    }

    // 빛나는 효과
    val infiniteTransition = rememberInfiniteTransition(label = "celebration")
    val glowPulse by infiniteTransition.animateFloat(
        initialValue = 0.6f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000),
            repeatMode = RepeatMode.Reverse
        ),
        label = "glow"
    )

    AnimatedVisibility(
        visible = visible,
        enter = fadeIn(tween(500)) + scaleIn(tween(500)),
        exit = fadeOut(tween(300))
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(DeepNavy.copy(alpha = 0.85f))
                .clickable(
                    indication = null,
                    interactionSource = remember { MutableInteractionSource() }
                ) { onDismiss() },
            contentAlignment = Alignment.Center
        ) {
            // 파티클 그리기
            Canvas(modifier = Modifier.fillMaxSize()) {
                particles.forEach { particle ->
                    val x = particle.x * size.width
                    val y = particle.y * size.height

                    // 파티클 빛
                    drawCircle(
                        color = particle.color.copy(alpha = 0.3f),
                        radius = particle.size * 2,
                        center = Offset(x, y)
                    )

                    // 파티클
                    drawCircle(
                        color = particle.color,
                        radius = particle.size,
                        center = Offset(x, y)
                    )
                }
            }

            // 축하 메시지
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = Modifier.padding(32.dp)
            ) {
                // 왕관 이모지
                Text(
                    text = "👑",
                    fontSize = 64.sp
                )

                Spacer(modifier = Modifier.height(24.dp))

                // 빛나는 텍스트 박스
                Box(
                    modifier = Modifier
                        .background(
                            color = Gold.copy(alpha = glowPulse * 0.2f),
                            shape = RoundedCornerShape(16.dp)
                        )
                        .padding(24.dp)
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = "축하합니다!",
                            fontSize = 28.sp,
                            fontWeight = FontWeight.Bold,
                            color = Gold
                        )

                        Spacer(modifier = Modifier.height(12.dp))

                        Text(
                            text = "12개의 성소를 모두 탐험했습니다",
                            fontSize = 16.sp,
                            color = GoldLight
                        )

                        Spacer(modifier = Modifier.height(8.dp))

                        Text(
                            text = "당신의 별자리 여정이 완성되었습니다 ✨",
                            fontSize = 14.sp,
                            color = Color.White.copy(alpha = 0.8f),
                            textAlign = TextAlign.Center
                        )
                    }
                }

                Spacer(modifier = Modifier.height(32.dp))

                Text(
                    text = "탭하여 닫기",
                    fontSize = 12.sp,
                    color = Color.White.copy(alpha = 0.5f)
                )
            }
        }
    }
}
