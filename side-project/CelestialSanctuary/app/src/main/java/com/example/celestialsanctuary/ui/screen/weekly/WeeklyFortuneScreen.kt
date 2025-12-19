package com.example.celestialsanctuary.ui.screen.weekly

import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.example.celestialsanctuary.ui.component.StarFieldBackground
import com.example.celestialsanctuary.ui.theme.DeepNavy
import com.example.celestialsanctuary.ui.theme.Gold
import com.example.celestialsanctuary.ui.theme.GoldDark
import com.example.celestialsanctuary.ui.theme.GoldLight
import com.example.celestialsanctuary.ui.theme.NavyLight
import com.example.celestialsanctuary.ui.theme.RoyalPurple

/**
 * 주간 운세 화면
 * 이번 주 7일간의 운세를 한눈에 볼 수 있음
 */
@Composable
fun WeeklyFortuneScreen(
    onBackClick: () -> Unit,
    viewModel: WeeklyFortuneViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var selectedDayIndex by remember { mutableStateOf(uiState.todayIndex) }

    StarFieldBackground(
        modifier = Modifier.fillMaxSize(),
        starCount = 60,
        showNebula = true,
        nebulaColor = RoyalPurple.copy(alpha = 0.4f)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp)
        ) {
            // 헤더
            WeeklyHeader(
                onBackClick = onBackClick,
                weekRange = uiState.weekRange
            )

            Spacer(modifier = Modifier.height(20.dp))

            // 요일 선택 바
            DaySelector(
                days = uiState.days,
                selectedIndex = selectedDayIndex,
                todayIndex = uiState.todayIndex,
                onDaySelected = { selectedDayIndex = it }
            )

            Spacer(modifier = Modifier.height(24.dp))

            // 선택된 날의 운세 상세
            uiState.days.getOrNull(selectedDayIndex)?.let { selectedDay ->
                DayFortuneDetail(
                    dayFortune = selectedDay,
                    isToday = selectedDayIndex == uiState.todayIndex
                )
            }
        }
    }
}

@Composable
private fun WeeklyHeader(
    onBackClick: () -> Unit,
    weekRange: String
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        IconButton(
            onClick = onBackClick,
            modifier = Modifier
                .size(40.dp)
                .background(NavyLight.copy(alpha = 0.5f), CircleShape)
        ) {
            Icon(
                imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                contentDescription = "뒤로가기",
                tint = Gold
            )
        }

        Spacer(modifier = Modifier.weight(1f))

        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(
                text = "📅 주간 운세",
                fontSize = 22.sp,
                fontWeight = FontWeight.Bold,
                color = Gold
            )
            Text(
                text = weekRange,
                fontSize = 12.sp,
                color = Gold.copy(alpha = 0.7f)
            )
        }

        Spacer(modifier = Modifier.weight(1f))

        // 균형을 위한 공간
        Spacer(modifier = Modifier.width(40.dp))
    }
}

@Composable
private fun DaySelector(
    days: List<DayFortune>,
    selectedIndex: Int,
    todayIndex: Int,
    onDaySelected: (Int) -> Unit
) {
    LazyRow(
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        contentPadding = PaddingValues(horizontal = 4.dp)
    ) {
        itemsIndexed(days) { index, day ->
            DaySelectorItem(
                dayFortune = day,
                isSelected = index == selectedIndex,
                isToday = index == todayIndex,
                onClick = { onDaySelected(index) }
            )
        }
    }
}

@Composable
private fun DaySelectorItem(
    dayFortune: DayFortune,
    isSelected: Boolean,
    isToday: Boolean,
    onClick: () -> Unit
) {
    val scale by animateFloatAsState(
        targetValue = if (isSelected) 1.1f else 1f,
        animationSpec = tween(200),
        label = "scale"
    )

    val infiniteTransition = rememberInfiniteTransition(label = "today")
    val todayGlow by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 0.8f,
        animationSpec = infiniteRepeatable(
            animation = tween(1500, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "glow"
    )

    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier
            .scale(scale)
            .clip(RoundedCornerShape(12.dp))
            .background(
                color = when {
                    isSelected -> Gold.copy(alpha = 0.2f)
                    else -> NavyLight.copy(alpha = 0.5f)
                }
            )
            .border(
                width = if (isSelected) 2.dp else 1.dp,
                color = when {
                    isToday -> Gold.copy(alpha = todayGlow)
                    isSelected -> Gold
                    else -> GoldDark.copy(alpha = 0.3f)
                },
                shape = RoundedCornerShape(12.dp)
            )
            .clickable(onClick = onClick)
            .padding(horizontal = 12.dp, vertical = 8.dp)
    ) {
        // 요일
        Text(
            text = dayFortune.dayOfWeek,
            fontSize = 12.sp,
            color = if (isSelected) Gold else Gold.copy(alpha = 0.6f)
        )

        // 날짜
        Text(
            text = "${dayFortune.dayOfMonth}",
            fontSize = 18.sp,
            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
            color = if (isSelected) Gold else Gold.copy(alpha = 0.8f)
        )

        // 운세 레벨 표시
        Text(
            text = when (dayFortune.fortuneLevel) {
                5 -> "⭐"
                4 -> "✨"
                3 -> "☆"
                2 -> "·"
                else -> "··"
            },
            fontSize = 14.sp,
            color = getFortuneColor(dayFortune.fortuneLevel)
        )

        // 오늘 표시
        if (isToday) {
            Box(
                modifier = Modifier
                    .padding(top = 4.dp)
                    .background(Gold, RoundedCornerShape(4.dp))
                    .padding(horizontal = 6.dp, vertical = 2.dp)
            ) {
                Text(
                    text = "오늘",
                    fontSize = 8.sp,
                    fontWeight = FontWeight.Bold,
                    color = DeepNavy
                )
            }
        }
    }
}

@Composable
private fun DayFortuneDetail(
    dayFortune: DayFortune,
    isToday: Boolean
) {
    LazyColumn(
        verticalArrangement = Arrangement.spacedBy(16.dp),
        modifier = Modifier.fillMaxSize()
    ) {
        // 날짜 헤더
        item {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = dayFortune.fullDate,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = Gold
                )

                if (isToday) {
                    Spacer(modifier = Modifier.width(8.dp))
                    Box(
                        modifier = Modifier
                            .background(Color(0xFFFF6B6B), RoundedCornerShape(8.dp))
                            .padding(horizontal = 8.dp, vertical = 4.dp)
                    ) {
                        Text(
                            text = "TODAY",
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                    }
                }
            }
        }

        // 운세 레벨 카드
        item {
            FortuneLevelCard(level = dayFortune.fortuneLevel)
        }

        // 종합 운세
        item {
            FortuneSection(
                title = "종합 운세",
                icon = "🌟",
                content = dayFortune.generalFortune
            )
        }

        // 사랑 운
        item {
            FortuneSection(
                title = "사랑 운",
                icon = "💕",
                content = dayFortune.loveFortune
            )
        }

        // 재물 운
        item {
            FortuneSection(
                title = "재물 운",
                icon = "💰",
                content = dayFortune.moneyFortune
            )
        }

        // 건강 운
        item {
            FortuneSection(
                title = "건강 운",
                icon = "💪",
                content = dayFortune.healthFortune
            )
        }

        // 조언
        item {
            AdviceCard(advice = dayFortune.advice)
        }

        // 행운 아이템
        item {
            LuckyItemsCard(
                luckyColor = dayFortune.luckyColor,
                luckyNumber = dayFortune.luckyNumber,
                luckyDirection = dayFortune.luckyDirection
            )
        }

        // 하단 여백
        item {
            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}

@Composable
private fun FortuneLevelCard(level: Int) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp))
            .background(
                brush = Brush.horizontalGradient(
                    colors = listOf(
                        getFortuneColor(level).copy(alpha = 0.3f),
                        NavyLight.copy(alpha = 0.6f),
                        getFortuneColor(level).copy(alpha = 0.3f)
                    )
                )
            )
            .border(
                width = 1.dp,
                color = getFortuneColor(level).copy(alpha = 0.5f),
                shape = RoundedCornerShape(16.dp)
            )
            .padding(20.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "오늘의 운세 지수",
                fontSize = 14.sp,
                color = MaterialTheme.colorScheme.onSurface
            )

            Spacer(modifier = Modifier.width(16.dp))

            // 별 표시
            repeat(5) { index ->
                Text(
                    text = if (index < level) "⭐" else "☆",
                    fontSize = 24.sp,
                    color = if (index < level) Gold else Gold.copy(alpha = 0.3f)
                )
            }
        }
    }
}

@Composable
private fun FortuneSection(
    title: String,
    icon: String,
    content: String
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp))
            .background(NavyLight.copy(alpha = 0.6f))
            .border(1.dp, GoldDark.copy(alpha = 0.3f), RoundedCornerShape(16.dp))
            .padding(16.dp)
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(icon, fontSize = 20.sp)
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = title,
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                color = Gold
            )
        }

        Spacer(modifier = Modifier.height(12.dp))

        Text(
            text = content,
            fontSize = 14.sp,
            color = MaterialTheme.colorScheme.onSurface,
            lineHeight = 22.sp
        )
    }
}

@Composable
private fun AdviceCard(advice: String) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp))
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(
                        RoyalPurple.copy(alpha = 0.4f),
                        NavyLight.copy(alpha = 0.6f)
                    )
                )
            )
            .border(1.dp, Gold.copy(alpha = 0.3f), RoundedCornerShape(16.dp))
            .padding(16.dp)
    ) {
        Column {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("💡", fontSize = 20.sp)
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "오늘의 조언",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    color = Gold
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            Text(
                text = "\"$advice\"",
                fontSize = 15.sp,
                fontWeight = FontWeight.Medium,
                color = Color.White,
                textAlign = TextAlign.Center,
                lineHeight = 24.sp,
                modifier = Modifier.fillMaxWidth()
            )
        }
    }
}

@Composable
private fun LuckyItemsCard(
    luckyColor: String,
    luckyNumber: Int,
    luckyDirection: String
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp))
            .background(NavyLight.copy(alpha = 0.6f))
            .border(1.dp, GoldDark.copy(alpha = 0.3f), RoundedCornerShape(16.dp))
            .padding(16.dp),
        horizontalArrangement = Arrangement.SpaceEvenly
    ) {
        LuckyItem(icon = "🎨", label = "행운 색상", value = luckyColor)
        LuckyItem(icon = "🔢", label = "행운 숫자", value = "$luckyNumber")
        LuckyItem(icon = "🧭", label = "행운 방향", value = luckyDirection)
    }
}

@Composable
private fun LuckyItem(
    icon: String,
    label: String,
    value: String
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(icon, fontSize = 24.sp)
        Text(
            text = label,
            fontSize = 10.sp,
            color = Gold.copy(alpha = 0.6f)
        )
        Text(
            text = value,
            fontSize = 14.sp,
            fontWeight = FontWeight.Bold,
            color = Gold
        )
    }
}

private fun getFortuneColor(level: Int): Color {
    return when (level) {
        5 -> Color(0xFFFFD700) // 금색
        4 -> Color(0xFF4CAF50) // 초록
        3 -> Color(0xFF2196F3) // 파랑
        2 -> Color(0xFFFF9800) // 주황
        else -> Color(0xFF9E9E9E) // 회색
    }
}
