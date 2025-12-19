# Android 아키텍처 학습 가이드

> Celestial Sanctuary 프로젝트를 예시로 한 Android Clean Architecture 학습 문서

---

## 목차

1. [아키텍처 개요](#1-아키텍처-개요)
2. [계층별 역할과 책임](#2-계층별-역할과-책임)
3. [의존성 규칙](#3-의존성-규칙)
4. [실제 코드로 보는 설계 패턴](#4-실제-코드로-보는-설계-패턴)
5. [좋은 설계 vs 나쁜 설계](#5-좋은-설계-vs-나쁜-설계)
6. [SOLID 원칙 적용](#6-solid-원칙-적용)
7. [상태 관리 패턴](#7-상태-관리-패턴)
8. [테스트 가능한 설계](#8-테스트-가능한-설계)
9. [자주 하는 실수와 해결책](#9-자주-하는-실수와-해결책)

---

## 1. 아키텍처 개요

### 1.1 Clean Architecture란?

Robert C. Martin(Uncle Bob)이 제안한 소프트웨어 설계 철학입니다.

```
┌─────────────────────────────────────────────────────────┐
│                      UI Layer                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │               Presentation Layer                 │   │
│  │  ┌─────────────────────────────────────────┐   │   │
│  │  │              Domain Layer                │   │   │
│  │  │  ┌─────────────────────────────────┐   │   │   │
│  │  │  │          Data Layer             │   │   │   │
│  │  │  └─────────────────────────────────┘   │   │   │
│  │  └─────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘

의존성 방향: 바깥 → 안쪽 (UI → Domain ← Data)
```

### 1.2 이 프로젝트의 구조

```
app/src/main/java/com/example/celestialsanctuary/
│
├── 📁 data/                    # Data Layer
│   ├── 📁 local/
│   │   └── UserPreferencesDataStore.kt
│   ├── 📁 astrology/
│   │   ├── AstrologyEngine.kt
│   │   └── BirthChart.kt
│   └── 📁 repository/
│       ├── ChartRepository.kt
│       └── UserRepository.kt
│
├── 📁 domain/                  # Domain Layer
│   ├── 📁 model/
│   │   ├── House.kt
│   │   ├── Planet.kt
│   │   ├── HouseState.kt
│   │   ├── HouseDetail.kt
│   │   └── UserProfile.kt
│   └── 📁 usecase/             # M7에서 추가
│       ├── GetAllHousesUseCase.kt
│       └── GetHouseDetailUseCase.kt
│
├── 📁 ui/                      # Presentation Layer
│   ├── 📁 screen/
│   │   ├── 📁 opening/
│   │   ├── 📁 onboarding/
│   │   ├── 📁 hall/
│   │   │   ├── HouseHallScreen.kt
│   │   │   └── HouseHallViewModel.kt
│   │   └── 📁 house/
│   ├── 📁 component/
│   │   ├── StarFieldBackground.kt
│   │   └── CelebrationOverlay.kt
│   └── 📁 theme/
│
├── 📁 di/                      # Dependency Injection
│   └── AppModule.kt
│
└── 📁 navigation/
    └── NavGraph.kt
```

---

## 2. 계층별 역할과 책임

### 2.1 Domain Layer (도메인 계층)

> **핵심 비즈니스 로직을 담당. 다른 계층에 의존하지 않음.**

#### Model (엔티티)
```kotlin
// domain/model/Planet.kt
enum class Planet(
    val symbol: String,
    val displayName: String,
    val color: Color
) {
    SUN("☉", "태양", Color(0xFFFFD700)),
    MOON("☽", "달", Color(0xFFE0E0E0)),
    MERCURY("☿", "수성", Color(0xFFA0A0A0)),
    // ...
}
```

**좋은 점:**
- 순수 Kotlin 클래스 (Android 의존성 없음)
- 불변(immutable) 객체
- 명확한 타입 정의

#### UseCase (유스케이스)
```kotlin
// domain/usecase/GetAllHousesUseCase.kt
class GetAllHousesUseCase @Inject constructor(
    private val chartRepository: ChartRepository
) {
    operator fun invoke(): Flow<List<HouseWithState>> {
        return chartRepository.getAllHousesWithState()
    }
}
```

**역할:**
- 하나의 비즈니스 작업을 캡슐화
- ViewModel에서 직접 Repository를 호출하지 않게 함
- 테스트하기 쉬움

---

### 2.2 Data Layer (데이터 계층)

> **데이터 소스와의 통신 담당 (DB, API, SharedPreferences 등)**

#### DataStore
```kotlin
// data/local/UserPreferencesDataStore.kt
class UserPreferencesDataStore(private val context: Context) {

    private object PreferencesKeys {
        val USER_NAME = stringPreferencesKey("user_name")
        val BIRTH_DATE_TIME = longPreferencesKey("birth_date_time")
        val VISITED_HOUSES = stringSetPreferencesKey("visited_houses")
    }

    val userName: Flow<String?> = context.dataStore.data
        .map { preferences -> preferences[PreferencesKeys.USER_NAME] }

    suspend fun saveUserProfile(name: String?, birthDateTime: Long, location: String) {
        context.dataStore.edit { preferences ->
            name?.let { preferences[PreferencesKeys.USER_NAME] = it }
            preferences[PreferencesKeys.BIRTH_DATE_TIME] = birthDateTime
        }
    }
}
```

**좋은 점:**
- Flow로 반응형 데이터 제공
- suspend 함수로 비동기 처리
- 단일 책임 (저장소 관리만)

#### Repository
```kotlin
// data/repository/UserRepository.kt
@Singleton
class UserRepository @Inject constructor(
    private val dataStore: UserPreferencesDataStore
) {
    val userProfile: Flow<UserProfile?> = combine(
        dataStore.userName,
        dataStore.birthDateTime,
        dataStore.birthLocation
    ) { name, dateTime, location ->
        if (dateTime != null && location != null) {
            UserProfile(name, dateTime, location)
        } else null
    }

    suspend fun saveUserProfile(profile: UserProfile) {
        dataStore.saveUserProfile(
            name = profile.name,
            birthDateTime = profile.birthDateTime,
            birthLocation = profile.birthLocation
        )
    }
}
```

**Repository 패턴의 장점:**
- 데이터 소스 추상화 (나중에 Room DB로 변경해도 ViewModel 수정 불필요)
- 여러 데이터 소스 조합 가능
- 캐싱 로직 추가 용이

---

### 2.3 Presentation Layer (프레젠테이션 계층)

> **UI와 사용자 상호작용 담당**

#### ViewModel
```kotlin
// ui/screen/hall/HouseHallViewModel.kt
@HiltViewModel
class HouseHallViewModel @Inject constructor(
    private val chartRepository: ChartRepository,
    private val userRepository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(HouseHallUiState(isLoading = true))
    val uiState: StateFlow<HouseHallUiState> = _uiState.asStateFlow()

    init {
        loadHouses()
    }

    private fun loadHouses() {
        viewModelScope.launch {
            combine(
                chartRepository.getAllHousesWithState(),
                userRepository.visitedHouses,
                userRepository.userProfile
            ) { houses, visited, profile ->
                HouseHallUiState(
                    houses = houses.map { /* 변환 */ },
                    userName = profile?.name,
                    visitedCount = visited.size
                )
            }.collect { state ->
                _uiState.value = state
            }
        }
    }
}
```

**ViewModel의 역할:**
- UI 상태 관리
- 비즈니스 로직 호출 (UseCase/Repository)
- 생명주기 인식 (viewModelScope)

#### Composable (Screen)
```kotlin
// ui/screen/hall/HouseHallScreen.kt
@Composable
fun HouseHallScreen(
    onHouseClick: (Int) -> Unit,
    viewModel: HouseHallViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    // UI 렌더링만 담당
    StarFieldBackground {
        Column {
            PersonalizedHeader(userName = uiState.userName)
            HouseGrid(
                houses = uiState.houses,
                onClick = onHouseClick
            )
        }
    }
}
```

**Composable 함수의 원칙:**
- 상태를 소유하지 않음 (State Hoisting)
- ViewModel에서 상태를 받아 표시만 함
- 사용자 이벤트는 콜백으로 전달

---

## 3. 의존성 규칙

### 3.1 의존성 방향

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│     UI       │ ──▶ │   Domain     │ ◀── │    Data      │
│  (Screen,    │     │  (UseCase,   │     │ (Repository, │
│   ViewModel) │     │    Model)    │     │  DataStore)  │
└──────────────┘     └──────────────┘     └──────────────┘
        │                   ▲                    │
        └───────────────────┴────────────────────┘
              모두 Domain을 향해 의존
```

### 3.2 잘못된 의존성 예시

```kotlin
// ❌ 나쁜 예: Domain이 Data에 의존
// domain/model/House.kt
data class House(
    val index: Int,
    val dataStore: UserPreferencesDataStore  // Domain이 Data 계층 알면 안됨!
)

// ❌ 나쁜 예: Domain이 UI에 의존
// domain/model/Planet.kt
enum class Planet(
    val color: androidx.compose.ui.graphics.Color  // UI 라이브러리 의존!
)
```

### 3.3 올바른 의존성

```kotlin
// ✅ 좋은 예: Domain은 순수 Kotlin
// domain/model/Planet.kt
enum class Planet(
    val symbol: String,
    val displayName: String,
    val colorHex: Long  // 원시 타입 사용
) {
    SUN("☉", "태양", 0xFFFFD700)
}

// UI에서 변환
// ui/theme/Color.kt
val Planet.color: Color
    get() = Color(this.colorHex)
```

---

## 4. 실제 코드로 보는 설계 패턴

### 4.1 State Pattern (상태 패턴)

```kotlin
// domain/model/HouseState.kt
enum class HouseState {
    EMPTY,       // 행성 없음
    TENANT,      // 손님 행성 있음
    OWNER_HOME   // 집주인 행성 있음 (가장 강력)
}

// 사용: 상태에 따른 UI 분기
@Composable
fun HouseDoorCard(state: HouseState) {
    val borderColor = when (state) {
        HouseState.EMPTY -> GoldDark
        HouseState.TENANT -> TenantGlow
        HouseState.OWNER_HOME -> OwnerGlow
    }
    // ...
}
```

**장점:**
- 상태 전이가 명확함
- 새 상태 추가 시 when 절에서 컴파일 에러로 누락 방지

### 4.2 Observer Pattern (관찰자 패턴)

```kotlin
// Flow를 사용한 반응형 데이터 스트림
class UserRepository {
    val visitedHouses: Flow<Set<Int>> = dataStore.visitedHouses
}

// ViewModel에서 구독
viewModelScope.launch {
    userRepository.visitedHouses.collect { visited ->
        _uiState.value = _uiState.value.copy(visitedCount = visited.size)
    }
}

// Compose에서 상태로 수집
@Composable
fun Screen(viewModel: ViewModel) {
    val state by viewModel.uiState.collectAsState()
}
```

### 4.3 Factory Pattern (팩토리 패턴)

```kotlin
// Hilt가 의존성 생성을 담당
@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideUserPreferencesDataStore(
        @ApplicationContext context: Context
    ): UserPreferencesDataStore {
        return UserPreferencesDataStore(context)
    }

    @Provides
    @Singleton
    fun provideUserRepository(
        dataStore: UserPreferencesDataStore
    ): UserRepository {
        return UserRepository(dataStore)
    }
}
```

---

## 5. 좋은 설계 vs 나쁜 설계

### 5.1 ViewModel 설계

```kotlin
// ❌ 나쁜 예: 거대한 ViewModel
class BadViewModel : ViewModel() {
    // 너무 많은 책임
    fun loadHouses() { ... }
    fun loadUser() { ... }
    fun saveProfile() { ... }
    fun calculateAstrology() { ... }
    fun formatDate() { ... }
    fun validateInput() { ... }
}

// ✅ 좋은 예: 단일 책임
class HouseHallViewModel(
    private val getAllHousesUseCase: GetAllHousesUseCase,
    private val userRepository: UserRepository
) : ViewModel() {
    // Hall 화면에 필요한 것만
    private val _uiState = MutableStateFlow(HouseHallUiState())
    val uiState: StateFlow<HouseHallUiState> = _uiState.asStateFlow()

    fun loadHouses() { ... }
}
```

### 5.2 UiState 설계

```kotlin
// ❌ 나쁜 예: 개별 상태 변수들
class BadViewModel : ViewModel() {
    val isLoading = MutableStateFlow(false)
    val houses = MutableStateFlow<List<House>>(emptyList())
    val error = MutableStateFlow<String?>(null)
    val userName = MutableStateFlow<String?>(null)
    // 상태 동기화 어려움!
}

// ✅ 좋은 예: 단일 UiState
data class HouseHallUiState(
    val houses: List<HouseWithState> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
    val userName: String? = null
)

class GoodViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(HouseHallUiState())
    val uiState: StateFlow<HouseHallUiState> = _uiState.asStateFlow()

    // 상태 업데이트는 copy로
    fun setLoading() {
        _uiState.value = _uiState.value.copy(isLoading = true)
    }
}
```

### 5.3 Composable 설계

```kotlin
// ❌ 나쁜 예: 거대한 Composable
@Composable
fun BadScreen() {
    var name by remember { mutableStateOf("") }
    var date by remember { mutableStateOf("") }
    // 500줄의 UI 코드...
}

// ✅ 좋은 예: 작은 단위로 분리
@Composable
fun OnboardingScreen(viewModel: OnboardingViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsState()

    Column {
        StepIndicator(currentStep = uiState.currentStep)
        StepContent(step = uiState.currentStep, state = uiState)
        NavigationButtons(onNext = { viewModel.nextStep() })
    }
}

@Composable
private fun StepIndicator(currentStep: Int) { ... }

@Composable
private fun StepContent(step: Int, state: UiState) { ... }

@Composable
private fun NavigationButtons(onNext: () -> Unit) { ... }
```

---

## 6. SOLID 원칙 적용

### 6.1 S - Single Responsibility (단일 책임)

```kotlin
// ✅ 각 클래스는 하나의 책임만
class UserPreferencesDataStore { /* 저장소 관리 */ }
class UserRepository { /* 사용자 데이터 조합 */ }
class OnboardingViewModel { /* 온보딩 UI 상태 관리 */ }
class AstrologyEngine { /* 점성술 계산 */ }
```

### 6.2 O - Open/Closed (개방/폐쇄)

```kotlin
// ✅ 확장에 열려있고, 수정에 닫혀있음
sealed class HouseState {
    object Empty : HouseState()
    object Tenant : HouseState()
    object OwnerHome : HouseState()
    // 새 상태 추가 시 기존 코드 수정 불필요
    object Exalted : HouseState()  // 새 상태 추가
}
```

### 6.3 L - Liskov Substitution (리스코프 치환)

```kotlin
// ✅ 인터페이스를 통한 대체 가능성
interface ChartRepository {
    fun getAllHousesWithState(): Flow<List<HouseWithState>>
}

class RealChartRepository : ChartRepository { /* 실제 구현 */ }
class FakeChartRepository : ChartRepository { /* 테스트용 */ }
```

### 6.4 I - Interface Segregation (인터페이스 분리)

```kotlin
// ❌ 나쁜 예: 거대한 인터페이스
interface BadRepository {
    fun getHouses()
    fun saveUser()
    fun calculateChart()
    fun sendNotification()
}

// ✅ 좋은 예: 분리된 인터페이스
interface ChartRepository { fun getAllHousesWithState(): Flow<...> }
interface UserRepository { fun saveUserProfile(profile: UserProfile) }
```

### 6.5 D - Dependency Inversion (의존성 역전)

```kotlin
// ✅ 구체 클래스가 아닌 추상화에 의존
class HouseHallViewModel @Inject constructor(
    private val chartRepository: ChartRepository,  // 인터페이스
    private val userRepository: UserRepository     // 인터페이스
) : ViewModel()

// Hilt가 실제 구현체 주입
@Provides
fun provideChartRepository(impl: ChartRepositoryImpl): ChartRepository = impl
```

---

## 7. 상태 관리 패턴

### 7.1 단방향 데이터 흐름 (UDF)

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│    State ──────────▶ UI ──────────▶ Event          │
│      ▲                               │              │
│      │                               │              │
│      └───────── ViewModel ◀──────────┘              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

```kotlin
// State: 화면에 표시할 데이터
data class HouseHallUiState(
    val houses: List<HouseWithState>,
    val userName: String?
)

// UI: State를 표시
@Composable
fun HouseHallScreen(viewModel: HouseHallViewModel) {
    val state by viewModel.uiState.collectAsState()
    HouseGrid(houses = state.houses)
}

// Event: 사용자 액션
fun onHouseClick(houseIndex: Int) {
    navController.navigate("house/$houseIndex")
}
```

### 7.2 State Hoisting (상태 끌어올리기)

```kotlin
// ❌ 나쁜 예: Composable 내부에 상태
@Composable
fun BadTextField() {
    var text by remember { mutableStateOf("") }
    TextField(value = text, onValueChange = { text = it })
}

// ✅ 좋은 예: 상태를 상위로 끌어올림
@Composable
fun GoodTextField(
    value: String,
    onValueChange: (String) -> Unit
) {
    TextField(value = value, onValueChange = onValueChange)
}

// 사용
@Composable
fun ParentScreen(viewModel: ViewModel) {
    val state by viewModel.uiState.collectAsState()
    GoodTextField(
        value = state.userName,
        onValueChange = { viewModel.updateUserName(it) }
    )
}
```

---

## 8. 테스트 가능한 설계

### 8.1 의존성 주입으로 테스트 용이

```kotlin
// 프로덕션 코드
@HiltViewModel
class HouseHallViewModel @Inject constructor(
    private val chartRepository: ChartRepository
) : ViewModel()

// 테스트 코드
class HouseHallViewModelTest {

    private val fakeRepository = FakeChartRepository()
    private lateinit var viewModel: HouseHallViewModel

    @Before
    fun setup() {
        viewModel = HouseHallViewModel(fakeRepository)
    }

    @Test
    fun `하우스 로드 시 상태가 올바르게 변경됨`() {
        // Given
        fakeRepository.setHouses(listOf(testHouse))

        // When
        viewModel.loadHouses()

        // Then
        assertEquals(1, viewModel.uiState.value.houses.size)
    }
}
```

### 8.2 UseCase 테스트

```kotlin
class GetAllHousesUseCaseTest {

    @Test
    fun `빈 차트일 때 모든 하우스가 EMPTY 상태`() = runTest {
        // Given
        val fakeRepo = FakeChartRepository(emptyChart = true)
        val useCase = GetAllHousesUseCase(fakeRepo)

        // When
        val result = useCase().first()

        // Then
        assertTrue(result.all { it.state == HouseState.EMPTY })
    }
}
```

---

## 9. 자주 하는 실수와 해결책

### 9.1 실수: ViewModel에서 Context 사용

```kotlin
// ❌ 메모리 누수 위험
class BadViewModel(private val context: Context) : ViewModel() {
    fun showToast() {
        Toast.makeText(context, "Hello", Toast.LENGTH_SHORT).show()
    }
}

// ✅ 이벤트로 처리
class GoodViewModel : ViewModel() {
    private val _events = MutableSharedFlow<UiEvent>()
    val events = _events.asSharedFlow()

    fun triggerToast() {
        viewModelScope.launch {
            _events.emit(UiEvent.ShowToast("Hello"))
        }
    }
}

sealed class UiEvent {
    data class ShowToast(val message: String) : UiEvent()
}
```

### 9.2 실수: Composable에서 직접 비동기 호출

```kotlin
// ❌ 리컴포지션마다 호출됨
@Composable
fun BadScreen() {
    val data = someRepository.getData()  // 위험!
}

// ✅ ViewModel에서 처리
@Composable
fun GoodScreen(viewModel: ViewModel = hiltViewModel()) {
    val state by viewModel.uiState.collectAsState()
    Text(text = state.data)
}
```

### 9.3 실수: 무분별한 remember 사용

```kotlin
// ❌ 불필요한 remember
@Composable
fun BadComponent() {
    val text = remember { "Hello" }  // 상수는 remember 불필요
}

// ✅ 계산 비용이 클 때만 remember
@Composable
fun GoodComponent(items: List<Item>) {
    val sortedItems = remember(items) {
        items.sortedBy { it.priority }  // 비용이 큰 연산
    }
}
```

---

## 요약: 핵심 원칙

| 원칙 | 설명 |
|------|------|
| **계층 분리** | UI, Domain, Data 각각 독립적으로 |
| **단방향 의존성** | 바깥에서 안으로만 의존 |
| **단일 책임** | 한 클래스는 하나의 역할만 |
| **상태 불변성** | data class + copy() 사용 |
| **반응형 스트림** | Flow로 데이터 변화 감지 |
| **의존성 주입** | Hilt로 객체 생성 위임 |
| **테스트 가능성** | 인터페이스와 Fake 구현체 |

---

## 참고 자료

- [Android 공식 아키텍처 가이드](https://developer.android.com/topic/architecture)
- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Jetpack Compose 상태 관리](https://developer.android.com/jetpack/compose/state)
- [Kotlin Flow 가이드](https://kotlinlang.org/docs/flow.html)
