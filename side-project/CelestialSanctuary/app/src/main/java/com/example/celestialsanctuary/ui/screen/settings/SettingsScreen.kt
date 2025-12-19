package com.example.celestialsanctuary.ui.screen.settings

import android.Manifest
import android.content.Intent
import android.os.Build
import android.provider.Settings
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.VolumeUp
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.Schedule
import androidx.compose.material.icons.filled.Vibration
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TimePicker
import androidx.compose.material3.TimePickerDefaults
import androidx.compose.material3.rememberTimePickerState
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
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.app.NotificationManagerCompat
import androidx.hilt.navigation.compose.hiltViewModel
import com.example.celestialsanctuary.ui.component.StarFieldBackground
import com.example.celestialsanctuary.ui.theme.DeepNavy
import com.example.celestialsanctuary.ui.theme.Gold
import com.example.celestialsanctuary.ui.theme.GoldDark
import com.example.celestialsanctuary.ui.theme.GoldLight
import com.example.celestialsanctuary.ui.theme.NavyLight
import com.example.celestialsanctuary.ui.theme.RoyalPurple

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    onBackClick: () -> Unit,
    viewModel: SettingsViewModel = hiltViewModel()
) {
    val context = LocalContext.current
    val uiState by viewModel.uiState.collectAsState()

    // 시간 선택 다이얼로그 상태
    var showTimePicker by remember { mutableStateOf(false) }

    // 알림 권한 요청 (Android 13+)
    val notificationPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            viewModel.setNotificationsEnabled(true)
        }
    }

    // 시스템 알림 설정 확인
    var systemNotificationsEnabled by remember { mutableStateOf(true) }

    LaunchedEffect(Unit) {
        systemNotificationsEnabled = NotificationManagerCompat.from(context).areNotificationsEnabled()
    }

    StarFieldBackground(
        modifier = Modifier.fillMaxSize(),
        starCount = 40,
        showNebula = true,
        nebulaColor = RoyalPurple.copy(alpha = 0.3f)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp)
        ) {
            // 헤더
            SettingsHeader(onBackClick = onBackClick)

            Spacer(modifier = Modifier.height(24.dp))

            // 설정 항목들
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // 알림 섹션
                SettingsSectionHeader(title = "알림 설정")

                // 시스템 알림이 꺼져있으면 안내
                if (!systemNotificationsEnabled) {
                    SystemNotificationWarning(
                        onClick = {
                            val intent = Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS).apply {
                                putExtra(Settings.EXTRA_APP_PACKAGE, context.packageName)
                            }
                            context.startActivity(intent)
                        }
                    )
                }

                // 알림 활성화 토글
                SettingsToggleItem(
                    icon = Icons.Default.Notifications,
                    title = "일일 운세 알림",
                    description = "매일 정해진 시간에 운세 알림을 받습니다",
                    checked = uiState.notificationsEnabled,
                    onCheckedChange = { enabled ->
                        if (enabled) {
                            // Android 13+ 권한 요청
                            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                                notificationPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
                            } else {
                                viewModel.setNotificationsEnabled(true)
                            }
                        } else {
                            viewModel.setNotificationsEnabled(false)
                        }
                    },
                    enabled = systemNotificationsEnabled
                )

                // 알림 시간 설정
                SettingsClickItem(
                    icon = Icons.Default.Schedule,
                    title = "알림 시간",
                    description = String.format(
                        "%s %d:%02d",
                        if (uiState.notificationHour < 12) "오전" else "오후",
                        if (uiState.notificationHour == 0) 12
                        else if (uiState.notificationHour > 12) uiState.notificationHour - 12
                        else uiState.notificationHour,
                        uiState.notificationMinute
                    ),
                    onClick = { showTimePicker = true },
                    enabled = uiState.notificationsEnabled && systemNotificationsEnabled
                )

                Spacer(modifier = Modifier.height(24.dp))

                // 사운드 & 햅틱 섹션
                SettingsSectionHeader(title = "사운드 & 진동")

                // 사운드 효과 토글
                SettingsToggleItem(
                    icon = Icons.AutoMirrored.Filled.VolumeUp,
                    title = "사운드 효과",
                    description = "운세 확인 시 효과음을 재생합니다",
                    checked = uiState.soundEnabled,
                    onCheckedChange = { viewModel.setSoundEnabled(it) }
                )

                // 햅틱 피드백 토글
                SettingsToggleItem(
                    icon = Icons.Filled.Vibration,
                    title = "진동 피드백",
                    description = "터치 시 진동 피드백을 제공합니다",
                    checked = uiState.hapticEnabled,
                    onCheckedChange = { viewModel.setHapticEnabled(it) }
                )

                Spacer(modifier = Modifier.height(24.dp))

                // 앱 정보 섹션
                SettingsSectionHeader(title = "앱 정보")

                AppInfoCard()
            }
        }
    }

    // 시간 선택 다이얼로그
    if (showTimePicker) {
        TimePickerDialog(
            initialHour = uiState.notificationHour,
            initialMinute = uiState.notificationMinute,
            onDismiss = { showTimePicker = false },
            onConfirm = { hour, minute ->
                viewModel.setNotificationTime(hour, minute)
                showTimePicker = false
            }
        )
    }
}

@Composable
private fun SettingsHeader(onBackClick: () -> Unit) {
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

        Spacer(modifier = Modifier.width(12.dp))

        Text(
            text = "⚙️ 설정",
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold,
            color = Gold
        )
    }
}

@Composable
private fun SettingsSectionHeader(title: String) {
    Text(
        text = title,
        fontSize = 14.sp,
        fontWeight = FontWeight.Bold,
        color = Gold.copy(alpha = 0.8f),
        letterSpacing = 2.sp,
        modifier = Modifier.padding(start = 4.dp, bottom = 8.dp)
    )
}

@Composable
private fun SettingsToggleItem(
    icon: ImageVector,
    title: String,
    description: String,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit,
    enabled: Boolean = true
) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp))
            .background(NavyLight.copy(alpha = if (enabled) 0.6f else 0.3f))
            .border(
                width = 1.dp,
                color = if (enabled) GoldDark.copy(alpha = 0.5f) else Color.Gray.copy(alpha = 0.3f),
                shape = RoundedCornerShape(16.dp)
            )
            .padding(16.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = if (enabled) Gold else Color.Gray,
                modifier = Modifier.size(28.dp)
            )

            Spacer(modifier = Modifier.width(16.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium,
                    color = if (enabled) MaterialTheme.colorScheme.onSurface else Color.Gray
                )
                Text(
                    text = description,
                    fontSize = 12.sp,
                    color = if (enabled) MaterialTheme.colorScheme.onSurfaceVariant else Color.Gray.copy(alpha = 0.7f)
                )
            }

            Switch(
                checked = checked,
                onCheckedChange = onCheckedChange,
                enabled = enabled,
                colors = SwitchDefaults.colors(
                    checkedThumbColor = Gold,
                    checkedTrackColor = GoldDark.copy(alpha = 0.5f),
                    uncheckedThumbColor = Color.Gray,
                    uncheckedTrackColor = NavyLight
                )
            )
        }
    }
}

@Composable
private fun SettingsClickItem(
    icon: ImageVector,
    title: String,
    description: String,
    onClick: () -> Unit,
    enabled: Boolean = true
) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp))
            .background(NavyLight.copy(alpha = if (enabled) 0.6f else 0.3f))
            .border(
                width = 1.dp,
                color = if (enabled) GoldDark.copy(alpha = 0.5f) else Color.Gray.copy(alpha = 0.3f),
                shape = RoundedCornerShape(16.dp)
            )
            .clickable(enabled = enabled, onClick = onClick)
            .padding(16.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = if (enabled) Gold else Color.Gray,
                modifier = Modifier.size(28.dp)
            )

            Spacer(modifier = Modifier.width(16.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium,
                    color = if (enabled) MaterialTheme.colorScheme.onSurface else Color.Gray
                )
                Text(
                    text = description,
                    fontSize = 12.sp,
                    color = if (enabled) Gold else Color.Gray.copy(alpha = 0.7f)
                )
            }

            Text(
                text = "›",
                fontSize = 24.sp,
                color = if (enabled) Gold.copy(alpha = 0.6f) else Color.Gray.copy(alpha = 0.3f)
            )
        }
    }
}

@Composable
private fun SystemNotificationWarning(onClick: () -> Unit) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(Color(0xFFFF6B6B).copy(alpha = 0.2f))
            .border(
                width = 1.dp,
                color = Color(0xFFFF6B6B).copy(alpha = 0.5f),
                shape = RoundedCornerShape(12.dp)
            )
            .clickable(onClick = onClick)
            .padding(12.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "⚠️",
                fontSize = 20.sp
            )

            Spacer(modifier = Modifier.width(12.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = "시스템 알림이 꺼져 있습니다",
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium,
                    color = Color(0xFFFF6B6B)
                )
                Text(
                    text = "탭하여 설정에서 알림을 켜주세요",
                    fontSize = 12.sp,
                    color = Color(0xFFFF6B6B).copy(alpha = 0.8f)
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun TimePickerDialog(
    initialHour: Int,
    initialMinute: Int,
    onDismiss: () -> Unit,
    onConfirm: (Int, Int) -> Unit
) {
    val timePickerState = rememberTimePickerState(
        initialHour = initialHour,
        initialMinute = initialMinute
    )

    AlertDialog(
        onDismissRequest = onDismiss,
        containerColor = DeepNavy,
        title = {
            Text(
                text = "알림 시간 설정",
                color = Gold,
                fontWeight = FontWeight.Bold
            )
        },
        text = {
            Box(
                modifier = Modifier.fillMaxWidth(),
                contentAlignment = Alignment.Center
            ) {
                TimePicker(
                    state = timePickerState,
                    colors = TimePickerDefaults.colors(
                        clockDialColor = NavyLight,
                        clockDialSelectedContentColor = DeepNavy,
                        clockDialUnselectedContentColor = Gold.copy(alpha = 0.7f),
                        selectorColor = Gold,
                        containerColor = DeepNavy,
                        periodSelectorBorderColor = GoldDark,
                        periodSelectorSelectedContainerColor = Gold.copy(alpha = 0.3f),
                        periodSelectorUnselectedContainerColor = NavyLight,
                        periodSelectorSelectedContentColor = Gold,
                        periodSelectorUnselectedContentColor = Gold.copy(alpha = 0.6f),
                        timeSelectorSelectedContainerColor = Gold.copy(alpha = 0.3f),
                        timeSelectorUnselectedContainerColor = NavyLight,
                        timeSelectorSelectedContentColor = Gold,
                        timeSelectorUnselectedContentColor = Gold.copy(alpha = 0.6f)
                    )
                )
            }
        },
        confirmButton = {
            TextButton(
                onClick = { onConfirm(timePickerState.hour, timePickerState.minute) }
            ) {
                Text("확인", color = Gold)
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("취소", color = Gold.copy(alpha = 0.6f))
            }
        }
    )
}

@Composable
private fun AppInfoCard() {
    val infiniteTransition = rememberInfiniteTransition(label = "app_info")
    val shimmerAlpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 0.6f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "shimmer"
    )

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
            .border(
                width = 1.dp,
                brush = Brush.verticalGradient(
                    colors = listOf(
                        Gold.copy(alpha = shimmerAlpha),
                        GoldDark.copy(alpha = 0.3f)
                    )
                ),
                shape = RoundedCornerShape(16.dp)
            )
            .padding(20.dp)
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "🏛️",
                fontSize = 48.sp
            )

            Spacer(modifier = Modifier.height(12.dp))

            Text(
                text = "Celestial Sanctuary",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = Gold,
                letterSpacing = 2.sp
            )

            Text(
                text = "천상의 성소",
                fontSize = 14.sp,
                color = GoldLight.copy(alpha = 0.8f)
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = "버전 1.0.0",
                fontSize = 12.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Spacer(modifier = Modifier.height(16.dp))

            Text(
                text = "당신의 별자리 운세를 탐험하세요\n12개의 하우스가 당신을 기다리고 있습니다",
                fontSize = 12.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
                lineHeight = 18.sp
            )
        }
    }
}
