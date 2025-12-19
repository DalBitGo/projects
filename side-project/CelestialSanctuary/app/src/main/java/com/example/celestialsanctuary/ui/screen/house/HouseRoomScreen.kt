package com.example.celestialsanctuary.ui.screen.house

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowLeft
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.runtime.snapshotFlow
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.scale
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.example.celestialsanctuary.domain.model.House
import com.example.celestialsanctuary.domain.model.HouseDetail
import com.example.celestialsanctuary.domain.model.HouseState
import com.example.celestialsanctuary.domain.model.Planet
import com.example.celestialsanctuary.ui.component.StarFieldBackground
import com.example.celestialsanctuary.ui.theme.DeepNavy
import com.example.celestialsanctuary.ui.theme.EmptyOrb
import com.example.celestialsanctuary.ui.theme.Gold
import com.example.celestialsanctuary.ui.theme.GoldDark
import com.example.celestialsanctuary.ui.theme.NavyLight
import com.example.celestialsanctuary.ui.theme.OwnerGlow
import com.example.celestialsanctuary.ui.theme.RoyalPurple
import com.example.celestialsanctuary.ui.theme.TenantGlow
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HouseRoomScreen(
    houseIndex: Int,
    onBackClick: () -> Unit,
    viewModel: HouseRoomViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val scope = rememberCoroutineScope()

    // Pager state - 초기 페이지는 선택된 하우스 (0-indexed)
    val pagerState = rememberPagerState(
        initialPage = uiState.initialHouseIndex - 1,
        pageCount = { 12 }
    )

    // 페이지 변경 감지
    LaunchedEffect(pagerState) {
        snapshotFlow { pagerState.currentPage }.collect { page ->
            viewModel.onPageChanged(page + 1)  // 1-indexed로 변환
        }
    }

    // 현재 표시할 하우스 정보
    val currentDetail = uiState.houseDetails.getOrNull(pagerState.currentPage)

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    currentDetail?.let { detail ->
                        Text(
                            text = "${getOrdinal(detail.house.index)} HOUSE : ${detail.house.nameEn}",
                            fontWeight = FontWeight.Bold,
                            color = Gold
                        )
                    } ?: Text(
                        text = "${getOrdinal(pagerState.currentPage + 1)} HOUSE",
                        fontWeight = FontWeight.Bold,
                        color = Gold
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onBackClick) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back",
                            tint = Gold
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = DeepNavy
                )
            )
        }
    ) { paddingValues ->
        if (uiState.isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(DeepNavy)
                    .padding(paddingValues),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator(color = Gold)
            }
        } else {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
            ) {
                // Horizontal Pager for swiping between houses
                HorizontalPager(
                    state = pagerState,
                    modifier = Modifier.fillMaxSize()
                ) { page ->
                    val detail = uiState.houseDetails.getOrNull(page)
                    if (detail != null) {
                        HouseRoomContent(
                            detail = detail,
                            modifier = Modifier.fillMaxSize()
                        )
                    } else {
                        // Placeholder while loading
                        Box(
                            modifier = Modifier
                                .fillMaxSize()
                                .background(DeepNavy),
                            contentAlignment = Alignment.Center
                        ) {
                            CircularProgressIndicator(color = Gold)
                        }
                    }
                }

                // Navigation arrows overlay
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .align(Alignment.Center)
                        .padding(horizontal = 8.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    // Left arrow (previous house)
                    IconButton(
                        onClick = {
                            scope.launch {
                                if (pagerState.currentPage > 0) {
                                    pagerState.animateScrollToPage(pagerState.currentPage - 1)
                                }
                            }
                        },
                        modifier = Modifier
                            .size(48.dp)
                            .alpha(if (pagerState.currentPage > 0) 0.8f else 0.3f)
                    ) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.KeyboardArrowLeft,
                            contentDescription = "Previous House",
                            tint = Gold,
                            modifier = Modifier.size(36.dp)
                        )
                    }

                    // Right arrow (next house)
                    IconButton(
                        onClick = {
                            scope.launch {
                                if (pagerState.currentPage < 11) {
                                    pagerState.animateScrollToPage(pagerState.currentPage + 1)
                                }
                            }
                        },
                        modifier = Modifier
                            .size(48.dp)
                            .alpha(if (pagerState.currentPage < 11) 0.8f else 0.3f)
                    ) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.KeyboardArrowRight,
                            contentDescription = "Next House",
                            tint = Gold,
                            modifier = Modifier.size(36.dp)
                        )
                    }
                }

                // Page indicator (bottom)
                PageIndicator(
                    currentPage = pagerState.currentPage,
                    pageCount = 12,
                    modifier = Modifier
                        .align(Alignment.BottomCenter)
                        .padding(bottom = 16.dp)
                )
            }
        }
    }
}

/**
 * 페이지 인디케이터 - 현재 하우스 위치 표시
 */
@Composable
private fun PageIndicator(
    currentPage: Int,
    pageCount: Int,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier,
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically
    ) {
        repeat(pageCount) { index ->
            val isSelected = index == currentPage
            Box(
                modifier = Modifier
                    .padding(horizontal = 3.dp)
                    .size(if (isSelected) 10.dp else 6.dp)
                    .background(
                        color = if (isSelected) Gold else GoldDark.copy(alpha = 0.5f),
                        shape = CircleShape
                    )
            )
        }
    }
}

@Composable
private fun HouseRoomContent(
    detail: HouseDetail,
    modifier: Modifier = Modifier
) {
    // 행성 색상으로 성운 효과
    val nebulaColor = detail.tenantPlanet?.color ?: RoyalPurple

    // 행성 상세 모달 표시 여부
    var showPlanetModal by remember { mutableStateOf(false) }

    StarFieldBackground(
        modifier = modifier.fillMaxSize(),
        starCount = 50,
        showNebula = true,
        nebulaColor = nebulaColor.copy(alpha = 0.5f)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(24.dp)
        ) {
            Spacer(modifier = Modifier.height(32.dp))

            // Crystal Orb with touch ripple + long press
            InteractivePlanetOrb(
                state = detail.state,
                planet = detail.tenantPlanet,
                onLongPress = { showPlanetModal = true },
                modifier = Modifier.size(220.dp)
            )

            // Long press hint
            Text(
                text = "길게 눌러 상세 정보 보기",
                fontSize = 11.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.6f)
            )

            // Status Text
            Text(
                text = getStateDescription(detail),
                fontSize = 14.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(horizontal = 32.dp)
            )

            Spacer(modifier = Modifier.height(16.dp))

            // Interpretation
            InterpretationCard(
                interpretation = detail.interpretation,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp)
            )

            Spacer(modifier = Modifier.height(32.dp))
        }
    }

    // 행성 상세 모달
    if (showPlanetModal) {
        PlanetDetailModal(
            planet = detail.tenantPlanet,
            house = detail.house,
            state = detail.state,
            onDismiss = { showPlanetModal = false }
        )
    }
}

/**
 * 파문 효과 데이터
 */
private data class Ripple(
    val id: Int,
    val progress: Animatable<Float, *>
)

/**
 * 터치 시 파문 효과가 있는 수정구슬
 */
@Composable
private fun InteractivePlanetOrb(
    state: HouseState,
    planet: Planet?,
    onLongPress: () -> Unit,
    modifier: Modifier = Modifier
) {
    val orbColor = when (state) {
        HouseState.EMPTY -> EmptyOrb
        HouseState.TENANT -> planet?.color ?: TenantGlow
        HouseState.OWNER_HOME -> OwnerGlow
    }

    val scope = rememberCoroutineScope()
    val ripples = remember { mutableStateListOf<Ripple>() }
    var rippleId = remember { 0 }

    // Pulsing animation
    val infiniteTransition = rememberInfiniteTransition(label = "orb_pulse")
    val scale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = when (state) {
            HouseState.EMPTY -> 1f
            HouseState.TENANT -> 1.05f
            HouseState.OWNER_HOME -> 1.1f
        },
        animationSpec = infiniteRepeatable(
            animation = tween(1500),
            repeatMode = RepeatMode.Reverse
        ),
        label = "scale"
    )

    // OWNER_HOME 상태일 때 추가 빛 펄스
    val glowPulse by infiniteTransition.animateFloat(
        initialValue = 0.5f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000),
            repeatMode = RepeatMode.Reverse
        ),
        label = "glow_pulse"
    )

    Box(
        modifier = modifier
            .scale(scale)
            .pointerInput(Unit) {
                detectTapGestures(
                    onTap = {
                        // 새 파문 생성
                        val newRipple = Ripple(
                            id = rippleId++,
                            progress = Animatable(0f)
                        )
                        ripples.add(newRipple)

                        scope.launch {
                            newRipple.progress.animateTo(
                                targetValue = 1f,
                                animationSpec = tween(800)
                            )
                            ripples.remove(newRipple)
                        }
                    },
                    onLongPress = {
                        // 길게 누르면 상세 모달 표시
                        onLongPress()
                    }
                )
            },
        contentAlignment = Alignment.Center
    ) {
        // 파문 효과 그리기
        Canvas(modifier = Modifier.fillMaxSize()) {
            val center = Offset(size.width / 2, size.height / 2)
            val maxRadius = size.minDimension / 2

            ripples.forEach { ripple ->
                val progress = ripple.progress.value
                val radius = maxRadius * (0.5f + progress * 0.8f)
                val alpha = (1f - progress) * 0.6f

                // 파문 원
                drawCircle(
                    color = orbColor.copy(alpha = alpha),
                    radius = radius,
                    center = center,
                    style = Stroke(width = 3f * (1f - progress * 0.5f))
                )

                // 내부 빛
                drawCircle(
                    brush = Brush.radialGradient(
                        colors = listOf(
                            orbColor.copy(alpha = alpha * 0.3f),
                            Color.Transparent
                        ),
                        center = center,
                        radius = radius
                    ),
                    center = center,
                    radius = radius
                )
            }
        }

        // 메인 구슬
        Box(
            modifier = Modifier
                .fillMaxSize(0.7f)
                .shadow(
                    elevation = when (state) {
                        HouseState.EMPTY -> 8.dp
                        HouseState.TENANT -> 24.dp
                        HouseState.OWNER_HOME -> (40 + glowPulse * 20).dp
                    },
                    shape = CircleShape,
                    ambientColor = orbColor,
                    spotColor = if (state == HouseState.OWNER_HOME) Gold else orbColor
                )
                .background(
                    brush = Brush.radialGradient(
                        colors = listOf(
                            if (state == HouseState.OWNER_HOME) Color.White.copy(alpha = 0.3f)
                            else orbColor.copy(alpha = 0.9f),
                            orbColor.copy(alpha = 0.6f),
                            orbColor.copy(alpha = 0.3f),
                            Color.Transparent
                        )
                    ),
                    shape = CircleShape
                ),
            contentAlignment = Alignment.Center
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Planet symbol
                Text(
                    text = planet?.symbol ?: when (state) {
                        HouseState.EMPTY -> "○"
                        else -> "✦"
                    },
                    fontSize = if (planet != null) 48.sp else 40.sp,
                    fontWeight = FontWeight.Bold,
                    color = if (state == HouseState.OWNER_HOME) Gold else Color.White
                )

                // Planet name
                planet?.let {
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = it.displayName,
                        fontSize = 12.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}

@Composable
private fun PlanetOrb(
    state: HouseState,
    planet: Planet?,
    modifier: Modifier = Modifier
) {
    val orbColor = when (state) {
        HouseState.EMPTY -> EmptyOrb
        HouseState.TENANT -> planet?.color ?: TenantGlow
        HouseState.OWNER_HOME -> OwnerGlow
    }

    // Pulsing animation for non-empty states
    val infiniteTransition = rememberInfiniteTransition(label = "orb_pulse")
    val scale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = when (state) {
            HouseState.EMPTY -> 1f
            HouseState.TENANT -> 1.05f
            HouseState.OWNER_HOME -> 1.1f
        },
        animationSpec = infiniteRepeatable(
            animation = tween(1500),
            repeatMode = RepeatMode.Reverse
        ),
        label = "scale"
    )

    Box(
        modifier = modifier
            .scale(scale)
            .shadow(
                elevation = when (state) {
                    HouseState.EMPTY -> 8.dp
                    HouseState.TENANT -> 20.dp
                    HouseState.OWNER_HOME -> 40.dp
                },
                shape = CircleShape,
                ambientColor = orbColor,
                spotColor = orbColor
            )
            .background(
                brush = Brush.radialGradient(
                    colors = listOf(
                        orbColor.copy(alpha = 0.9f),
                        orbColor.copy(alpha = 0.5f),
                        orbColor.copy(alpha = 0.2f),
                        Color.Transparent
                    )
                ),
                shape = CircleShape
            ),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Planet symbol
            Text(
                text = planet?.symbol ?: when (state) {
                    HouseState.EMPTY -> "○"
                    else -> "✦"
                },
                fontSize = if (planet != null) 56.sp else 48.sp,
                color = if (state == HouseState.OWNER_HOME) Gold else orbColor.copy(alpha = 0.9f)
            )

            // Planet name for non-empty states
            planet?.let {
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = it.displayName,
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun InterpretationCard(
    interpretation: String,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .background(
                color = NavyLight.copy(alpha = 0.7f),
                shape = RoundedCornerShape(16.dp)
            )
            .padding(20.dp)
    ) {
        Text(
            text = "해석",
            fontSize = 18.sp,
            fontWeight = FontWeight.Bold,
            color = Gold
        )

        Spacer(modifier = Modifier.height(12.dp))

        Text(
            text = interpretation,
            fontSize = 14.sp,
            color = MaterialTheme.colorScheme.onSurface,
            lineHeight = 22.sp
        )
    }
}

private fun getOrdinal(n: Int): String {
    return when (n) {
        1 -> "1st"
        2 -> "2nd"
        3 -> "3rd"
        else -> "${n}th"
    }
}

private fun getStateDescription(detail: HouseDetail): String {
    return when (detail.state) {
        HouseState.EMPTY -> "이 하우스에는 현재 행성이 없습니다."
        HouseState.TENANT -> "손님 행성 ${detail.tenantPlanet?.displayName ?: ""}이(가) 이 하우스에 머물고 있습니다."
        HouseState.OWNER_HOME -> "🌟 집주인 ${detail.house.ownerPlanet.displayName}이(가) 자신의 집에 있습니다!\n강력한 시너지 상태입니다."
    }
}

/**
 * 행성 상세 정보 모달
 */
@Composable
private fun PlanetDetailModal(
    planet: Planet?,
    house: House,
    state: HouseState,
    onDismiss: () -> Unit
) {
    // 빛나는 효과
    val infiniteTransition = rememberInfiniteTransition(label = "modal_glow")
    val glowAlpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 0.6f,
        animationSpec = infiniteRepeatable(
            animation = tween(1500),
            repeatMode = RepeatMode.Reverse
        ),
        label = "glow_alpha"
    )

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(DeepNavy.copy(alpha = 0.9f))
            .pointerInput(Unit) {
                detectTapGestures(onTap = { onDismiss() })
            },
        contentAlignment = Alignment.Center
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth(0.85f)
                .background(
                    brush = Brush.verticalGradient(
                        colors = listOf(
                            NavyLight,
                            NavyLight.copy(alpha = 0.95f),
                            DeepNavy
                        )
                    ),
                    shape = RoundedCornerShape(24.dp)
                )
                .border(
                    width = 2.dp,
                    brush = Brush.verticalGradient(
                        colors = listOf(
                            Gold.copy(alpha = glowAlpha),
                            Gold.copy(alpha = 0.2f)
                        )
                    ),
                    shape = RoundedCornerShape(24.dp)
                )
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // 닫기 힌트
            Text(
                text = "탭하여 닫기",
                fontSize = 10.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f),
                modifier = Modifier.align(Alignment.End)
            )

            Spacer(modifier = Modifier.height(8.dp))

            // 행성 심볼 (크게)
            val symbolColor = planet?.color ?: when (state) {
                HouseState.EMPTY -> EmptyOrb
                HouseState.OWNER_HOME -> OwnerGlow
                else -> TenantGlow
            }

            Box(
                modifier = Modifier
                    .size(100.dp)
                    .shadow(20.dp, CircleShape, ambientColor = symbolColor, spotColor = symbolColor)
                    .background(
                        brush = Brush.radialGradient(
                            colors = listOf(
                                symbolColor.copy(alpha = 0.8f),
                                symbolColor.copy(alpha = 0.3f),
                                Color.Transparent
                            )
                        ),
                        shape = CircleShape
                    ),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = planet?.symbol ?: "○",
                    fontSize = 56.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            // 행성 이름 (한글/영어)
            if (planet != null) {
                Text(
                    text = planet.displayName,
                    fontSize = 28.sp,
                    fontWeight = FontWeight.Bold,
                    color = Gold
                )

                Text(
                    text = planet.name,
                    fontSize = 14.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            } else {
                Text(
                    text = when (state) {
                        HouseState.EMPTY -> "빈 하우스"
                        else -> house.ownerPlanet.displayName
                    },
                    fontSize = 28.sp,
                    fontWeight = FontWeight.Bold,
                    color = Gold
                )
            }

            Spacer(modifier = Modifier.height(20.dp))

            // 상태 배지
            Box(
                modifier = Modifier
                    .background(
                        color = when (state) {
                            HouseState.EMPTY -> EmptyOrb.copy(alpha = 0.3f)
                            HouseState.TENANT -> TenantGlow.copy(alpha = 0.3f)
                            HouseState.OWNER_HOME -> OwnerGlow.copy(alpha = 0.3f)
                        },
                        shape = RoundedCornerShape(12.dp)
                    )
                    .padding(horizontal = 16.dp, vertical = 8.dp)
            ) {
                Text(
                    text = when (state) {
                        HouseState.EMPTY -> "빈 방"
                        HouseState.TENANT -> "손님 행성"
                        HouseState.OWNER_HOME -> "✨ 집주인 귀환"
                    },
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                    color = when (state) {
                        HouseState.EMPTY -> EmptyOrb
                        HouseState.TENANT -> TenantGlow
                        HouseState.OWNER_HOME -> Gold
                    }
                )
            }

            Spacer(modifier = Modifier.height(20.dp))

            // 행성 설명
            Text(
                text = getPlanetDescription(planet, house, state),
                fontSize = 14.sp,
                color = MaterialTheme.colorScheme.onSurface,
                textAlign = TextAlign.Center,
                lineHeight = 22.sp
            )

            Spacer(modifier = Modifier.height(16.dp))

            // 하우스 정보
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(
                        color = DeepNavy.copy(alpha = 0.5f),
                        shape = RoundedCornerShape(12.dp)
                    )
                    .padding(12.dp),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = "하우스",
                        fontSize = 10.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = "${house.index}",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = Gold
                    )
                }
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = "주인 행성",
                        fontSize = 10.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = house.ownerPlanet.symbol,
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = house.ownerPlanet.color
                    )
                }
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = "영역",
                        fontSize = 10.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = house.nameKo,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold,
                        color = Gold
                    )
                }
            }
        }
    }
}

/**
 * 행성 설명 텍스트 생성
 */
private fun getPlanetDescription(planet: Planet?, house: House, state: HouseState): String {
    if (planet == null) {
        return when (state) {
            HouseState.EMPTY -> "이 하우스에는 현재 어떤 행성도 머물지 않습니다.\n" +
                    "주인 행성 ${house.ownerPlanet.displayName}의 위치가 이 영역에 영향을 줍니다."
            else -> "집주인 ${house.ownerPlanet.displayName}이(가) 자신의 성소에 있습니다."
        }
    }

    val baseDesc = when (planet) {
        Planet.SUN -> "태양은 자아, 정체성, 생명력을 나타냅니다. 당신의 핵심적인 존재와 창조적 에너지의 원천입니다."
        Planet.MOON -> "달은 감정, 본능, 무의식을 상징합니다. 내면의 감정 세계와 안정감의 필요를 반영합니다."
        Planet.MERCURY -> "수성은 소통, 지성, 학습을 나타냅니다. 생각하고 표현하는 방식을 결정합니다."
        Planet.VENUS -> "금성은 사랑, 아름다움, 가치관을 상징합니다. 관계와 조화를 추구하는 방식을 보여줍니다."
        Planet.MARS -> "화성은 행동, 에너지, 욕망을 나타냅니다. 목표를 향해 나아가는 추진력을 상징합니다."
        Planet.JUPITER -> "목성은 확장, 행운, 철학을 상징합니다. 성장과 풍요를 가져오는 영역을 나타냅니다."
        Planet.SATURN -> "토성은 구조, 제한, 책임을 나타냅니다. 노력과 인내를 통해 성취하는 영역입니다."
        Planet.URANUS -> "천왕성은 혁신, 자유, 독창성을 상징합니다. 변화와 각성의 에너지를 가져옵니다."
        Planet.NEPTUNE -> "해왕성은 꿈, 영성, 상상력을 나타냅니다. 초월적 경험과 직관의 영역입니다."
        Planet.PLUTO -> "명왕성은 변형, 재생, 심층 심리를 상징합니다. 깊은 변화와 치유의 힘을 가집니다."
    }

    return baseDesc + "\n\n" + when (state) {
        HouseState.TENANT -> "이 행성이 ${house.nameKo}의 영역에서 손님으로 머물고 있습니다."
        HouseState.OWNER_HOME -> "자신의 집에서 가장 강력한 힘을 발휘합니다!"
        else -> ""
    }
}
