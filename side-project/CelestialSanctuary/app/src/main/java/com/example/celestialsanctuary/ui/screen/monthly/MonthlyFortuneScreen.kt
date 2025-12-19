package com.example.celestialsanctuary.ui.screen.monthly

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.slideInVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Tab
import androidx.compose.material3.TabRow
import androidx.compose.material3.TabRowDefaults
import androidx.compose.material3.TabRowDefaults.tabIndicatorOffset
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
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
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
import com.example.celestialsanctuary.util.ShareManager
import kotlinx.coroutines.delay

/**
 * 월간 운세 화면
 */
@Composable
fun MonthlyFortuneScreen(
    onBackClick: () -> Unit,
    viewModel: MonthlyFortuneViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

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
            // 헤더
            MonthlyHeader(onBackClick = onBackClick)

            Spacer(modifier = Modifier.height(16.dp))

            // 탭 (이번 달 / 다음 달)
            TabRow(
                selectedTabIndex = uiState.selectedTab,
                containerColor = Color.Transparent,
                contentColor = Gold,
                indicator = { tabPositions ->
                    TabRowDefaults.SecondaryIndicator(
                        modifier = Modifier.tabIndicatorOffset(tabPositions[uiState.selectedTab]),
                        color = Gold
                    )
                }
            ) {
                Tab(
                    selected = uiState.selectedTab == 0,
                    onClick = { viewModel.selectTab(0) },
                    text = {
                        Text(
                            "📅 이번 달",
                            color = if (uiState.selectedTab == 0) Gold else Gold.copy(alpha = 0.5f)
                        )
                    }
                )
                Tab(
                    selected = uiState.selectedTab == 1,
                    onClick = { viewModel.selectTab(1) },
                    text = {
                        Text(
                            "🔮 다음 달",
                            color = if (uiState.selectedTab == 1) Gold else Gold.copy(alpha = 0.5f)
                        )
                    }
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            // 콘텐츠
            val fortune = if (uiState.selectedTab == 0) uiState.currentMonth else uiState.nextMonth

            fortune?.let {
                MonthlyFortuneContent(fortune = it)
            }
        }
    }
}

@Composable
private fun MonthlyHeader(onBackClick: () -> Unit) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        IconButton(onClick = onBackClick) {
            Icon(
                imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                contentDescription = "뒤로가기",
                tint = Gold
            )
        }

        Spacer(modifier = Modifier.weight(1f))

        Text(
            text = "🌙 월간 운세 🌙",
            fontSize = 22.sp,
            fontWeight = FontWeight.Bold,
            color = Gold
        )

        Spacer(modifier = Modifier.weight(1f))

        Spacer(modifier = Modifier.width(48.dp))
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun MonthlyFortuneContent(fortune: MonthlyFortune) {
    var isVisible by remember { mutableStateOf(false) }

    LaunchedEffect(fortune) {
        isVisible = false
        delay(100)
        isVisible = true
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
    ) {
        AnimatedVisibility(
            visible = isVisible,
            enter = fadeIn(tween(500)) + slideInVertically(tween(500)) { it / 2 }
        ) {
            Column {
                // 월 표시 및 테마
                MonthHeader(fortune = fortune)

                Spacer(modifier = Modifier.height(16.dp))

                // 전체 운세
                OverallFortuneCard(fortune = fortune)

                Spacer(modifier = Modifier.height(16.dp))

                // 주차별 하이라이트
                WeeklyHighlightsCard(highlights = fortune.weeklyHighlights)

                Spacer(modifier = Modifier.height(16.dp))

                // 행운/주의 날짜
                SpecialDaysCard(
                    luckyDays = fortune.luckyDays,
                    cautionDays = fortune.cautionDays
                )

                Spacer(modifier = Modifier.height(16.dp))

                // 행운 아이템
                LuckyItemsCard(fortune = fortune)

                // 특별 이벤트
                fortune.specialEvent?.let { event ->
                    Spacer(modifier = Modifier.height(16.dp))
                    SpecialEventCard(event = event)
                }

                Spacer(modifier = Modifier.height(24.dp))
            }
        }
    }
}

@Composable
private fun MonthHeader(fortune: MonthlyFortune) {
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
                shape = RoundedCornerShape(16.dp)
            )
            .border(1.dp, Gold.copy(alpha = 0.3f), RoundedCornerShape(16.dp))
            .padding(20.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "${fortune.year}년",
            fontSize = 14.sp,
            color = Gold.copy(alpha = 0.7f)
        )
        Text(
            text = fortune.monthName,
            fontSize = 36.sp,
            fontWeight = FontWeight.Bold,
            color = Gold
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = "✨ ${fortune.theme} ✨",
            fontSize = 18.sp,
            fontWeight = FontWeight.Medium,
            color = GoldLight
        )

        Spacer(modifier = Modifier.height(12.dp))

        // 운세 레벨
        Row(
            horizontalArrangement = Arrangement.Center
        ) {
            repeat(fortune.fortuneLevel) {
                Text("⭐", fontSize = 24.sp)
            }
            repeat(5 - fortune.fortuneLevel) {
                Text("☆", fontSize = 24.sp, color = Gold.copy(alpha = 0.3f))
            }
        }
    }
}

@Composable
private fun OverallFortuneCard(fortune: MonthlyFortune) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(
                        NavyLight.copy(alpha = 0.8f),
                        DeepNavy.copy(alpha = 0.6f)
                    )
                ),
                shape = RoundedCornerShape(16.dp)
            )
            .border(1.dp, Gold.copy(alpha = 0.3f), RoundedCornerShape(16.dp))
            .padding(20.dp)
    ) {
        Text(
            text = "🔮 종합 운세",
            fontSize = 16.sp,
            fontWeight = FontWeight.Bold,
            color = Gold
        )

        Spacer(modifier = Modifier.height(12.dp))

        Text(
            text = fortune.overallFortune,
            fontSize = 15.sp,
            color = Color.White,
            lineHeight = 24.sp
        )
    }
}

@Composable
private fun WeeklyHighlightsCard(highlights: List<WeekHighlight>) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(
                        NavyLight.copy(alpha = 0.8f),
                        DeepNavy.copy(alpha = 0.6f)
                    )
                ),
                shape = RoundedCornerShape(16.dp)
            )
            .border(1.dp, Gold.copy(alpha = 0.3f), RoundedCornerShape(16.dp))
            .padding(20.dp)
    ) {
        Text(
            text = "📊 주차별 흐름",
            fontSize = 16.sp,
            fontWeight = FontWeight.Bold,
            color = Gold
        )

        Spacer(modifier = Modifier.height(16.dp))

        highlights.forEach { week ->
            WeekRow(week = week)
            if (week != highlights.last()) {
                Spacer(modifier = Modifier.height(12.dp))
            }
        }
    }
}

@Composable
private fun WeekRow(week: WeekHighlight) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                color = RoyalPurple.copy(alpha = 0.2f),
                shape = RoundedCornerShape(12.dp)
            )
            .padding(12.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // 주차 번호
        Box(
            modifier = Modifier
                .size(36.dp)
                .background(Gold.copy(alpha = 0.2f), CircleShape)
                .border(1.dp, Gold.copy(alpha = 0.5f), CircleShape),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "${week.weekNumber}주",
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                color = Gold
            )
        }

        Spacer(modifier = Modifier.width(12.dp))

        Column(
            modifier = Modifier.weight(1f)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = week.dateRange,
                    fontSize = 12.sp,
                    color = Gold.copy(alpha = 0.7f)
                )
                Spacer(modifier = Modifier.width(8.dp))
                // 에너지 레벨
                repeat(week.energyLevel) {
                    Text("●", fontSize = 6.sp, color = GoldLight)
                }
                repeat(5 - week.energyLevel) {
                    Text("○", fontSize = 6.sp, color = Gold.copy(alpha = 0.3f))
                }
            }
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "포커스: ${week.focus}",
                fontSize = 13.sp,
                fontWeight = FontWeight.Medium,
                color = Color.White
            )
            Text(
                text = week.advice,
                fontSize = 12.sp,
                color = Color.White.copy(alpha = 0.7f)
            )
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun SpecialDaysCard(
    luckyDays: List<Int>,
    cautionDays: List<Int>
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(
                        NavyLight.copy(alpha = 0.8f),
                        DeepNavy.copy(alpha = 0.6f)
                    )
                ),
                shape = RoundedCornerShape(16.dp)
            )
            .border(1.dp, Gold.copy(alpha = 0.3f), RoundedCornerShape(16.dp))
            .padding(20.dp)
    ) {
        Text(
            text = "📆 특별한 날",
            fontSize = 16.sp,
            fontWeight = FontWeight.Bold,
            color = Gold
        )

        Spacer(modifier = Modifier.height(16.dp))

        // 행운의 날
        Row(
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("🍀 행운의 날: ", fontSize = 14.sp, color = Color(0xFF4CAF50))
            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                luckyDays.forEach { day ->
                    DayChip(day = day, isLucky = true)
                }
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        // 주의할 날
        Row(
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("⚠️ 주의할 날: ", fontSize = 14.sp, color = Color(0xFFFF9800))
            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                cautionDays.forEach { day ->
                    DayChip(day = day, isLucky = false)
                }
            }
        }
    }
}

@Composable
private fun DayChip(day: Int, isLucky: Boolean) {
    Box(
        modifier = Modifier
            .background(
                color = if (isLucky) Color(0xFF4CAF50).copy(alpha = 0.2f)
                else Color(0xFFFF9800).copy(alpha = 0.2f),
                shape = RoundedCornerShape(8.dp)
            )
            .border(
                width = 1.dp,
                color = if (isLucky) Color(0xFF4CAF50).copy(alpha = 0.5f)
                else Color(0xFFFF9800).copy(alpha = 0.5f),
                shape = RoundedCornerShape(8.dp)
            )
            .padding(horizontal = 10.dp, vertical = 4.dp)
    ) {
        Text(
            text = "${day}일",
            fontSize = 12.sp,
            color = if (isLucky) Color(0xFF4CAF50) else Color(0xFFFF9800)
        )
    }
}

@Composable
private fun LuckyItemsCard(fortune: MonthlyFortune) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                brush = Brush.horizontalGradient(
                    colors = listOf(
                        NavyLight.copy(alpha = 0.8f),
                        RoyalPurple.copy(alpha = 0.5f),
                        NavyLight.copy(alpha = 0.8f)
                    )
                ),
                shape = RoundedCornerShape(16.dp)
            )
            .border(1.dp, Gold.copy(alpha = 0.3f), RoundedCornerShape(16.dp))
            .padding(20.dp),
        horizontalArrangement = Arrangement.SpaceEvenly
    ) {
        LuckyItemColumn(icon = "🎨", label = "행운 색상", value = fortune.luckyColor)
        LuckyItemColumn(icon = "🔢", label = "행운 숫자", value = "${fortune.luckyNumber}")
        LuckyItemColumn(icon = "💎", label = "행운 아이템", value = fortune.luckyItem)
    }
}

@Composable
private fun LuckyItemColumn(icon: String, label: String, value: String) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(icon, fontSize = 28.sp)
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = label,
            fontSize = 11.sp,
            color = Gold.copy(alpha = 0.7f)
        )
        Text(
            text = value,
            fontSize = 13.sp,
            fontWeight = FontWeight.Bold,
            color = Gold,
            textAlign = TextAlign.Center
        )
    }
}

@Composable
private fun SpecialEventCard(event: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                brush = Brush.horizontalGradient(
                    colors = listOf(
                        Color(0xFF9C27B0).copy(alpha = 0.3f),
                        Color(0xFF673AB7).copy(alpha = 0.3f)
                    )
                ),
                shape = RoundedCornerShape(16.dp)
            )
            .border(1.dp, Color(0xFFBA68C8).copy(alpha = 0.5f), RoundedCornerShape(16.dp))
            .padding(16.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text("🌟", fontSize = 32.sp)
        Spacer(modifier = Modifier.width(12.dp))
        Column {
            Text(
                text = "이번 달 특별 천문 이벤트",
                fontSize = 12.sp,
                color = Color(0xFFBA68C8)
            )
            Text(
                text = event,
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium,
                color = Color.White
            )
        }
    }
}
