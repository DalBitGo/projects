package com.example.celestialsanctuary.ui.screen.opening

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.size
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
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.scale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.example.celestialsanctuary.ui.component.StarFieldBackground
import com.example.celestialsanctuary.ui.component.GlowingSymbol
import com.example.celestialsanctuary.ui.theme.Gold
import kotlinx.coroutines.delay

@Composable
fun OpeningScreen(
    onNavigateToHall: () -> Unit,
    onNavigateToOnboarding: () -> Unit,
    viewModel: OpeningViewModel = hiltViewModel()
) {
    val destination by viewModel.destination.collectAsState()

    var startAnimation by remember { mutableStateOf(false) }
    val alpha by animateFloatAsState(
        targetValue = if (startAnimation) 1f else 0f,
        animationSpec = tween(durationMillis = 2000),
        label = "alpha"
    )

    val scale by animateFloatAsState(
        targetValue = if (startAnimation) 1f else 0.5f,
        animationSpec = tween(durationMillis = 2500),
        label = "scale"
    )

    LaunchedEffect(Unit) {
        startAnimation = true
        delay(3000)
        viewModel.checkOnboardingStatus()
    }

    LaunchedEffect(destination) {
        when (destination) {
            OpeningDestination.Hall -> onNavigateToHall()
            OpeningDestination.Onboarding -> onNavigateToOnboarding()
            OpeningDestination.Loading -> { /* 대기 */ }
        }
    }

    StarFieldBackground(
        modifier = Modifier.fillMaxSize(),
        starCount = 100,
        showNebula = true
    ) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = Modifier
                    .alpha(alpha)
                    .scale(scale)
            ) {
                // 빛나는 심볼
                GlowingSymbol(
                    symbol = "✦",
                    modifier = Modifier.size(120.dp)
                )

                Spacer(modifier = Modifier.height(32.dp))

                Text(
                    text = "CELESTIAL SANCTUARY",
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold,
                    color = Gold,
                    letterSpacing = 4.sp
                )

                Spacer(modifier = Modifier.height(8.dp))

                Text(
                    text = "천궁의 성소",
                    fontSize = 16.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}
