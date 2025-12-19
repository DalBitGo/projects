package com.example.celestialsanctuary.ui.screen.hall

import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.example.celestialsanctuary.domain.model.House
import com.example.celestialsanctuary.domain.model.HouseState
import com.example.celestialsanctuary.ui.component.CelebrationOverlay
import com.example.celestialsanctuary.ui.component.StarFieldBackground
import com.example.celestialsanctuary.ui.theme.DeepNavy
import com.example.celestialsanctuary.ui.theme.EmptyOrb
import com.example.celestialsanctuary.ui.theme.Gold
import com.example.celestialsanctuary.ui.theme.GoldDark
import com.example.celestialsanctuary.ui.theme.GoldLight
import com.example.celestialsanctuary.ui.theme.NavyLight
import com.example.celestialsanctuary.ui.theme.OwnerGlow
import com.example.celestialsanctuary.ui.theme.RoyalPurple
import com.example.celestialsanctuary.ui.theme.TenantGlow

@Composable
fun HouseHallScreen(
    onHouseClick: (Int) -> Unit,
    onFortuneClick: () -> Unit,
    onWeeklyFortuneClick: () -> Unit,
    onMonthlyFortuneClick: () -> Unit,
    onSettingsClick: () -> Unit,
    viewModel: HouseHallViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    // 축하 효과 표시 상태
    var showCelebration by remember { mutableStateOf(false) }
    var previousVisitedCount by remember { mutableStateOf(0) }

    // 12개 완료 시 축하 효과 트리거
    LaunchedEffect(uiState.visitedCount) {
        if (uiState.isAllExplored && previousVisitedCount < 12 && uiState.visitedCount == 12) {
            showCelebration = true
        }
        previousVisitedCount = uiState.visitedCount
    }

    Box(modifier = Modifier.fillMaxSize()) {
        StarFieldBackground(
        modifier = Modifier.fillMaxSize(),
        starCount = 60,
        showNebula = true,
        nebulaColor = RoyalPurple
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp)
        ) {
            // 개인화된 헤더
            PersonalizedHeader(
                userName = uiState.userName,
                sunSign = uiState.sunSign,
                moonSign = uiState.moonSign,
                ascendant = uiState.ascendant,
                dailyFortune = uiState.dailyFortune,
                onSettingsClick = onSettingsClick
            )

            Spacer(modifier = Modifier.height(12.dp))

            // 운세 배너들 - 일일
            DailyFortuneBanner(
                onClick = onFortuneClick,
                modifier = Modifier.fillMaxWidth()
            )

            Spacer(modifier = Modifier.height(8.dp))

            // 주간/월간 배너
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                // 주간 운세 배너
                WeeklyFortuneBanner(
                    onClick = onWeeklyFortuneClick,
                    modifier = Modifier.weight(1f)
                )

                // 월간 운세 배너
                MonthlyFortuneBanner(
                    onClick = onMonthlyFortuneClick,
                    modifier = Modifier.weight(1f)
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            // 탐험 진행도
            ExplorationProgressBar(
                visited = uiState.visitedCount,
                total = uiState.totalHouses,
                isComplete = uiState.isAllExplored
            )

            Spacer(modifier = Modifier.height(16.dp))

            // 로딩 중이거나 하우스가 비어있으면 기본 12개 하우스 표시
            val displayHouses = if (uiState.houses.isEmpty()) {
                House.ALL_HOUSES.map { HouseWithState(it, HouseState.EMPTY) }
            } else {
                uiState.houses
            }

            Box(modifier = Modifier.fillMaxSize()) {
                // House Grid
                LazyVerticalGrid(
                    columns = GridCells.Fixed(3),
                    contentPadding = PaddingValues(8.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                    modifier = Modifier.fillMaxSize()
                ) {
                    items(displayHouses) { houseWithState ->
                        HouseDoorCard(
                            houseWithState = houseWithState,
                            onClick = { onHouseClick(houseWithState.house.index) }
                        )
                    }
                }

                // 로딩 인디케이터 오버레이
                if (uiState.isLoading) {
                    CircularProgressIndicator(
                        color = Gold,
                        modifier = Modifier.align(Alignment.Center)
                    )
                }
            }
        }
        }

        // 축하 오버레이
        CelebrationOverlay(
            visible = showCelebration,
            onDismiss = { showCelebration = false }
        )
    }
}

@Composable
private fun HouseDoorCard(
    houseWithState: HouseWithState,
    onClick: () -> Unit
) {
    val house = houseWithState.house
    val state = houseWithState.state

    // 프레스 상태 추적
    var isPressed by remember { mutableStateOf(false) }

    // 프레스 시 스케일 애니메이션
    val scale by animateFloatAsState(
        targetValue = if (isPressed) 0.95f else 1f,
        animationSpec = tween(100),
        label = "card_scale"
    )

    // 프레스 시 글로우 강도
    val glowIntensity by animateFloatAsState(
        targetValue = if (isPressed) 1f else 0f,
        animationSpec = tween(150),
        label = "glow_intensity"
    )

    val borderColor = when (state) {
        HouseState.EMPTY -> GoldDark
        HouseState.TENANT -> TenantGlow
        HouseState.OWNER_HOME -> OwnerGlow
    }

    val glowColor = when (state) {
        HouseState.EMPTY -> Gold
        HouseState.TENANT -> TenantGlow
        HouseState.OWNER_HOME -> GoldLight
    }

    Box(
        modifier = Modifier
            .aspectRatio(0.75f)
            .scale(scale)
            .shadow(
                elevation = (8 + glowIntensity * 16).dp,
                shape = RoundedCornerShape(12.dp),
                ambientColor = glowColor.copy(alpha = 0.5f),
                spotColor = glowColor
            )
            .clip(RoundedCornerShape(12.dp))
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(
                        NavyLight,
                        NavyLight.copy(alpha = 0.9f),
                        if (glowIntensity > 0) glowColor.copy(alpha = glowIntensity * 0.2f)
                        else NavyLight.copy(alpha = 0.8f)
                    )
                )
            )
            .border(
                width = if (state == HouseState.OWNER_HOME) 3.dp else 2.dp,
                brush = Brush.verticalGradient(
                    colors = listOf(
                        borderColor,
                        borderColor.copy(alpha = 0.6f + glowIntensity * 0.4f)
                    )
                ),
                shape = RoundedCornerShape(12.dp)
            )
            .pointerInput(Unit) {
                detectTapGestures(
                    onPress = {
                        isPressed = true
                        tryAwaitRelease()
                        isPressed = false
                        onClick()
                    }
                )
            }
            .padding(8.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // Status indicator with glow
            Box(
                modifier = Modifier
                    .size(14.dp)
                    .shadow(
                        elevation = if (state != HouseState.EMPTY) 12.dp else 0.dp,
                        shape = CircleShape,
                        ambientColor = borderColor,
                        spotColor = borderColor
                    )
                    .background(
                        brush = Brush.radialGradient(
                            colors = when (state) {
                                HouseState.EMPTY -> listOf(EmptyOrb, EmptyOrb.copy(alpha = 0.5f))
                                HouseState.TENANT -> listOf(TenantGlow, TenantGlow.copy(alpha = 0.6f))
                                HouseState.OWNER_HOME -> listOf(Color.White, OwnerGlow)
                            }
                        ),
                        shape = CircleShape
                    )
            )

            Spacer(modifier = Modifier.height(8.dp))

            // Door icon with gradient
            Text(
                text = "⛩",
                fontSize = 32.sp,
                color = borderColor.copy(alpha = 0.9f + glowIntensity * 0.1f)
            )

            Spacer(modifier = Modifier.height(4.dp))

            Text(
                text = "${house.index}",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = borderColor
            )

            Text(
                text = house.nameEn,
                fontSize = 9.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center
            )

            Text(
                text = house.nameKo,
                fontSize = 9.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            // Planet indicator
            houseWithState.planet?.let { planet ->
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = planet.symbol,
                    fontSize = 14.sp,
                    color = planet.color
                )
            }
        }

        // 방문 표시 배지
        if (houseWithState.isVisited) {
            Box(
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .offset(x = 4.dp, y = (-4).dp)
                    .size(20.dp)
                    .shadow(4.dp, CircleShape, ambientColor = Gold, spotColor = Gold)
                    .background(Gold, CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "✓",
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold,
                    color = DeepNavy
                )
            }
        }
    }
}

/**
 * 개인화된 헤더 - 사용자 이름, 차트 요약, 오늘의 운세
 */
@Composable
private fun PersonalizedHeader(
    userName: String?,
    sunSign: String?,
    moonSign: String?,
    ascendant: String?,
    dailyFortune: String,
    onSettingsClick: () -> Unit
) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // 타이틀 + 설정 버튼
        Box(
            modifier = Modifier.fillMaxWidth()
        ) {
            // 개인화된 타이틀 (중앙)
            val title = if (userName.isNullOrBlank()) {
                "THE 12 HOUSES"
            } else {
                "${userName}의 천궁"
            }

            Text(
                text = title,
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = Gold,
                modifier = Modifier
                    .align(Alignment.Center)
                    .padding(vertical = 8.dp),
                textAlign = TextAlign.Center,
                letterSpacing = if (userName.isNullOrBlank()) 4.sp else 2.sp
            )

            // 설정 버튼 (우측)
            Box(
                modifier = Modifier
                    .align(Alignment.CenterEnd)
                    .size(36.dp)
                    .clip(CircleShape)
                    .background(NavyLight.copy(alpha = 0.6f))
                    .border(1.dp, GoldDark.copy(alpha = 0.5f), CircleShape)
                    .pointerInput(Unit) {
                        detectTapGestures(onTap = { onSettingsClick() })
                    },
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "⚙️",
                    fontSize = 18.sp
                )
            }
        }

        // 태양/달/상승 요약 카드
        if (sunSign != null || moonSign != null || ascendant != null) {
            ChartSummaryCard(
                sunSign = sunSign,
                moonSign = moonSign,
                ascendant = ascendant
            )
            Spacer(modifier = Modifier.height(12.dp))
        }

        // 오늘의 운세
        if (dailyFortune.isNotBlank()) {
            DailyFortuneCard(fortune = dailyFortune)
        }
    }
}

/**
 * 태양/달/상승 요약 카드
 */
@Composable
private fun ChartSummaryCard(
    sunSign: String?,
    moonSign: String?,
    ascendant: String?
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                color = NavyLight.copy(alpha = 0.6f),
                shape = RoundedCornerShape(12.dp)
            )
            .padding(12.dp),
        horizontalArrangement = Arrangement.SpaceEvenly
    ) {
        // 태양
        sunSign?.let {
            ChartSignItem(
                symbol = "☉",
                label = "태양",
                value = it,
                color = Gold
            )
        }

        // 달
        moonSign?.let {
            ChartSignItem(
                symbol = "☽",
                label = "달",
                value = it,
                color = Color(0xFFE0E0E0)
            )
        }

        // 상승
        ascendant?.let {
            ChartSignItem(
                symbol = "↑",
                label = "상승",
                value = it,
                color = GoldLight
            )
        }
    }
}

/**
 * 차트 기호 아이템
 */
@Composable
private fun ChartSignItem(
    symbol: String,
    label: String,
    value: String,
    color: Color
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = symbol,
            fontSize = 20.sp,
            color = color
        )
        Text(
            text = label,
            fontSize = 10.sp,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            fontSize = 12.sp,
            fontWeight = FontWeight.Bold,
            color = color
        )
    }
}

/**
 * 오늘의 운세 카드
 */
@Composable
private fun DailyFortuneCard(fortune: String) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                brush = Brush.horizontalGradient(
                    colors = listOf(
                        RoyalPurple.copy(alpha = 0.3f),
                        NavyLight.copy(alpha = 0.5f),
                        RoyalPurple.copy(alpha = 0.3f)
                    )
                ),
                shape = RoundedCornerShape(12.dp)
            )
            .border(
                width = 1.dp,
                color = Gold.copy(alpha = 0.3f),
                shape = RoundedCornerShape(12.dp)
            )
            .padding(12.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "✨ 오늘의 별빛 메시지 ✨",
            fontSize = 11.sp,
            color = Gold.copy(alpha = 0.8f)
        )
        Spacer(modifier = Modifier.height(6.dp))
        Text(
            text = fortune,
            fontSize = 13.sp,
            color = MaterialTheme.colorScheme.onSurface,
            textAlign = TextAlign.Center,
            lineHeight = 18.sp
        )
    }
}

/**
 * 탐험 진행도 바
 */
@Composable
private fun ExplorationProgressBar(
    visited: Int,
    total: Int,
    isComplete: Boolean
) {
    val progress by animateFloatAsState(
        targetValue = visited.toFloat() / total,
        animationSpec = tween(500),
        label = "progress"
    )

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 8.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center
        ) {
            if (isComplete) {
                Text(
                    text = "✨ 모든 성소를 탐험했습니다! ✨",
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                    color = Gold
                )
            } else {
                Text(
                    text = "탐험 진행",
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "$visited / $total",
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                    color = Gold
                )
            }
        }

        Spacer(modifier = Modifier.height(8.dp))

        // 진행 바
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(6.dp)
                .clip(RoundedCornerShape(3.dp))
                .background(NavyLight)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth(progress)
                    .height(6.dp)
                    .clip(RoundedCornerShape(3.dp))
                    .background(
                        brush = Brush.horizontalGradient(
                            colors = if (isComplete) {
                                listOf(Gold, GoldLight, Gold)
                            } else {
                                listOf(GoldDark, Gold)
                            }
                        )
                    )
            )
        }
    }
}

/**
 * 오늘의 운명 배너 - 게임 스타일 일일 보상 느낌
 */
@Composable
private fun DailyFortuneBanner(
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    // 반짝임 애니메이션
    val infiniteTransition = rememberInfiniteTransition(label = "fortune_banner")
    val shimmerAlpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 0.8f,
        animationSpec = infiniteRepeatable(
            animation = tween(1500, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "shimmer"
    )

    var isPressed by remember { mutableStateOf(false) }
    val scale by animateFloatAsState(
        targetValue = if (isPressed) 0.98f else 1f,
        animationSpec = tween(100),
        label = "banner_scale"
    )

    Box(
        modifier = modifier
            .scale(scale)
            .shadow(
                elevation = 8.dp,
                shape = RoundedCornerShape(16.dp),
                ambientColor = Gold.copy(alpha = 0.3f),
                spotColor = Gold.copy(alpha = 0.5f)
            )
            .clip(RoundedCornerShape(16.dp))
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(
                        RoyalPurple.copy(alpha = 0.9f),
                        DeepNavy
                    )
                )
            )
            .border(
                width = 2.dp,
                brush = Brush.verticalGradient(
                    colors = listOf(
                        Gold.copy(alpha = shimmerAlpha),
                        GoldLight.copy(alpha = 0.5f)
                    )
                ),
                shape = RoundedCornerShape(16.dp)
            )
            .pointerInput(Unit) {
                detectTapGestures(
                    onPress = {
                        isPressed = true
                        tryAwaitRelease()
                        isPressed = false
                        onClick()
                    }
                )
            }
            .padding(12.dp)
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // 아이콘들
            Row {
                Text(text = "🔮", fontSize = 20.sp)
                Text(text = "🃏", fontSize = 18.sp)
                Text(text = "🎲", fontSize = 18.sp)
            }

            Spacer(modifier = Modifier.height(6.dp))

            Text(
                text = "오늘의 운명",
                fontSize = 14.sp,
                fontWeight = FontWeight.Bold,
                color = Gold
            )

            Text(
                text = "수정구슬 · 타로 · 주사위",
                fontSize = 9.sp,
                color = Gold.copy(alpha = 0.7f)
            )
        }
    }
}

/**
 * 주간 운세 배너
 */
@Composable
private fun WeeklyFortuneBanner(
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val infiniteTransition = rememberInfiniteTransition(label = "weekly_banner")
    val shimmerAlpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 0.7f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "shimmer"
    )

    var isPressed by remember { mutableStateOf(false) }
    val scale by animateFloatAsState(
        targetValue = if (isPressed) 0.98f else 1f,
        animationSpec = tween(100),
        label = "banner_scale"
    )

    Box(
        modifier = modifier
            .scale(scale)
            .shadow(
                elevation = 8.dp,
                shape = RoundedCornerShape(16.dp),
                ambientColor = Color(0xFF4CAF50).copy(alpha = 0.3f),
                spotColor = Color(0xFF4CAF50).copy(alpha = 0.5f)
            )
            .clip(RoundedCornerShape(16.dp))
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(
                        Color(0xFF1B5E20).copy(alpha = 0.9f),
                        DeepNavy
                    )
                )
            )
            .border(
                width = 2.dp,
                brush = Brush.verticalGradient(
                    colors = listOf(
                        Color(0xFF4CAF50).copy(alpha = shimmerAlpha),
                        Color(0xFF81C784).copy(alpha = 0.5f)
                    )
                ),
                shape = RoundedCornerShape(16.dp)
            )
            .pointerInput(Unit) {
                detectTapGestures(
                    onPress = {
                        isPressed = true
                        tryAwaitRelease()
                        isPressed = false
                        onClick()
                    }
                )
            }
            .padding(12.dp)
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(text = "📅", fontSize = 28.sp)

            Spacer(modifier = Modifier.height(6.dp))

            Text(
                text = "주간 운세",
                fontSize = 14.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFF81C784)
            )

            Text(
                text = "7일간의 별자리 운세",
                fontSize = 9.sp,
                color = Color(0xFF81C784).copy(alpha = 0.7f)
            )
        }
    }
}

/**
 * 월간 운세 배너
 */
@Composable
private fun MonthlyFortuneBanner(
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val infiniteTransition = rememberInfiniteTransition(label = "monthly_banner")
    val shimmerAlpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 0.7f,
        animationSpec = infiniteRepeatable(
            animation = tween(2500, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "shimmer"
    )

    var isPressed by remember { mutableStateOf(false) }
    val scale by animateFloatAsState(
        targetValue = if (isPressed) 0.98f else 1f,
        animationSpec = tween(100),
        label = "banner_scale"
    )

    Box(
        modifier = modifier
            .scale(scale)
            .shadow(
                elevation = 8.dp,
                shape = RoundedCornerShape(16.dp),
                ambientColor = Color(0xFF9C27B0).copy(alpha = 0.3f),
                spotColor = Color(0xFF9C27B0).copy(alpha = 0.5f)
            )
            .clip(RoundedCornerShape(16.dp))
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(
                        Color(0xFF4A148C).copy(alpha = 0.9f),
                        DeepNavy
                    )
                )
            )
            .border(
                width = 2.dp,
                brush = Brush.verticalGradient(
                    colors = listOf(
                        Color(0xFF9C27B0).copy(alpha = shimmerAlpha),
                        Color(0xFFBA68C8).copy(alpha = 0.5f)
                    )
                ),
                shape = RoundedCornerShape(16.dp)
            )
            .pointerInput(Unit) {
                detectTapGestures(
                    onPress = {
                        isPressed = true
                        tryAwaitRelease()
                        isPressed = false
                        onClick()
                    }
                )
            }
            .padding(12.dp)
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(text = "🌙", fontSize = 28.sp)

            Spacer(modifier = Modifier.height(6.dp))

            Text(
                text = "월간 운세",
                fontSize = 14.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFFBA68C8)
            )

            Text(
                text = "한 달의 별자리 흐름",
                fontSize = 9.sp,
                color = Color(0xFFBA68C8).copy(alpha = 0.7f)
            )
        }
    }
}
