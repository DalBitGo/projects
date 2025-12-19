# Celestial Sanctuary - 개발 변경 이력

## 개요
점성술 기반 Android 앱 "Celestial Sanctuary"의 개발 진행 상황을 기록합니다.

---

## [M9] 출시 준비 고도화 ✅

### 목표
v1.0 출시를 위한 사용자 경험 강화 및 필수 기능 구현

---

### M9.1 푸시 알림 시스템 ✅

**새 파일들:**
```
notification/
├── NotificationHelper.kt      # 알림 생성/표시
├── DailyReminderReceiver.kt   # BroadcastReceiver
├── DailyReminderScheduler.kt  # AlarmManager 스케줄링
├── BootReceiver.kt            # 재부팅 후 알림 복원
└── NotificationPreferences.kt # DataStore 설정 저장
```

**주요 구현:**
```kotlin
// 로컬 푸시 알림 (Firebase 미사용)
class DailyReminderScheduler(context: Context) {
    fun scheduleDailyReminder(hour: Int, minute: Int)
    fun cancelDailyReminder()
}

// 알림 메시지
"오늘의 운세가 준비되었습니다 ✨"
```

**AndroidManifest.xml 추가:**
- `RECEIVE_BOOT_COMPLETED` 권한
- `POST_NOTIFICATIONS` 권한 (Android 13+)
- `BootReceiver` 등록
- `DailyReminderReceiver` 등록

---

### M9.2 일일 리셋 시스템 ✅

**새 파일:** `data/FortuneDataStore.kt`

```kotlin
class FortuneRepository(context: Context) {
    // 날짜 기반 자동 리셋
    val isNewDay: Flow<Boolean>
    val streakDays: Flow<Int>  // 연속 접속일

    // 운세별 상태 저장
    val crystalBallRevealed: Flow<Boolean>
    val tarotRevealed: Flow<Boolean>
    val diceRolled: Flow<Boolean>

    // 결과 데이터 저장
    val savedCrystalBallResult: Flow<CrystalBallData?>
    val savedTarotResult: Flow<TarotData?>
    val savedDiceResult: Flow<DiceData?>

    suspend fun updateDailyAccess()
    suspend fun saveCrystalBallResult(...)
    suspend fun saveTarotResult(...)
    suspend fun saveDiceResult(...)
}
```

**DailyFortuneScreen 변경:**
- 연속 접속일 표시: "🔥 3일 연속 접속!"
- 탭별 완료 체크마크 표시: ✅
- 결과 유지 (앱 종료 후에도)

---

### M9.3 설정 화면 ✅

**새 파일들:**
```
ui/screen/settings/
├── SettingsScreen.kt
└── SettingsViewModel.kt
```

**설정 항목:**
| 항목 | 타입 | 설명 |
|------|------|------|
| 알림 활성화 | 토글 | 일일 알림 ON/OFF |
| 알림 시간 | 시간 선택 | 기본 오전 9시 |
| 사운드 효과 | 토글 | (추후 확장용) |
| 햅틱 피드백 | 토글 | 진동 ON/OFF |

**UI 컴포넌트:**
```kotlin
@Composable
fun SettingsScreen(
    onBackClick: () -> Unit,
    viewModel: SettingsViewModel = hiltViewModel()
)

@Composable
private fun SettingItem(title, subtitle, trailing)
```

**Android 13+ 알림 권한 처리:**
```kotlin
val notificationPermission = rememberLauncherForActivityResult(
    ActivityResultContracts.RequestPermission()
) { granted -> ... }
```

---

### M9.4 주간 운세 화면 ✅

**새 파일들:**
```
ui/screen/weekly/
├── WeeklyFortuneScreen.kt
└── WeeklyFortuneViewModel.kt
```

**주간 운세 데이터:**
```kotlin
data class DayFortune(
    val dayOfWeek: String,      // "월", "화", ...
    val dayOfMonth: Int,
    val fullDate: String,
    val fortuneLevel: Int,      // 1-5
    val generalFortune: String,
    val loveFortune: String,
    val moneyFortune: String,
    val healthFortune: String,
    val advice: String,
    val luckyColor: String,
    val luckyNumber: Int,
    val luckyDirection: String
)
```

**UI 구성:**
- 7일 선택기 (오늘 강조)
- 운세 레벨 별점 표시
- 카테고리별 운세 (종합/애정/금전/건강)
- 조언 및 행운 아이템

**HouseHallScreen 변경:**
- `WeeklyFortuneBanner` 추가
- 일일/주간 배너 나란히 표시 (Row)

---

### M9.5 햅틱 피드백 시스템 ✅

**새 파일:** `util/SoundManager.kt`

```kotlin
class SoundManager(context: Context) {
    private var hapticEnabled: Boolean = true

    fun hapticTap()       // 가벼운 탭
    fun hapticSuccess()   // 성공 피드백
    fun hapticDiceRoll()  // 주사위 굴리기
    fun hapticShake()     // 흔들기
    fun hapticCardFlip()  // 카드 뒤집기

    fun setHapticEnabled(enabled: Boolean)
}
```

**DailyFortuneViewModel 적용:**
```kotlin
fun onCrystalBallShake() { soundManager.hapticShake() }
fun revealCrystalBall() { soundManager.hapticSuccess() }
fun selectTarotCard(index: Int) { soundManager.hapticCardFlip() }
fun rollDice() { soundManager.hapticDiceRoll() }
```

---

### M9.6 공유 기능 ✅

**새 파일:** `util/ShareManager.kt`

```kotlin
object ShareManager {
    fun shareText(context: Context, text: String, title: String)

    fun createCrystalBallShareText(
        message: String,
        luckyNumbers: List<Int>,
        luckyColor: String,
        luckyDirection: String
    ): String

    fun createTarotShareText(
        cardName: String,
        cardSymbol: String,
        meaning: String
    ): String

    fun createDiceShareText(
        numbers: List<Int>,
        interpretation: String,
        luckyLevel: Int
    ): String

    fun createWeeklyFortuneShareText(...): String
}
```

**공유 텍스트 예시:**
```
🔮 오늘의 수정구슬 운세 🔮
📅 2024년 12월 13일

✨ 메시지:
"오늘은 당신의 직감이 특별히 날카로운 날입니다..."

🔢 행운 숫자: 7, 23, 41
🎨 행운 색상: 금색
🧭 행운 방향: 동쪽

━━━━━━━━━━━
📲 Celestial Sanctuary
#수정구슬운세 #오늘의운세
```

**DailyFortuneScreen 변경:**
- 각 결과 카드에 "📤 공유하기" 버튼 추가
- Intent.ACTION_SEND로 공유

---

### 네비게이션 변경

**Screen.kt 추가:**
```kotlin
sealed class Screen(val route: String) {
    ...
    data object WeeklyFortune : Screen("weekly_fortune")
    data object Settings : Screen("settings")
}
```

**NavGraph.kt 추가:**
```kotlin
composable(Screen.WeeklyFortune.route) {
    WeeklyFortuneScreen(onBackClick = { navController.popBackStack() })
}
composable(Screen.Settings.route) {
    SettingsScreen(onBackClick = { navController.popBackStack() })
}
```

---

### 파일 구조 업데이트

```
app/src/main/java/com/example/celestialsanctuary/
├── data/
│   ├── FortuneDataStore.kt        # [M9] 운세 데이터 저장
│   └── ...
├── notification/                   # [M9] 알림 시스템
│   ├── NotificationHelper.kt
│   ├── DailyReminderReceiver.kt
│   ├── DailyReminderScheduler.kt
│   ├── BootReceiver.kt
│   └── NotificationPreferences.kt
├── ui/screen/
│   ├── fortune/
│   │   ├── DailyFortuneScreen.kt   # 스트릭, 공유 추가
│   │   └── DailyFortuneViewModel.kt # Repository, SoundManager 적용
│   ├── weekly/                      # [M9] 주간 운세
│   │   ├── WeeklyFortuneScreen.kt
│   │   └── WeeklyFortuneViewModel.kt
│   └── settings/                    # [M9] 설정 화면
│       ├── SettingsScreen.kt
│       └── SettingsViewModel.kt
├── util/                            # [M9] 유틸리티
│   ├── SoundManager.kt
│   └── ShareManager.kt
└── ...
```

---

## [M8] 게이미피케이션 - 일일 운세 ✅

### 목표
게임 스타일 요소로 재방문 유도 및 재미 요소 강화

---

### M8.1 DailyFortuneScreen 구현 ✅

**새 파일:** `ui/screen/fortune/DailyFortuneScreen.kt`

```kotlin
@Composable
fun DailyFortuneScreen(
    onBackClick: () -> Unit,
    viewModel: DailyFortuneViewModel = hiltViewModel()
)
```

**구조:**
- 3개 탭: 수정구슬 | 타로카드 | 행운주사위
- HorizontalPager로 스와이프 전환
- 각 탭별 독립적 상태 관리

---

### M8.2 수정구슬 기능 ✅

**인터랙션:**
```kotlin
// 드래그로 흔들기 감지
.pointerInput(Unit) {
    detectDragGestures(
        onDrag = { _, dragAmount ->
            // 흔들림 카운트 증가
            if (dragAmount.x.absoluteValue > 10) shakeCount++
        },
        onDragEnd = {
            if (shakeCount > 5) onReveal()
        }
    )
}
```

**결과 데이터:**
```kotlin
data class CrystalBallResult(
    val message: String,        // 오늘의 메시지
    val luckyNumbers: List<Int>, // 행운 숫자 3개
    val luckyColor: String,      // 행운 색상
    val luckyDirection: String   // 행운 방향
)
```

---

### M8.3 타로카드 기능 ✅

**22장 메이저 아르카나:**
```kotlin
data class TarotCard(
    val id: Int,
    val name: String,   // "바보", "마법사", ...
    val symbol: String, // 🃏, 🎭, ...
    val meaning: String // 카드 해석
)
```

**카드 뒤집기 애니메이션:**
```kotlin
// 3D Y축 회전
.graphicsLayer {
    rotationY = rotation  // 0f → 180f
    cameraDistance = 12f * density
}
```

---

### M8.4 행운주사위 기능 ✅

**결과 계산:**
```kotlin
data class DiceResult(
    val numbers: List<Int>,    // 3개 주사위 값
    val interpretation: String, // 해석 메시지
    val luckyLevel: Int         // 1~5 (⭐ 개수)
)

// 트리플 = 5⭐, 합계 15+ = 4⭐, ...
```

**굴리기 애니메이션:**
```kotlin
rotation.animateTo(
    targetValue = rotation.value + 720f + Random.nextFloat() * 360f,
    animationSpec = tween(1500, easing = FastOutSlowInEasing)
)
```

---

### M8.5 Hall 화면 배너 ✅

**DailyFortuneBanner 컴포넌트:**
```kotlin
@Composable
private fun DailyFortuneBanner(onClick: () -> Unit)
```

**특징:**
- 반짝이는 금색 테두리 (shimmer 애니메이션)
- 🔮🃏🎲 아이콘 + "오늘의 운명" 텍스트
- GO! 배지 (게임 스타일)
- 프레스 시 스케일 애니메이션

---

### M8.6 게임 요소 ✅

**날짜 기반 시드:**
```kotlin
private val dailySeed = Calendar.getInstance().run {
    get(Calendar.YEAR) * 10000 + get(Calendar.DAY_OF_YEAR)
}

val random = Random(dailySeed)
// → 같은 날은 같은 결과, 다음 날은 다른 결과
```

**리니지/모바일게임 참고:**
- 화려한 결과 카드 UI
- 행운 레벨 별점 표시
- 애니메이션 강조 효과

---

### 파일 구조 업데이트

```
ui/screen/fortune/           # [M8] 새 폴더
├── DailyFortuneScreen.kt    # 메인 UI (3개 탭)
└── DailyFortuneViewModel.kt # 상태 관리 + 데이터

navigation/
└── Screen.kt               # Fortune route 추가
└── NavGraph.kt             # Fortune 화면 연결

ui/screen/hall/
└── HouseHallScreen.kt      # DailyFortuneBanner 추가
```

---

## [M7] 아키텍처 고도화 ✅

### 목표
Clean Architecture 원칙 적용, 코드 품질 및 테스트 가능성 향상

---

### M7.1 Result Sealed Class ✅

**파일:** `domain/model/Result.kt`

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String, val exception: Throwable? = null) : Result<Nothing>()
    data object Loading : Result<Nothing>()

    // 유틸리티 함수
    fun getOrNull(): T?
    fun <R> map(transform: (T) -> R): Result<R>
    inline fun onSuccess(action: (T) -> Unit): Result<T>
    inline fun onError(action: (String, Throwable?) -> Unit): Result<T>

    companion object {
        fun <T> success(data: T): Result<T>
        fun error(message: String, exception: Throwable? = null): Result<Nothing>
        fun loading(): Result<Nothing>
    }
}
```

**장점:**
- 비동기 작업 결과를 명시적으로 표현
- Success/Error/Loading 세 가지 상태 처리
- `when` 문으로 exhaustive 패턴 매칭
- 유틸리티 함수로 체이닝 가능

---

### M7.2 UseCase 계층 ✅

#### GetAllHousesUseCase
**파일:** `domain/usecase/GetAllHousesUseCase.kt`

```kotlin
class GetAllHousesUseCase @Inject constructor(
    private val chartRepository: ChartRepository,
    private val userRepository: UserRepository
) {
    operator fun invoke(): Flow<Result<List<HouseWithVisitState>>>
}
```

**책임:**
- 차트 데이터와 방문 상태 조합
- HouseWithVisitState 모델로 변환
- Flow로 실시간 업데이트 제공

#### GetHouseDetailUseCase
**파일:** `domain/usecase/GetHouseDetailUseCase.kt`

```kotlin
class GetHouseDetailUseCase @Inject constructor(
    private val chartRepository: ChartRepository,
    private val userRepository: UserRepository
) {
    suspend operator fun invoke(
        houseIndex: Int,
        markAsVisited: Boolean = true
    ): Result<HouseDetail>
}
```

**책임:**
- 하우스 상세 정보 조회
- 방문 기록 저장 (선택적)
- 에러 핸들링

#### GetUserProfileUseCase
**파일:** `domain/usecase/GetUserProfileUseCase.kt`

```kotlin
class GetUserProfileUseCase @Inject constructor(
    private val userRepository: UserRepository,
    private val chartRepository: ChartRepository
) {
    operator fun invoke(): Flow<Result<UserProfileWithChart>>
}
```

**책임:**
- 사용자 프로필 조회
- 차트 정보 (태양/달/상승) 조합
- 오늘의 운세 생성

#### SaveUserProfileUseCase
**파일:** `domain/usecase/SaveUserProfileUseCase.kt`

```kotlin
class SaveUserProfileUseCase @Inject constructor(
    private val userRepository: UserRepository
) {
    suspend operator fun invoke(
        userName: String?,
        birthDate: String,
        birthTime: String,
        birthLocation: String
    ): Result<Unit>
}
```

**책임:**
- 입력값 유효성 검증
- 날짜/시간 파싱
- 프로필 저장

---

### M7.3 ViewModel UseCase 적용 ✅

#### HouseHallViewModel 변경
```kotlin
@HiltViewModel
class HouseHallViewModel @Inject constructor(
    private val getAllHousesUseCase: GetAllHousesUseCase,
    private val getUserProfileUseCase: GetUserProfileUseCase
) : ViewModel() {
    // Repository 직접 접근 → UseCase 통해 접근
    // combine으로 두 Flow 결합
}
```

#### HouseRoomViewModel 변경
```kotlin
@HiltViewModel
class HouseRoomViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle,
    private val getHouseDetailUseCase: GetHouseDetailUseCase
) : ViewModel() {
    // 12개 하우스 로드 시 UseCase 사용
    // 페이지 변경 시 방문 기록도 UseCase 통해
}
```

#### OnboardingViewModel 변경
```kotlin
@HiltViewModel
class OnboardingViewModel @Inject constructor(
    private val saveUserProfileUseCase: SaveUserProfileUseCase
) : ViewModel() {
    // 유효성 검증이 UseCase로 이동
    // Result로 성공/실패 처리
}
```

---

### M7.4 학습 문서 ✅

**파일:** `ARCHITECTURE.md`

Clean Architecture 학습 문서 작성:
- 레이어 구조 (Domain/Data/Presentation)
- SOLID 원칙 설명
- 상태 관리 패턴
- 테스트 전략
- 프로젝트 예시 활용

---

### 아키텍처 개선 요약

| 구분 | 이전 | 개선 후 |
|------|------|---------|
| 비즈니스 로직 | Repository에 혼재 | UseCase에 캡슐화 |
| 에러 처리 | try-catch만 | Result sealed class |
| 테스트 가능성 | 낮음 | UseCase 단위 테스트 가능 |
| 코드 재사용 | 어려움 | UseCase 조합으로 재사용 |

---

## [M6] UX 몰입감 개선 ✅

### 2024년 구현 완료 항목

---

### M6.1 탐험 진행도 시스템 ✅

**목표:** 사용자가 12개 하우스를 탐험하도록 유도

**구현 내용:**

#### 데이터 저장 (`UserPreferencesDataStore.kt`)
```kotlin
// 방문한 하우스 ID Set 저장
val visitedHouses: Flow<Set<Int>>
suspend fun markHouseVisited(houseIndex: Int)
suspend fun resetExploration()
```

#### Repository 확장 (`UserRepository.kt`)
- `visitedHouses` Flow 추가
- `markHouseVisited()` 메서드
- `getVisitedCount()` 메서드

#### HouseHallScreen 변경사항
| 컴포넌트 | 설명 |
|---------|------|
| `ExplorationProgressBar` | "탐험 진행 3/12" 프로그레스 바 |
| `HouseDoorCard` 배지 | 방문한 문에 금색 ✓ 표시 |
| `CelebrationOverlay` | 12개 완료 시 축하 애니메이션 |

#### HouseRoomViewModel 변경
- `init` 블록에서 자동으로 `markAsVisited()` 호출

---

### M6.2 온보딩 개선 ✅

**목표:** 출생정보 입력을 마법적인 경험으로 변환

**구현 내용:**

#### 3단계 마법사 UI
| 단계 | 심볼 | 제목 | 입력 |
|------|------|------|------|
| 1/3 | ☉ | 태양의 날 | 생년월일 (YYYY-MM-DD) |
| 2/3 | ☽ | 달의 시간 | 출생 시간 (HH:MM) |
| 3/3 | ⊕ | 지구의 자리 | 출생 장소 |

#### 새로운 컴포넌트
```kotlin
@Composable
private fun StepIndicator(currentStep: Int, totalSteps: Int)

@Composable
private fun StepCard(
    symbol: String,
    title: String,
    subtitle: String,
    content: @Composable () -> Unit
)

@Composable
private fun MagicTextField(
    value: String,
    onValueChange: (String) -> Unit,
    placeholder: String,
    visualTransformation: VisualTransformation
)

@Composable
private fun NavigationButtons(
    currentStep: Int,
    canProceed: Boolean,
    onBack: () -> Unit,
    onNext: () -> Unit,
    onComplete: () -> Unit
)
```

#### 애니메이션
- `AnimatedContent`로 단계 간 슬라이드 전환
- 입력 필드 포커스 시 금색 테두리 글로우
- "별자리 지도를 그리는 중..." 로딩 애니메이션

---

### M6.4 House Room 인터랙션 ✅

**목표:** 하우스 간 탐색 편의성 및 상세 정보 제공

**구현 내용:**

#### 스와이프 네비게이션 (`HouseRoomScreen.kt`)
```kotlin
// HorizontalPager로 12개 하우스 스와이프
val pagerState = rememberPagerState(
    initialPage = uiState.initialHouseIndex - 1,
    pageCount = { 12 }
)

HorizontalPager(state = pagerState) { page ->
    HouseRoomContent(detail = uiState.houseDetails[page])
}
```

#### ViewModel 변경 (`HouseRoomViewModel.kt`)
```kotlin
data class HouseRoomUiState(
    val houseDetails: List<HouseDetail> = emptyList(),  // 12개 전체 로드
    val initialHouseIndex: Int = 1,
    val currentHouseIndex: Int = 1,
    val isLoading: Boolean = false
)

fun onPageChanged(houseIndex: Int)  // 페이지 변경 시 방문 기록
```

#### 페이지 인디케이터
```kotlin
@Composable
private fun PageIndicator(
    currentPage: Int,
    pageCount: Int,
    modifier: Modifier
)
```
- 12개 점으로 현재 위치 표시
- 선택된 점: 10dp 금색
- 미선택 점: 6dp 어두운 금색

#### 좌우 화살표 네비게이션
- 화면 양쪽에 반투명 화살표 버튼
- 첫 페이지/마지막 페이지에서 비활성화 (alpha 0.3)

#### 수정구슬 길게 누르기 상세 모달
```kotlin
@Composable
private fun PlanetDetailModal(
    planet: Planet?,
    house: House,
    state: HouseState,
    onDismiss: () -> Unit
)
```

**모달 구성요소:**
| 섹션 | 내용 |
|------|------|
| 행성 심볼 | 100dp 크기, 빛나는 원형 배경 |
| 행성 이름 | 한글명 (28sp) + 영문명 |
| 상태 배지 | 빈 방 / 손님 행성 / ✨ 집주인 귀환 |
| 행성 설명 | 각 행성별 의미 설명 |
| 하우스 정보 | 하우스 번호, 주인 행성, 영역명 |

#### 행성별 설명 텍스트
```kotlin
private fun getPlanetDescription(planet: Planet?, house: House, state: HouseState): String
```
- 태양: 자아, 정체성, 생명력
- 달: 감정, 본능, 무의식
- 수성: 소통, 지성, 학습
- 금성: 사랑, 아름다움, 가치관
- 화성: 행동, 에너지, 욕망
- 목성: 확장, 행운, 철학
- 토성: 구조, 제한, 책임
- 천왕성: 혁신, 자유, 독창성
- 해왕성: 꿈, 영성, 상상력
- 명왕성: 변형, 재생, 심층 심리

---

### M6.5 개인화 강화 ✅

**목표:** 사용자가 "나만의 별자리 여정"을 느끼도록

**구현 내용:**

#### 온보딩 이름 입력 추가 (`OnboardingScreen.kt`, `OnboardingViewModel.kt`)

| 단계 | 심볼 | 제목 | 설명 |
|------|------|------|------|
| 1/4 | ✧ | 당신의 이름 | 선택 입력 (최대 20자) |
| 2/4 | ☉ | 탄생의 날 | 생년월일 |
| 3/4 | ☽ | 탄생의 시간 | 출생 시간 |
| 4/4 | ⊕ | 탄생의 장소 | 출생 장소 |

```kotlin
// OnboardingUiState 확장
data class OnboardingUiState(
    val userName: String = "",  // 새로 추가
    val birthDate: String = "",
    val birthTime: String = "",
    val birthLocation: String = "",
    ...
)
```

#### 개인화된 Hall 화면 (`HouseHallScreen.kt`, `HouseHallViewModel.kt`)

**PersonalizedHeader 컴포넌트:**
- 사용자 이름이 있으면 "Luna의 천궁"
- 없으면 "THE 12 HOUSES"

**ChartSummaryCard 컴포넌트:**
| 항목 | 심볼 | 색상 |
|------|------|------|
| 태양궁 | ☉ | Gold |
| 달궁 | ☽ | Silver |
| 상승궁 | ↑ | GoldLight |

**DailyFortuneCard 컴포넌트:**
- 12개의 운세 메시지 중 날짜 기반 선택
- 같은 날에는 같은 메시지 표시
- `dayOfYear % fortunes.size`로 결정

```kotlin
// HouseHallUiState 확장
data class HouseHallUiState(
    ...
    val userName: String? = null,
    val moonSign: String? = null,  // 새로 추가
    val dailyFortune: String = "",  // 새로 추가
    ...
)
```

#### 운세 메시지 예시
```kotlin
val fortunes = listOf(
    "오늘은 창의적인 에너지가 넘치는 날입니다.",
    "주변 사람들과의 소통이 행운을 가져올 것입니다.",
    "내면의 직감을 믿으세요. 별들이 당신의 편입니다.",
    ...
)
```

---

## [M5] 신비로운 분위기 강화 ✅

### M5.1 별 배경 시스템 ✅

**파일:** `ui/component/StarFieldBackground.kt`

```kotlin
@Composable
fun StarFieldBackground(
    modifier: Modifier = Modifier,
    starCount: Int = 80,
    showNebula: Boolean = true,
    nebulaColor: Color = RoyalPurple,
    content: @Composable BoxScope.() -> Unit
)
```

**기능:**
- Canvas로 랜덤 위치에 별 그리기
- 별 반짝임 애니메이션 (알파값 0.3~1.0 변화)
- 성운 효과 (radialGradient)
- 모든 화면에서 재사용 가능

**적용 화면:**
| 화면 | 별 개수 | 성운 색상 |
|------|---------|----------|
| OpeningScreen | 100개 | RoyalPurple |
| HouseHallScreen | 60개 | RoyalPurple |
| HouseRoomScreen | 50개 | 행성 색상 |

---

### M5.2 Opening Screen 개선 ✅

**파일:** `ui/screen/opening/OpeningScreen.kt`

**변경사항:**
- 별 배경 적용 (100개 별 + 성운)
- `GlowingSymbol` 컴포넌트 사용
- 스케일 + 페이드인 애니메이션

---

### M5.3 Hall Screen 분위기 개선 ✅

**파일:** `ui/screen/hall/HouseHallScreen.kt`

**변경사항:**
- 별 배경 적용 (60개 별)
- 문 프레스 시 스케일 축소 (0.95f) + 글로우 강화
- 상태별 그라디언트 테두리
- 탐험 진행도 바

---

### M5.4 House Room 효과 강화 ✅

**파일:** `ui/screen/house/HouseRoomScreen.kt`

**변경사항:**
- 별 배경 (행성 색상 성운)
- 수정구슬 터치 시 파문 효과 (800ms)
- OWNER_HOME 상태 빛 펄스 강화
- 행성 색상 반영

---

## [M4] 애니메이션 & 폴리싱 ✅

### 완료 항목
- Opening Screen 별 배경 + 스케일 애니메이션
- Hall Screen 문 프레스 효과 (스케일 + 글로우)
- House Room 수정구슬 터치 파문 효과
- OWNER_HOME 상태 빛 펄스 강화

---

## 파일 구조

```
app/src/main/java/com/example/celestialsanctuary/
├── data/
│   ├── local/
│   │   └── UserPreferencesDataStore.kt  # visitedHouses 추가
│   ├── repository/
│   │   ├── ChartRepository.kt
│   │   └── UserRepository.kt  # 탐험 메서드 추가
│   └── FortuneDataStore.kt      # [M9] 운세 데이터 저장
├── domain/
│   ├── model/
│   │   ├── House.kt
│   │   ├── HouseDetail.kt
│   │   ├── HouseState.kt
│   │   ├── Planet.kt
│   │   └── Result.kt           # [M7] Result sealed class
│   └── usecase/                 # [M7] UseCase 계층
│       ├── GetAllHousesUseCase.kt
│       ├── GetHouseDetailUseCase.kt
│       ├── GetUserProfileUseCase.kt
│       └── SaveUserProfileUseCase.kt
├── notification/                # [M9] 알림 시스템
│   ├── NotificationHelper.kt
│   ├── DailyReminderReceiver.kt
│   ├── DailyReminderScheduler.kt
│   ├── BootReceiver.kt
│   └── NotificationPreferences.kt
├── ui/
│   ├── component/
│   │   ├── StarFieldBackground.kt  # [M5] 별 배경
│   │   ├── GlowingSymbol.kt        # [M5] 빛나는 심볼
│   │   └── CelebrationOverlay.kt   # [M6] 축하 오버레이
│   ├── screen/
│   │   ├── opening/
│   │   │   └── OpeningScreen.kt    # 별 배경 적용
│   │   ├── onboarding/
│   │   │   ├── OnboardingScreen.kt # 4단계 마법사 UI
│   │   │   └── OnboardingViewModel.kt # [M7] UseCase 적용
│   │   ├── hall/
│   │   │   ├── HouseHallScreen.kt  # 개인화, 진행도, 배너
│   │   │   └── HouseHallViewModel.kt # [M7] UseCase 적용
│   │   ├── house/
│   │   │   ├── HouseRoomScreen.kt  # 스와이프, 모달
│   │   │   └── HouseRoomViewModel.kt # [M7] UseCase 적용
│   │   ├── fortune/             # [M8] 일일 운세
│   │   │   ├── DailyFortuneScreen.kt
│   │   │   └── DailyFortuneViewModel.kt
│   │   ├── weekly/              # [M9] 주간 운세
│   │   │   ├── WeeklyFortuneScreen.kt
│   │   │   └── WeeklyFortuneViewModel.kt
│   │   └── settings/            # [M9] 설정 화면
│   │       ├── SettingsScreen.kt
│   │       └── SettingsViewModel.kt
│   └── theme/
│       └── Color.kt
├── util/                        # [M9] 유틸리티
│   ├── SoundManager.kt
│   └── ShareManager.kt
├── navigation/
│   ├── Screen.kt
│   └── NavGraph.kt
├── ARCHITECTURE.md              # [M7] 아키텍처 학습 문서
├── CHANGELOG.md                 # 개발 이력
└── PLAN.md                      # 개발 계획
```

---

## 다음 작업 예정 (선택적)

### v1.0 출시 준비
- [ ] 출시 준비 체크리스트 (ROADMAP.md 참조)
- [ ] 앱 아이콘 & 스토어 에셋 준비
- [ ] 개인정보처리방침 페이지 생성
- [ ] Release APK 빌드 및 테스트

### v1.1 업데이트
- [ ] 앱 위젯 구현
- [ ] 사운드 효과 추가 (mp3 파일)
- [ ] 결과 이미지 저장 기능
- [ ] 월간 운세

### 추가 개선 사항
- [ ] Hall 원형 배치 레이아웃
- [ ] 애니메이션 시스템 모듈화
- [ ] 단위 테스트 추가
- [ ] 성능 최적화 (리컴포지션, ProGuard)

---

## 기술 스택

- **UI:** Jetpack Compose, Material3
- **아키텍처:** MVVM + Clean Architecture
- **DI:** Hilt
- **상태관리:** StateFlow, SharedFlow
- **저장소:** DataStore Preferences
- **애니메이션:** Compose Animation API
