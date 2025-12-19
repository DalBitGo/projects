# Celestial Sanctuary - 프로젝트 컨텍스트

## 프로젝트 개요
점성술 12하우스를 신비로운 성소로 탐험하는 Android 앱

### 앱 컨셉
- 황금 고대 책이 열리면서 점성술 세계로 입장
- 12개의 황금 문(하우스)이 있는 홀에서 각 방을 탐험
- 각 방의 수정구슬이 사용자 차트에 따라 3단계 상태로 표시
- 사용자 맞춤 점성술 해석 제공

### 핵심 기능
1. **오프닝 애니메이션**: 황금 책이 열리는 Lottie 애니메이션
2. **12 하우스 홀**: 그리드 형태의 황금 문 선택 화면
3. **수정구슬 3단계 상태**:
   - EMPTY: 빈 방 (투명/회색)
   - TENANT: 손님 행성 (해당 행성 색상 오라)
   - OWNER_HOME: 집주인 행성 (금색 폭발 파티클)
4. **해석 오버레이**: 사용자 차트 기반 텍스트

---

## 기술 스택

| 항목 | 선택 |
|------|------|
| 언어 | Kotlin |
| UI | Jetpack Compose |
| 아키텍처 | MVVM + Clean Architecture |
| DI | Hilt |
| Navigation | Navigation Compose |
| 애니메이션 | Lottie Compose |
| 로컬 저장 | DataStore (설정), Room (해석 데이터) |
| 비동기 | Coroutines + Flow |

---

## 패키지 구조

```
com.example.celestialsanctuary/
├── MainActivity.kt
├── CelestialSanctuaryApp.kt          # Application 클래스 (Hilt)
│
├── navigation/
│   └── NavGraph.kt                    # Navigation 설정
│
├── domain/
│   ├── model/
│   │   ├── House.kt                   # 하우스 데이터
│   │   ├── Planet.kt                  # 행성 enum
│   │   ├── ZodiacSign.kt              # 별자리 enum
│   │   ├── HouseState.kt              # 방 상태 enum
│   │   ├── PlanetPlacement.kt         # 행성 배치
│   │   └── UserProfile.kt             # 사용자 프로필
│   └── usecase/
│       └── GetHouseDetailUseCase.kt
│
├── data/
│   ├── repository/
│   │   ├── HouseRepository.kt
│   │   └── UserRepository.kt
│   └── local/
│       └── HouseData.kt               # 하드코딩 데이터 (초기)
│
├── ui/
│   ├── theme/
│   │   ├── Color.kt
│   │   ├── Theme.kt
│   │   └── Type.kt
│   ├── component/
│   │   ├── PlanetOrb.kt               # 수정구슬 컴포넌트
│   │   ├── HouseDoorCard.kt           # 하우스 문 카드
│   │   ├── InterpretationOverlay.kt   # 해석 오버레이
│   │   └── SymbolBanner.kt            # 행성 기호 배너
│   └── screen/
│       ├── opening/
│       │   ├── OpeningScreen.kt
│       │   └── OpeningViewModel.kt
│       ├── onboarding/
│       │   ├── OnboardingScreen.kt
│       │   └── OnboardingViewModel.kt
│       ├── hall/
│       │   ├── HouseHallScreen.kt
│       │   └── HouseHallViewModel.kt
│       └── house/
│           ├── HouseRoomScreen.kt
│           └── HouseRoomViewModel.kt
│
└── di/
    └── AppModule.kt                   # Hilt 모듈
```

---

## 화면 플로우

```
[Opening] → [Onboarding] → [Hall] → [HouseRoom]
    │           │            │          │
  책 열림    출생정보     12개 문    수정구슬+해석
  애니메이션   입력        그리드     3단계 상태
```

### Navigation Routes
- `opening` - 스플래시/오프닝
- `onboarding` - 출생정보 입력 (첫 실행시만)
- `hall` - 메인 홀 (12 하우스 문)
- `house/{houseIndex}` - 하우스 상세 (1-12)

---

## 코딩 컨벤션

### Compose
- Composable 함수: PascalCase (`HouseHallScreen`)
- Preview 함수: `{ComponentName}Preview`
- Modifier는 항상 첫 번째 파라미터로

### State Management
- UI State: `data class {Screen}UiState`
- ViewModel: StateFlow로 상태 노출
- Side Effects: SharedFlow 또는 Channel

### Naming
- Screen: `{Name}Screen`
- ViewModel: `{Name}ViewModel`
- Repository: `{Name}Repository`
- UseCase: `{Action}{Target}UseCase`

---

## 하우스 & 주인 행성 매핑

| House | English | Korean | Owner Planet |
|-------|---------|--------|--------------|
| 1st | The Self | 자아 | Mars |
| 2nd | Possessions | 소유 | Venus |
| 3rd | Communication | 소통 | Mercury |
| 4th | Home | 가정 | Moon |
| 5th | Pleasure | 즐거움 | Sun |
| 6th | Health | 건강 | Mercury |
| 7th | Partnership | 관계 | Venus |
| 8th | Transformation | 변화 | Pluto |
| 9th | Philosophy | 철학 | Jupiter |
| 10th | Career | 직업 | Saturn |
| 11th | Community | 커뮤니티 | Uranus |
| 12th | Subconscious | 무의식 | Neptune |

---

## 색상 팔레트

### Primary Colors
- **Gold**: `#FFD700` - 메인 강조색
- **Deep Navy**: `#0D1B2A` - 배경
- **Royal Purple**: `#4A1C6F` - 보조 배경

### Planet Colors
- Sun: `#FFD700` (Gold)
- Moon: `#C0C0C0` (Silver)
- Mercury: `#87CEEB` (Sky Blue)
- Venus: `#FFB6C1` (Pink)
- Mars: `#FF4500` (Red-Orange)
- Jupiter: `#4169E1` (Royal Blue)
- Saturn: `#8B4513` (Brown)
- Uranus: `#00CED1` (Cyan)
- Neptune: `#9370DB` (Purple)
- Pluto: `#2F4F4F` (Dark Slate)

---

## 현재 개발 상태

### 완료
- [x] 프로젝트 초기 세팅 (Android Studio)
- [x] 기본 Compose 설정

### 진행 중
- [ ] 프로젝트 문서화

### 예정
- [ ] 의존성 추가
- [ ] 패키지 구조 생성
- [ ] 도메인 모델 작성
- [ ] Navigation 설정
- [ ] 테마 커스터마이징
- [ ] 각 화면 구현

---

## 참고 자료
- PDF 기획서: `astrology-app/점성술_앱_만들기_프로젝트.pdf`
- ChatGPT 정리 문서: 프로젝트 구조 및 UX 플로우 상세
