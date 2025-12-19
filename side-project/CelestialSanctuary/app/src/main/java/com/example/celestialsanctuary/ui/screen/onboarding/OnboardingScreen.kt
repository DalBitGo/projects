package com.example.celestialsanctuary.ui.screen.onboarding

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInHorizontally
import androidx.compose.animation.slideOutHorizontally
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.background
import androidx.compose.foundation.border
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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.OffsetMapping
import androidx.compose.ui.text.input.TransformedText
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.example.celestialsanctuary.ui.component.StarFieldBackground
import com.example.celestialsanctuary.ui.theme.DeepNavy
import com.example.celestialsanctuary.ui.theme.Gold
import com.example.celestialsanctuary.ui.theme.GoldDark
import com.example.celestialsanctuary.ui.theme.GoldLight
import com.example.celestialsanctuary.ui.theme.MarsColor
import com.example.celestialsanctuary.ui.theme.NavyLight
import com.example.celestialsanctuary.ui.theme.RoyalPurple
import com.example.celestialsanctuary.ui.theme.TextPrimary

// 생년월일 포맷: 19921202 -> 1992-12-02
class DateVisualTransformation : VisualTransformation {
    override fun filter(text: AnnotatedString): TransformedText {
        val trimmed = text.text.take(8)
        var output = ""

        for (i in trimmed.indices) {
            output += trimmed[i]
            if (i == 3 || i == 5) output += "-"
        }

        val offsetMapping = object : OffsetMapping {
            override fun originalToTransformed(offset: Int): Int {
                return when {
                    offset <= 4 -> offset
                    offset <= 6 -> offset + 1
                    offset <= 8 -> offset + 2
                    else -> 10
                }
            }

            override fun transformedToOriginal(offset: Int): Int {
                return when {
                    offset <= 4 -> offset
                    offset <= 7 -> offset - 1
                    offset <= 10 -> offset - 2
                    else -> 8
                }
            }
        }

        return TransformedText(AnnotatedString(output), offsetMapping)
    }
}

// 시간 포맷: 1430 -> 14:30
class TimeVisualTransformation : VisualTransformation {
    override fun filter(text: AnnotatedString): TransformedText {
        val trimmed = text.text.take(4)
        var output = ""

        for (i in trimmed.indices) {
            output += trimmed[i]
            if (i == 1) output += ":"
        }

        val offsetMapping = object : OffsetMapping {
            override fun originalToTransformed(offset: Int): Int {
                return when {
                    offset <= 2 -> offset
                    offset <= 4 -> offset + 1
                    else -> 5
                }
            }

            override fun transformedToOriginal(offset: Int): Int {
                return when {
                    offset <= 2 -> offset
                    offset <= 5 -> offset - 1
                    else -> 4
                }
            }
        }

        return TransformedText(AnnotatedString(output), offsetMapping)
    }
}

@Composable
fun OnboardingScreen(
    onComplete: () -> Unit,
    viewModel: OnboardingViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var currentStep by remember { mutableIntStateOf(0) }

    LaunchedEffect(Unit) {
        viewModel.events.collect { event ->
            when (event) {
                OnboardingEvent.NavigateToHall -> onComplete()
            }
        }
    }

    StarFieldBackground(
        modifier = Modifier.fillMaxSize(),
        starCount = 80,
        showNebula = true,
        nebulaColor = RoyalPurple
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Spacer(modifier = Modifier.height(48.dp))

            // 타이틀
            Text(
                text = "✧ 별의 주문 ✧",
                fontSize = 28.sp,
                fontWeight = FontWeight.Bold,
                color = Gold
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = "당신의 탄생 순간을 기록하세요",
                fontSize = 14.sp,
                color = Color.White.copy(alpha = 0.7f)
            )

            Spacer(modifier = Modifier.height(32.dp))

            // 진행 표시기
            StepIndicator(
                currentStep = currentStep,
                totalSteps = 4
            )

            Spacer(modifier = Modifier.height(40.dp))

            // 단계별 컨텐츠
            Box(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth(),
                contentAlignment = Alignment.Center
            ) {
                AnimatedContent(
                    targetState = currentStep,
                    transitionSpec = {
                        if (targetState > initialState) {
                            slideInHorizontally { it } + fadeIn() togetherWith
                                    slideOutHorizontally { -it } + fadeOut()
                        } else {
                            slideInHorizontally { -it } + fadeIn() togetherWith
                                    slideOutHorizontally { it } + fadeOut()
                        }
                    },
                    label = "step_content"
                ) { step ->
                    when (step) {
                        0 -> UserNameStep(
                            value = uiState.userName,
                            onValueChange = { viewModel.updateUserName(it) }
                        )
                        1 -> BirthDateStep(
                            value = uiState.birthDate,
                            onValueChange = { viewModel.updateBirthDate(it) }
                        )
                        2 -> BirthTimeStep(
                            value = uiState.birthTime,
                            onValueChange = { viewModel.updateBirthTime(it) }
                        )
                        3 -> BirthLocationStep(
                            value = uiState.birthLocation,
                            onValueChange = { viewModel.updateBirthLocation(it) },
                            isLoading = uiState.isLoading
                        )
                    }
                }
            }

            // 에러 메시지
            AnimatedVisibility(visible = uiState.errorMessage != null) {
                uiState.errorMessage?.let { error ->
                    Text(
                        text = error,
                        color = MarsColor,
                        fontSize = 14.sp,
                        modifier = Modifier.padding(vertical = 8.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            // 네비게이션 버튼
            NavigationButtons(
                currentStep = currentStep,
                isLastStep = currentStep == 3,
                isLoading = uiState.isLoading,
                canProceed = when (currentStep) {
                    0 -> true  // 이름은 선택사항
                    1 -> uiState.birthDate.length == 8
                    2 -> uiState.birthTime.length == 4
                    3 -> uiState.birthLocation.isNotBlank()
                    else -> false
                },
                onBack = { currentStep-- },
                onNext = {
                    if (currentStep < 3) {
                        currentStep++
                    } else {
                        viewModel.saveProfile()
                    }
                }
            )

            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}

/**
 * 단계 표시기
 */
@Composable
private fun StepIndicator(
    currentStep: Int,
    totalSteps: Int
) {
    Row(
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically
    ) {
        repeat(totalSteps) { step ->
            val isActive = step <= currentStep
            val isCurrent = step == currentStep

            val size by animateFloatAsState(
                targetValue = if (isCurrent) 14f else 10f,
                animationSpec = tween(300),
                label = "step_size"
            )

            Box(
                modifier = Modifier
                    .size(size.dp)
                    .shadow(
                        elevation = if (isActive) 8.dp else 0.dp,
                        shape = CircleShape,
                        ambientColor = Gold,
                        spotColor = Gold
                    )
                    .background(
                        brush = if (isActive) {
                            Brush.radialGradient(
                                colors = listOf(GoldLight, Gold)
                            )
                        } else {
                            Brush.radialGradient(
                                colors = listOf(NavyLight, NavyLight)
                            )
                        },
                        shape = CircleShape
                    )
                    .border(
                        width = 1.dp,
                        color = if (isActive) Gold else GoldDark,
                        shape = CircleShape
                    )
            )

            if (step < totalSteps - 1) {
                Box(
                    modifier = Modifier
                        .width(40.dp)
                        .height(2.dp)
                        .background(
                            color = if (step < currentStep) Gold else NavyLight
                        )
                )
            }
        }
    }
}

/**
 * 이름 입력 단계
 */
@Composable
private fun UserNameStep(
    value: String,
    onValueChange: (String) -> Unit
) {
    StepCard(
        symbol = "✧",
        title = "당신의 이름",
        subtitle = "별들이 당신을 어떻게 부를까요?"
    ) {
        MagicTextField(
            value = value,
            onValueChange = { newValue ->
                onValueChange(newValue.take(20))
            },
            label = "이름 (선택)",
            placeholder = "예: Luna",
            visualTransformation = VisualTransformation.None,
            keyboardType = KeyboardType.Text
        )

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = "건너뛰어도 괜찮아요",
            fontSize = 12.sp,
            color = Color.White.copy(alpha = 0.5f),
            textAlign = TextAlign.Center,
            modifier = Modifier.fillMaxWidth()
        )
    }
}

/**
 * 생년월일 입력 단계
 */
@Composable
private fun BirthDateStep(
    value: String,
    onValueChange: (String) -> Unit
) {
    StepCard(
        symbol = "☉",
        title = "탄생의 날",
        subtitle = "당신이 이 세상에 온 날을 알려주세요"
    ) {
        MagicTextField(
            value = value,
            onValueChange = { newValue ->
                val filtered = newValue.filter { it.isDigit() }.take(8)
                onValueChange(filtered)
            },
            label = "생년월일",
            placeholder = "예: 19901215",
            visualTransformation = DateVisualTransformation(),
            keyboardType = KeyboardType.Number
        )
    }
}

/**
 * 출생 시간 입력 단계
 */
@Composable
private fun BirthTimeStep(
    value: String,
    onValueChange: (String) -> Unit
) {
    StepCard(
        symbol = "☽",
        title = "탄생의 시간",
        subtitle = "별들이 어디에 있었는지 알려주세요"
    ) {
        MagicTextField(
            value = value,
            onValueChange = { newValue ->
                val filtered = newValue.filter { it.isDigit() }.take(4)
                onValueChange(filtered)
            },
            label = "출생 시간 (24시간)",
            placeholder = "예: 1430",
            visualTransformation = TimeVisualTransformation(),
            keyboardType = KeyboardType.Number
        )
    }
}

/**
 * 출생 장소 입력 단계
 */
@Composable
private fun BirthLocationStep(
    value: String,
    onValueChange: (String) -> Unit,
    isLoading: Boolean
) {
    StepCard(
        symbol = "⊕",
        title = "탄생의 장소",
        subtitle = "지구 어디에서 태어났나요?"
    ) {
        MagicTextField(
            value = value,
            onValueChange = onValueChange,
            label = "출생 장소",
            placeholder = "예: 서울",
            visualTransformation = VisualTransformation.None,
            keyboardType = KeyboardType.Text
        )

        if (isLoading) {
            Spacer(modifier = Modifier.height(16.dp))
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center,
                modifier = Modifier.fillMaxWidth()
            ) {
                CircularProgressIndicator(
                    color = Gold,
                    modifier = Modifier.size(20.dp),
                    strokeWidth = 2.dp
                )
                Spacer(modifier = Modifier.width(12.dp))
                Text(
                    text = "별자리 지도를 그리는 중...",
                    fontSize = 14.sp,
                    color = Gold
                )
            }
        }
    }
}

/**
 * 단계 카드 컨테이너
 */
@Composable
private fun StepCard(
    symbol: String,
    title: String,
    subtitle: String,
    content: @Composable () -> Unit
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier.fillMaxWidth()
    ) {
        // 심볼
        Box(
            modifier = Modifier
                .size(80.dp)
                .shadow(16.dp, CircleShape, ambientColor = Gold, spotColor = Gold)
                .background(
                    brush = Brush.radialGradient(
                        colors = listOf(
                            Gold.copy(alpha = 0.3f),
                            DeepNavy
                        )
                    ),
                    shape = CircleShape
                )
                .border(2.dp, Gold, CircleShape),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = symbol,
                fontSize = 36.sp,
                color = Gold
            )
        }

        Spacer(modifier = Modifier.height(24.dp))

        Text(
            text = title,
            fontSize = 22.sp,
            fontWeight = FontWeight.Bold,
            color = Gold
        )

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = subtitle,
            fontSize = 14.sp,
            color = Color.White.copy(alpha = 0.6f),
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(32.dp))

        // 입력 필드
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(16.dp))
                .background(NavyLight.copy(alpha = 0.5f))
                .border(
                    width = 1.dp,
                    brush = Brush.verticalGradient(
                        colors = listOf(Gold.copy(alpha = 0.5f), Gold.copy(alpha = 0.2f))
                    ),
                    shape = RoundedCornerShape(16.dp)
                )
                .padding(20.dp)
        ) {
            Column {
                content()
            }
        }
    }
}

/**
 * 마법 느낌의 텍스트 필드
 */
@Composable
private fun MagicTextField(
    value: String,
    onValueChange: (String) -> Unit,
    label: String,
    placeholder: String,
    visualTransformation: VisualTransformation,
    keyboardType: KeyboardType
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        label = { Text(label) },
        placeholder = { Text(placeholder, color = Color.White.copy(alpha = 0.3f)) },
        modifier = Modifier.fillMaxWidth(),
        visualTransformation = visualTransformation,
        keyboardOptions = KeyboardOptions(keyboardType = keyboardType),
        colors = OutlinedTextFieldDefaults.colors(
            focusedBorderColor = Gold,
            unfocusedBorderColor = GoldDark.copy(alpha = 0.5f),
            focusedLabelColor = Gold,
            unfocusedLabelColor = Gold.copy(alpha = 0.7f),
            cursorColor = Gold,
            focusedTextColor = TextPrimary,
            unfocusedTextColor = TextPrimary,
            focusedContainerColor = Color.Transparent,
            unfocusedContainerColor = Color.Transparent
        ),
        singleLine = true,
        shape = RoundedCornerShape(12.dp)
    )
}

/**
 * 네비게이션 버튼
 */
@Composable
private fun NavigationButtons(
    currentStep: Int,
    isLastStep: Boolean,
    isLoading: Boolean,
    canProceed: Boolean,
    onBack: () -> Unit,
    onNext: () -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        // 뒤로 버튼
        if (currentStep > 0) {
            TextButton(
                onClick = onBack,
                enabled = !isLoading
            ) {
                Text(
                    text = "← 이전",
                    color = Gold.copy(alpha = 0.8f),
                    fontSize = 16.sp
                )
            }
        } else {
            Spacer(modifier = Modifier.width(80.dp))
        }

        // 다음/완료 버튼
        Button(
            onClick = onNext,
            enabled = canProceed && !isLoading,
            colors = ButtonDefaults.buttonColors(
                containerColor = Gold,
                contentColor = DeepNavy,
                disabledContainerColor = GoldDark.copy(alpha = 0.3f),
                disabledContentColor = Color.White.copy(alpha = 0.5f)
            ),
            shape = RoundedCornerShape(12.dp),
            modifier = Modifier
                .shadow(
                    elevation = if (canProceed) 8.dp else 0.dp,
                    shape = RoundedCornerShape(12.dp),
                    ambientColor = Gold,
                    spotColor = Gold
                )
        ) {
            Text(
                text = if (isLastStep) "성소에 입장 ✦" else "다음 →",
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp)
            )
        }
    }
}
