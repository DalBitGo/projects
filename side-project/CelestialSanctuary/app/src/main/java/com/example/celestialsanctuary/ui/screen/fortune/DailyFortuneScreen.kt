package com.example.celestialsanctuary.ui.screen.fortune

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.scaleIn
import androidx.compose.animation.scaleOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Tab
import androidx.compose.material3.TabRow
import androidx.compose.material3.TabRowDefaults
import androidx.compose.material3.TabRowDefaults.tabIndicatorOffset
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.blur
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.draw.scale
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.IntOffset
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
import com.example.celestialsanctuary.ui.component.CapturableContent
import com.example.celestialsanctuary.ui.component.rememberCaptureController
import com.example.celestialsanctuary.util.ImageCaptureManager
import com.example.celestialsanctuary.util.ShareManager
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlin.math.absoluteValue
import kotlin.math.roundToInt
import kotlin.random.Random

/**
 * 일일 운세 화면
 * 수정구슬 / 타로카드 / 행운주사위 세 가지 기능 제공
 */
@Composable
fun DailyFortuneScreen(
    onBackClick: () -> Unit,
    viewModel: DailyFortuneViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val pagerState = rememberPagerState(pageCount = { 3 })
    val coroutineScope = rememberCoroutineScope()

    val tabs = listOf(
        FortuneTab("🔮", "수정구슬", uiState.crystalBallRevealed),
        FortuneTab("🃏", "타로카드", uiState.tarotRevealed),
        FortuneTab("🎲", "행운주사위", uiState.diceRolled)
    )

    StarFieldBackground(
        modifier = Modifier.fillMaxSize(),
        starCount = 80,
        showNebula = true,
        nebulaColor = RoyalPurple
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp)
        ) {
            // 헤더
            FortuneHeader(
                onBackClick = onBackClick,
                streakDays = uiState.streakDays,
                allRevealed = uiState.allFortuneRevealed
            )

            Spacer(modifier = Modifier.height(16.dp))

            // 탭 바
            TabRow(
                selectedTabIndex = pagerState.currentPage,
                containerColor = Color.Transparent,
                contentColor = Gold,
                indicator = { tabPositions ->
                    TabRowDefaults.SecondaryIndicator(
                        modifier = Modifier.tabIndicatorOffset(tabPositions[pagerState.currentPage]),
                        color = Gold
                    )
                }
            ) {
                tabs.forEachIndexed { index, tab ->
                    Tab(
                        selected = pagerState.currentPage == index,
                        onClick = {
                            coroutineScope.launch {
                                pagerState.animateScrollToPage(index)
                            }
                        },
                        text = {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Box {
                                    Text(tab.icon, fontSize = 24.sp)
                                    // 완료 체크 표시
                                    if (tab.isCompleted) {
                                        Box(
                                            modifier = Modifier
                                                .align(Alignment.TopEnd)
                                                .offset(x = 8.dp, y = (-4).dp)
                                                .size(14.dp)
                                                .background(Color(0xFF4CAF50), CircleShape),
                                            contentAlignment = Alignment.Center
                                        ) {
                                            Text(
                                                text = "✓",
                                                fontSize = 8.sp,
                                                color = Color.White
                                            )
                                        }
                                    }
                                }
                                Text(
                                    tab.title,
                                    fontSize = 12.sp,
                                    color = if (pagerState.currentPage == index) Gold else Gold.copy(alpha = 0.5f)
                                )
                            }
                        }
                    )
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            // 페이저 콘텐츠
            HorizontalPager(
                state = pagerState,
                modifier = Modifier.weight(1f)
            ) { page ->
                when (page) {
                    0 -> CrystalBallContent(
                        result = uiState.crystalBallResult,
                        isRevealed = uiState.crystalBallRevealed,
                        onReveal = { viewModel.revealCrystalBall() }
                    )
                    1 -> TarotCardContent(
                        cards = uiState.tarotCards,
                        selectedIndex = uiState.selectedTarotIndex,
                        isRevealed = uiState.tarotRevealed,
                        onSelectCard = { viewModel.selectTarotCard(it) }
                    )
                    2 -> DiceContent(
                        result = uiState.diceResult,
                        isRolled = uiState.diceRolled,
                        onRoll = { viewModel.rollDice() }
                    )
                }
            }
        }
    }
}

@Composable
private fun FortuneHeader(
    onBackClick: () -> Unit,
    streakDays: Int = 0,
    allRevealed: Boolean = false
) {
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

        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(
                text = "✨ 오늘의 운명 ✨",
                fontSize = 22.sp,
                fontWeight = FontWeight.Bold,
                color = Gold
            )

            // 연속 접속 표시
            if (streakDays > 1) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.Center
                ) {
                    Text(
                        text = "🔥 ${streakDays}일 연속 접속",
                        fontSize = 12.sp,
                        color = Color(0xFFFF6B6B)
                    )
                    if (allRevealed) {
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "✅ 완료",
                            fontSize = 12.sp,
                            color = Color(0xFF4CAF50)
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.weight(1f))

        // 균형을 위한 빈 공간
        Spacer(modifier = Modifier.width(48.dp))
    }
}

/**
 * 수정구슬 콘텐츠 - 흔들어서 메시지 확인
 */
@Composable
private fun CrystalBallContent(
    result: CrystalBallResult?,
    isRevealed: Boolean,
    onReveal: () -> Unit
) {
    var offsetX by remember { mutableFloatStateOf(0f) }
    var offsetY by remember { mutableFloatStateOf(0f) }
    var isShaking by remember { mutableStateOf(false) }
    var shakeCount by remember { mutableIntStateOf(0) }
    val coroutineScope = rememberCoroutineScope()

    // 글로우 애니메이션
    val infiniteTransition = rememberInfiniteTransition(label = "glow")
    val glowAlpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 0.8f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "glowAlpha"
    )

    Column(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        if (!isRevealed) {
            Text(
                text = "수정구슬을 흔들어 운세를 확인하세요",
                fontSize = 14.sp,
                color = Gold.copy(alpha = 0.7f)
            )

            Spacer(modifier = Modifier.height(32.dp))

            // 수정구슬
            Box(
                modifier = Modifier
                    .size(200.dp)
                    .offset { IntOffset(offsetX.roundToInt(), offsetY.roundToInt()) }
                    .pointerInput(Unit) {
                        detectDragGestures(
                            onDrag = { change, dragAmount ->
                                change.consume()
                                offsetX += dragAmount.x
                                offsetY += dragAmount.y

                                // 흔들림 감지
                                if (dragAmount.x.absoluteValue > 10 || dragAmount.y.absoluteValue > 10) {
                                    shakeCount++
                                    if (shakeCount > 5 && !isShaking) {
                                        isShaking = true
                                    }
                                }
                            },
                            onDragEnd = {
                                coroutineScope.launch {
                                    // 원위치로 복귀
                                    offsetX = 0f
                                    offsetY = 0f

                                    if (isShaking) {
                                        delay(500)
                                        onReveal()
                                    }
                                    shakeCount = 0
                                    isShaking = false
                                }
                            }
                        )
                    },
                contentAlignment = Alignment.Center
            ) {
                // 글로우 효과
                Box(
                    modifier = Modifier
                        .size(220.dp)
                        .blur(30.dp)
                        .background(
                            brush = Brush.radialGradient(
                                colors = listOf(
                                    RoyalPurple.copy(alpha = glowAlpha),
                                    Color.Transparent
                                )
                            ),
                            shape = CircleShape
                        )
                )

                // 구슬 본체
                Box(
                    modifier = Modifier
                        .size(180.dp)
                        .shadow(20.dp, CircleShape)
                        .background(
                            brush = Brush.radialGradient(
                                colors = listOf(
                                    Color.White.copy(alpha = 0.3f),
                                    RoyalPurple.copy(alpha = 0.5f),
                                    DeepNavy.copy(alpha = 0.8f)
                                )
                            ),
                            shape = CircleShape
                        )
                        .border(2.dp, Gold.copy(alpha = 0.5f), CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = if (isShaking) "✨" else "?",
                        fontSize = 48.sp,
                        color = Gold.copy(alpha = if (isShaking) 1f else 0.5f)
                    )
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            Text(
                text = if (isShaking) "운명을 읽는 중..." else "↔ 좌우로 흔들어보세요",
                fontSize = 14.sp,
                color = Gold.copy(alpha = 0.7f)
            )
        } else {
            // 결과 표시
            CrystalBallResultCard(result = result)
        }
    }
}

@Composable
private fun CrystalBallResultCard(result: CrystalBallResult?) {
    val context = LocalContext.current
    val captureController = rememberCaptureController()

    result?.let {
        Column(
            modifier = Modifier.fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // 캡처 가능한 결과 카드
            CapturableContent(
                controller = captureController,
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp)
                        .background(
                            brush = Brush.verticalGradient(
                                colors = listOf(
                                    NavyLight.copy(alpha = 0.95f),
                                    RoyalPurple.copy(alpha = 0.85f)
                                )
                            ),
                            shape = RoundedCornerShape(20.dp)
                        )
                        .border(1.dp, Gold.copy(alpha = 0.5f), RoundedCornerShape(20.dp))
                        .padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text("🔮", fontSize = 48.sp)

                    Spacer(modifier = Modifier.height(16.dp))

                    Text(
                        text = "오늘의 메시지",
                        fontSize = 14.sp,
                        color = Gold.copy(alpha = 0.7f)
                    )

                    Spacer(modifier = Modifier.height(8.dp))

                    Text(
                        text = "\"${it.message}\"",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.White,
                        textAlign = TextAlign.Center,
                        lineHeight = 26.sp
                    )

                    Spacer(modifier = Modifier.height(24.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceEvenly
                    ) {
                        LuckyItem(icon = "🔢", label = "행운숫자", value = it.luckyNumbers.joinToString(", "))
                        LuckyItem(icon = "🎨", label = "행운색상", value = it.luckyColor)
                        LuckyItem(icon = "🧭", label = "행운방향", value = it.luckyDirection)
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    // 앱 워터마크
                    Text(
                        text = "✨ Celestial Sanctuary ✨",
                        fontSize = 10.sp,
                        color = Gold.copy(alpha = 0.5f)
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // 공유/저장 버튼
            ActionButtonGroup(
                onShareClick = {
                    val shareText = ShareManager.createCrystalBallShareText(
                        message = it.message,
                        luckyNumbers = it.luckyNumbers,
                        luckyColor = it.luckyColor,
                        luckyDirection = it.luckyDirection
                    )
                    ShareManager.shareText(context, shareText, "수정구슬 운세")
                },
                onSaveClick = {
                    captureController.capture()?.let { bitmap ->
                        ImageCaptureManager.saveBitmapToGallery(context, bitmap, "crystal_ball")
                    }
                }
            )
        }
    }
}

@Composable
private fun LuckyItem(icon: String, label: String, value: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(icon, fontSize = 24.sp)
        Text(label, fontSize = 10.sp, color = Gold.copy(alpha = 0.6f))
        Text(value, fontSize = 12.sp, fontWeight = FontWeight.Bold, color = Gold)
    }
}

/**
 * 타로카드 콘텐츠 - 3장 중 1장 선택
 */
@Composable
private fun TarotCardContent(
    cards: List<TarotCard>,
    selectedIndex: Int?,
    isRevealed: Boolean,
    onSelectCard: (Int) -> Unit
) {
    Column(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        if (!isRevealed) {
            Text(
                text = "마음을 집중하고 카드를 선택하세요",
                fontSize = 14.sp,
                color = Gold.copy(alpha = 0.7f)
            )

            Spacer(modifier = Modifier.height(32.dp))

            // 3장의 카드
            Row(
                horizontalArrangement = Arrangement.spacedBy(16.dp),
                modifier = Modifier.padding(horizontal = 16.dp)
            ) {
                cards.forEachIndexed { index, card ->
                    TarotCardBack(
                        index = index,
                        isSelected = selectedIndex == index,
                        onClick = { onSelectCard(index) }
                    )
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            Text(
                text = "운명의 카드가 당신을 기다립니다",
                fontSize = 12.sp,
                color = Gold.copy(alpha = 0.5f)
            )
        } else {
            // 선택된 카드 결과
            selectedIndex?.let { idx ->
                TarotCardResult(card = cards[idx])
            }
        }
    }
}

@Composable
private fun TarotCardBack(
    index: Int,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    val scale by animateFloatAsState(
        targetValue = if (isSelected) 1.1f else 1f,
        animationSpec = tween(200),
        label = "cardScale"
    )

    // 카드 호버 애니메이션
    val infiniteTransition = rememberInfiniteTransition(label = "card_$index")
    val hoverOffset by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 8f,
        animationSpec = infiniteRepeatable(
            animation = tween(1500 + index * 200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "hover_$index"
    )

    Box(
        modifier = Modifier
            .width(100.dp)
            .height(150.dp)
            .offset(y = (-hoverOffset).dp)
            .scale(scale)
            .shadow(
                elevation = if (isSelected) 20.dp else 8.dp,
                shape = RoundedCornerShape(12.dp),
                ambientColor = if (isSelected) Gold else RoyalPurple,
                spotColor = if (isSelected) Gold else RoyalPurple
            )
            .clip(RoundedCornerShape(12.dp))
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(
                        RoyalPurple,
                        DeepNavy
                    )
                )
            )
            .border(
                width = if (isSelected) 3.dp else 1.dp,
                color = if (isSelected) Gold else GoldDark,
                shape = RoundedCornerShape(12.dp)
            )
            .clickable { onClick() },
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text("✦", fontSize = 32.sp, color = Gold)
            Spacer(modifier = Modifier.height(8.dp))
            Text("${index + 1}", fontSize = 14.sp, color = Gold.copy(alpha = 0.5f))
        }
    }
}

@Composable
private fun TarotCardResult(card: TarotCard) {
    val context = LocalContext.current
    val captureController = rememberCaptureController()
    var isFlipped by remember { mutableStateOf(false) }
    val rotation by animateFloatAsState(
        targetValue = if (isFlipped) 180f else 0f,
        animationSpec = tween(600),
        label = "flip"
    )

    LaunchedEffect(Unit) {
        delay(300)
        isFlipped = true
    }

    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // 캡처 가능한 카드 영역
        CapturableContent(
            controller = captureController,
            modifier = Modifier.fillMaxWidth()
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(DeepNavy)
                    .padding(32.dp),
                contentAlignment = Alignment.Center
            ) {
                if (rotation <= 90f) {
                    // 카드 뒷면
                    Box(
                        modifier = Modifier
                            .width(200.dp)
                            .height(300.dp)
                            .graphicsLayer {
                                rotationY = rotation
                                cameraDistance = 12f * density
                            }
                            .shadow(16.dp, RoundedCornerShape(16.dp))
                            .background(
                                brush = Brush.verticalGradient(
                                    colors = listOf(RoyalPurple, DeepNavy)
                                ),
                                shape = RoundedCornerShape(16.dp)
                            )
                            .border(2.dp, Gold, RoundedCornerShape(16.dp)),
                        contentAlignment = Alignment.Center
                    ) {
                        Text("✦", fontSize = 64.sp, color = Gold)
                    }
                } else {
                    // 카드 앞면
                    Column(
                        modifier = Modifier
                            .width(200.dp)
                            .height(300.dp)
                            .graphicsLayer {
                                rotationY = rotation
                                rotationY = 180f
                                cameraDistance = 12f * density
                            }
                            .shadow(16.dp, RoundedCornerShape(16.dp))
                            .background(
                                brush = Brush.verticalGradient(
                                    colors = listOf(
                                        NavyLight,
                                        RoyalPurple.copy(alpha = 0.8f)
                                    )
                                ),
                                shape = RoundedCornerShape(16.dp)
                            )
                            .border(2.dp, Gold, RoundedCornerShape(16.dp))
                            .padding(16.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        Text(card.symbol, fontSize = 48.sp)
                        Spacer(modifier = Modifier.height(12.dp))
                        Text(
                            card.name,
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold,
                            color = Gold
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            card.meaning,
                            fontSize = 12.sp,
                            color = Color.White.copy(alpha = 0.8f),
                            textAlign = TextAlign.Center,
                            lineHeight = 18.sp
                        )
                        Spacer(modifier = Modifier.height(12.dp))
                        // 앱 워터마크
                        Text(
                            text = "✨ Celestial Sanctuary",
                            fontSize = 8.sp,
                            color = Gold.copy(alpha = 0.5f)
                        )
                    }
                }
            }
        }

        // 공유/저장 버튼 (카드가 뒤집힌 후 표시)
        AnimatedVisibility(visible = isFlipped) {
            ActionButtonGroup(
                onShareClick = {
                    val shareText = ShareManager.createTarotShareText(
                        cardName = card.name,
                        cardSymbol = card.symbol,
                        meaning = card.meaning
                    )
                    ShareManager.shareText(context, shareText, "타로카드 운세")
                },
                onSaveClick = {
                    captureController.capture()?.let { bitmap ->
                        ImageCaptureManager.saveBitmapToGallery(context, bitmap, "tarot_${card.name}")
                    }
                }
            )
        }
    }
}

/**
 * 주사위 콘텐츠 - 굴려서 행운 숫자 확인
 */
@Composable
private fun DiceContent(
    result: DiceResult?,
    isRolled: Boolean,
    onRoll: () -> Unit
) {
    var isRolling by remember { mutableStateOf(false) }
    val rotation = remember { Animatable(0f) }
    val coroutineScope = rememberCoroutineScope()

    Column(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        if (!isRolled) {
            Text(
                text = "주사위를 굴려 행운을 시험하세요",
                fontSize = 14.sp,
                color = Gold.copy(alpha = 0.7f)
            )

            Spacer(modifier = Modifier.height(32.dp))

            // 주사위
            Box(
                modifier = Modifier
                    .size(120.dp)
                    .rotate(rotation.value)
                    .shadow(12.dp, RoundedCornerShape(16.dp))
                    .background(
                        brush = Brush.linearGradient(
                            colors = listOf(Gold, GoldDark)
                        ),
                        shape = RoundedCornerShape(16.dp)
                    )
                    .border(2.dp, GoldLight, RoundedCornerShape(16.dp))
                    .clickable(enabled = !isRolling) {
                        isRolling = true
                        coroutineScope.launch {
                            // 굴리기 애니메이션
                            rotation.animateTo(
                                targetValue = rotation.value + 720f + Random.nextFloat() * 360f,
                                animationSpec = tween(1500, easing = FastOutSlowInEasing)
                            )
                            delay(300)
                            onRoll()
                        }
                    },
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = if (isRolling) "?" else "🎲",
                    fontSize = 48.sp,
                    color = DeepNavy
                )
            }

            Spacer(modifier = Modifier.height(24.dp))

            Text(
                text = if (isRolling) "운명이 결정되는 중..." else "탭하여 굴리기",
                fontSize = 14.sp,
                color = Gold.copy(alpha = 0.7f)
            )
        } else {
            // 결과 표시
            DiceResultCard(result = result)
        }
    }
}

@Composable
private fun DiceResultCard(result: DiceResult?) {
    val context = LocalContext.current
    val captureController = rememberCaptureController()

    result?.let {
        Column(
            modifier = Modifier.fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // 캡처 가능한 결과 카드
            CapturableContent(
                controller = captureController,
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp)
                        .background(
                            brush = Brush.verticalGradient(
                                colors = listOf(
                                    NavyLight.copy(alpha = 0.95f),
                                    GoldDark.copy(alpha = 0.5f)
                                )
                            ),
                            shape = RoundedCornerShape(20.dp)
                        )
                        .border(1.dp, Gold.copy(alpha = 0.5f), RoundedCornerShape(20.dp))
                        .padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    // 주사위 숫자들
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        it.numbers.forEach { num ->
                            Box(
                                modifier = Modifier
                                    .size(60.dp)
                                    .shadow(8.dp, RoundedCornerShape(12.dp))
                                    .background(Gold, RoundedCornerShape(12.dp)),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = "$num",
                                    fontSize = 28.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = DeepNavy
                                )
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(24.dp))

                    Text(
                        text = "오늘의 행운 숫자",
                        fontSize = 14.sp,
                        color = Gold.copy(alpha = 0.7f)
                    )

                    Spacer(modifier = Modifier.height(8.dp))

                    Text(
                        text = it.interpretation,
                        fontSize = 16.sp,
                        color = Color.White,
                        textAlign = TextAlign.Center,
                        lineHeight = 24.sp
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    // 행운 레벨
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.Center
                    ) {
                        Text("행운 레벨: ", fontSize = 14.sp, color = Gold.copy(alpha = 0.7f))
                        repeat(it.luckyLevel) {
                            Text("⭐", fontSize = 20.sp)
                        }
                        repeat(5 - it.luckyLevel) {
                            Text("☆", fontSize = 20.sp, color = Gold.copy(alpha = 0.3f))
                        }
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    // 앱 워터마크
                    Text(
                        text = "✨ Celestial Sanctuary ✨",
                        fontSize = 10.sp,
                        color = Gold.copy(alpha = 0.5f)
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // 공유/저장 버튼
            ActionButtonGroup(
                onShareClick = {
                    val shareText = ShareManager.createDiceShareText(
                        numbers = it.numbers,
                        interpretation = it.interpretation,
                        luckyLevel = it.luckyLevel
                    )
                    ShareManager.shareText(context, shareText, "주사위 운세")
                },
                onSaveClick = {
                    captureController.capture()?.let { bitmap ->
                        ImageCaptureManager.saveBitmapToGallery(context, bitmap, "dice")
                    }
                }
            )
        }
    }
}

private data class FortuneTab(val icon: String, val title: String, val isCompleted: Boolean = false)

/**
 * 공유 버튼 컴포저블
 */
@Composable
private fun ShareButton(onClick: () -> Unit) {
    ActionButton(
        icon = "📤",
        text = "공유하기",
        onClick = onClick
    )
}

/**
 * 저장 버튼 컴포저블
 */
@Composable
private fun SaveButton(onClick: () -> Unit) {
    ActionButton(
        icon = "💾",
        text = "저장하기",
        onClick = onClick
    )
}

/**
 * 액션 버튼 베이스 컴포저블
 */
@Composable
private fun ActionButton(
    icon: String,
    text: String,
    onClick: () -> Unit
) {
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(12.dp))
            .background(Gold.copy(alpha = 0.2f))
            .border(1.dp, Gold.copy(alpha = 0.5f), RoundedCornerShape(12.dp))
            .clickable(onClick = onClick)
            .padding(horizontal = 16.dp, vertical = 8.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center
        ) {
            Text(
                text = icon,
                fontSize = 16.sp
            )
            Spacer(modifier = Modifier.width(6.dp))
            Text(
                text = text,
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium,
                color = Gold
            )
        }
    }
}

/**
 * 공유/저장 버튼 그룹
 */
@Composable
private fun ActionButtonGroup(
    onShareClick: () -> Unit,
    onSaveClick: () -> Unit
) {
    Row(
        horizontalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        ShareButton(onClick = onShareClick)
        SaveButton(onClick = onSaveClick)
    }
}
