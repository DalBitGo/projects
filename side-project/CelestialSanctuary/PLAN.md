# Celestial Sanctuary - 개발 계획

## 마일스톤 개요

| 마일스톤 | 목표 | 상태 |
|----------|------|------|
| M1 | 프로젝트 기반 구축 | ✅ 완료 |
| M2 | 기본 화면 구현 (더미 데이터) | ✅ 완료 |
| M3 | 점성술 로직 & 데이터 연동 | ✅ 완료 |
| M4 | 애니메이션 & 폴리싱 | ✅ 완료 |
| M5 | 신비로운 분위기 강화 | ✅ 완료 |
| M6 | UX 몰입감 개선 | ✅ 완료 |
| M7 | 아키텍처 고도화 | ✅ 완료 |
| M8 | 게이미피케이션 (일일 운세) | ✅ 완료 |
| M9 | 고도화 & 디테일 | 📋 예정 |

---

## 완료된 마일스톤

### Milestone 1: 프로젝트 기반 구축 ✅
- 프로젝트 구조 확립
- Navigation Compose, Hilt, Lottie, DataStore 의존성
- 도메인 모델 (Planet, House, ZodiacSign, HouseState 등)
- 테마 커스터마이징 (Gold/DeepNavy/RoyalPurple)

### Milestone 2: 기본 화면 구현 ✅
- OpeningScreen: 페이드인 애니메이션
- OnboardingScreen: 출생정보 입력 폼
- HouseHallScreen: 12개 문 그리드
- HouseRoomScreen: 수정구슬 + 해석 카드

### Milestone 3: 점성술 로직 & 데이터 연동 ✅
- AstrologyEngine: 태양/달/행성 배치 계산
- ChartRepository: 하우스 상태 및 해석 생성
- UserRepository: DataStore 연동
- 3단계 상태 시스템 (EMPTY/TENANT/OWNER_HOME)

---

### Milestone 4: 애니메이션 & 폴리싱 ✅
- [x] Opening Screen 별 배경 + 스케일 애니메이션
- [x] Hall Screen 문 프레스 효과 (스케일 + 글로우)
- [x] House Room 수정구슬 터치 파문 효과
- [x] OWNER_HOME 상태 빛 펄스 강화

### Milestone 5: 신비로운 분위기 강화 ✅

#### 5.1 별 배경 시스템 ✅
- [x] `ui/component/StarFieldBackground.kt` 생성
- [x] Canvas로 랜덤 위치 별 그리기 (50-100개)
- [x] 별 반짝임 애니메이션 (알파값 변화)
- [x] 성운 효과 (radial gradient)
- [x] 모든 Screen에 배경으로 적용

#### 5.2 Opening Screen 개선 ✅
- [x] 별 배경 적용 (100개 별 + 성운)
- [x] GlowingSymbol 컴포넌트 (빛나는 ✦)
- [x] 스케일 + 페이드인 애니메이션
- [ ] Lottie 황금 책 애니메이션 (추후)

#### 5.3 Hall Screen 분위기 개선 ✅
- [x] 별 배경 적용 (60개 별)
- [x] 문 프레스 시 스케일 축소 + 글로우 강화
- [x] 상태별 그라디언트 테두리
- [x] 탐험 진행도 바

#### 5.4 House Room 효과 강화 ✅
- [x] 별 배경 (행성 색상 성운)
- [x] 수정구슬 터치 시 파문 효과 (800ms)
- [x] OWNER_HOME 상태 빛 펄스 강화
- [x] 행성 색상 반영

---

## 🎮 Milestone 6: UX 몰입감 개선 ✅

### 목표
사용자가 "탐험하고 싶다"는 욕구를 느끼도록

### 태스크

#### 6.1 탐험 진행도 시스템 ✅
- [x] DataStore에 방문 기록 저장 (visitedHouses)
- [x] UserRepository에 탐험 메서드 추가
- [x] HouseRoomViewModel에서 자동 방문 기록
- [x] Hall에 "3/12 탐험" 진행도 바
- [x] 방문한 문에 금색 ✓ 배지
- [x] 12개 완료 시 축하 오버레이 (CelebrationOverlay)

#### 6.2 온보딩 개선 ✅
- [x] 단계별 마법사 UI (1/3, 2/3, 3/3)
- [x] 슬라이드 전환 애니메이션
- [x] 각 단계별 심볼 (☉ ☽ ⊕)
- [x] 빛나는 입력 카드 UI
- [x] "별자리 지도를 그리는 중..." 로딩

#### 6.3 Hall 레이아웃 개선
- [ ] 원형 배치 옵션 (12개 문이 원으로)
- [ ] 또는 스와이프 캐러셀
- [ ] 첫 방문 시 안개 효과 → 점점 걷힘
- [ ] 중앙에 사용자 태양 기호 표시

#### 6.4 House Room 인터랙션 ✅
- [x] 좌우 스와이프로 이전/다음 하우스 (HorizontalPager)
- [x] 수정구슬 길게 누르기 → 상세 모달 (PlanetDetailModal)
- [x] 페이지 인디케이터 + 좌우 화살표 네비게이션
- [x] 행성별 상세 설명 텍스트

#### 6.5 개인화 강화 ✅
- [x] 사용자 이름 표시 ("Luna의 천궁")
- [x] 온보딩에 이름 입력 단계 추가 (4단계)
- [x] 태양/달/상승 요약 카드 (ChartSummaryCard)
- [x] 오늘의 운세 메시지 (DailyFortuneCard)

---

## 🏗️ Milestone 7: 아키텍처 고도화 ✅

### 목표
코드 품질, 테스트 가능성, 확장성 향상

### 태스크

#### 7.1 UseCase 계층 추가 ✅
- [x] `domain/usecase/GetAllHousesUseCase.kt`
- [x] `domain/usecase/GetHouseDetailUseCase.kt`
- [x] `domain/usecase/SaveUserProfileUseCase.kt`
- [x] `domain/usecase/GetUserProfileUseCase.kt`

**이전:** Repository가 비즈니스 로직 직접 처리
**개선:** UseCase가 비즈니스 로직 캡슐화, 단일 책임 원칙 준수

#### 7.2 에러 핸들링 개선 ✅
- [x] `domain/model/Result.kt` (sealed class)
```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String, val exception: Throwable?) : Result<Nothing>()
    data object Loading : Result<Nothing>()

    fun getOrNull(): T?
    fun <R> map(transform: (T) -> R): Result<R>
    inline fun onSuccess(action: (T) -> Unit): Result<T>
    inline fun onError(action: (String, Throwable?) -> Unit): Result<T>
}
```
- [x] UseCase에서 Result 반환 적용
- [x] ViewModel에서 Result 처리 및 에러 상태 표시

#### 7.3 ViewModel UseCase 적용 ✅
- [x] `HouseHallViewModel` → `GetAllHousesUseCase`, `GetUserProfileUseCase`
- [x] `HouseRoomViewModel` → `GetHouseDetailUseCase`
- [x] `OnboardingViewModel` → `SaveUserProfileUseCase`

#### 7.4 학습 문서 작성 ✅
- [x] `ARCHITECTURE.md` - Clean Architecture 학습 문서
- [x] 프로젝트 예시를 활용한 설계 패턴 설명

#### 7.5 추후 개선 사항 (선택적)
- [ ] 애니메이션 시스템 모듈화
- [ ] 단위 테스트 추가
- [ ] Compose 리컴포지션 최적화
- [ ] ProGuard 설정

---

## 🎮 Milestone 8: 게이미피케이션 (일일 운세) ✅

### 목표
게임 스타일 요소로 재방문 유도 및 재미 요소 강화

### 태스크

#### 8.1 DailyFortuneScreen 구현 ✅
- [x] 3개 탭 구조 (수정구슬/타로카드/주사위)
- [x] HorizontalPager로 스와이프 전환
- [x] 탭별 독립적 상태 관리

#### 8.2 수정구슬 기능 ✅
- [x] 드래그로 흔들기 인터랙션
- [x] 흔들림 감지 → 결과 공개
- [x] 오늘의 메시지 + 행운숫자/색상/방향
- [x] 글로우 애니메이션

#### 8.3 타로카드 기능 ✅
- [x] 22장 메이저 아르카나 카드
- [x] 3장 중 1장 선택
- [x] 카드 뒤집기 애니메이션 (3D rotationY)
- [x] 카드별 의미 해석

#### 8.4 행운주사위 기능 ✅
- [x] 3개 주사위 굴리기
- [x] 회전 애니메이션
- [x] 합계 기반 해석 (트리플 보너스)
- [x] 행운 레벨 (⭐ 1~5개)

#### 8.5 Hall 화면 연동 ✅
- [x] "오늘의 운명" 배너 추가
- [x] 반짝이는 테두리 애니메이션
- [x] GO! 배지 (게임 스타일)
- [x] 네비게이션 연결

#### 8.6 게임 요소 ✅
- [x] 날짜 기반 시드 (매일 다른 결과, 같은 날은 동일)
- [x] 화려한 결과 카드 UI
- [x] 리니지/모바일게임 스타일 UX

---

## 🚀 Milestone 9: 고도화 & 출시 준비

> 📋 상세 로드맵: **ROADMAP.md** 참조

### 목표
앱 완성도 높이기 및 스토어 출시 준비

---

### Phase 1: 사용자 참여 강화 (v1.0 필수)

#### 9.1.1 푸시 알림 시스템
- [ ] Firebase Cloud Messaging 연동
- [ ] 매일 오전 알림 스케줄링
- [ ] 알림 설정 화면 추가
- [ ] 미접속 유저 리텐션 알림

#### 9.1.2 일일 리셋 시스템
- [ ] 자정에 Fortune 상태 초기화
- [ ] WorkManager로 백그라운드 작업
- [ ] 마지막 접속 날짜 저장

---

### Phase 2: 콘텐츠 확장 (v1.1)

#### 9.2.1 주간 운세
- [ ] WeeklyFortuneScreen 구현
- [ ] 요일별 에너지 그래프
- [ ] 주간 조언 콘텐츠

#### 9.2.2 월간 운세
- [ ] MonthlyFortuneScreen 구현
- [ ] 월간 테마 & 흐름
- [ ] 중요 천문 이벤트

---

### Phase 3: 몰입감 강화 (v1.1)

#### 9.3.1 사운드 효과
- [ ] 수정구슬 흔들기 소리
- [ ] 카드 뒤집기 소리
- [ ] 주사위 굴리기 소리
- [ ] 결과 공개 효과음
- [ ] 설정에서 on/off

#### 9.3.2 햅틱 피드백
- [ ] 인터랙션에 진동 추가
- [ ] 강도 설정 옵션

---

### Phase 4: 공유 & 바이럴 (v1.2)

#### 9.4.1 결과 이미지 저장
- [ ] Canvas로 공유 카드 생성
- [ ] 갤러리 저장 기능
- [ ] 앱 로고/링크 포함

#### 9.4.2 SNS 공유
- [ ] Android ShareSheet 연동
- [ ] 카카오톡/인스타 최적화
- [ ] 딥링크 지원

---

### 출시 준비 체크리스트

#### 기술
- [ ] Firebase Crashlytics
- [ ] Firebase Analytics
- [ ] ProGuard 설정
- [ ] Release 키스토어

#### 스토어
- [ ] 앱 아이콘 (512x512)
- [ ] 피처 그래픽 (1024x500)
- [ ] 스크린샷 (최소 2장)
- [ ] 앱 설명 작성
- [ ] 개인정보처리방침 URL

---

### 버전 계획

| 버전 | 포함 기능 | 목표 |
|------|----------|------|
| v1.0 | Phase 1 + 출시 준비 | 스토어 출시 |
| v1.1 | Phase 2 + Phase 3 | 콘텐츠 & 몰입감 |
| v1.2 | Phase 4 | 공유 & 바이럴 |
| v2.0 | 소셜 기능, 수익화 | 성장 |

---

## 📋 우선순위 정리

### Phase 1: 즉시 (임팩트 높음)
| 순서 | 태스크 | 이유 |
|------|--------|------|
| 1 | 별 배경 시스템 | 전체 분위기 결정 |
| 2 | Opening Lottie | 첫인상 |
| 3 | 문 선택 애니메이션 | 핵심 인터랙션 |
| 4 | 수정구슬 터치 효과 | 메인 기능 강화 |

### Phase 2: 단기
| 순서 | 태스크 | 이유 |
|------|--------|------|
| 5 | 탐험 진행도 | 재방문 유도 |
| 6 | OWNER_HOME 파티클 | 특별함 강조 |
| 7 | Hall 레이아웃 개선 | 탐험 욕구 |
| 8 | 온보딩 개선 | 초기 경험 |

### Phase 3: 중기
| 순서 | 태스크 | 이유 |
|------|--------|------|
| 9 | UseCase 계층 | 코드 품질 |
| 10 | 에러 핸들링 | 안정성 |
| 11 | 스와이프 네비게이션 | 편의성 |
| 12 | 사운드 시스템 | 몰입감 완성 |

---

## 기술적 참고사항

### 파티클 시스템 구현 방향
```kotlin
@Composable
fun ParticleSystem(
    particleCount: Int,
    color: Color,
    emitPosition: Offset,
    type: ParticleType // EXPLOSION, CONTINUOUS, RIPPLE
)
```

### Lottie 파일 필요 목록
- `raw/book_opening.json` - 황금 책 열림
- `raw/door_glow.json` - 문 빛 효과 (선택적)
- `raw/celebration.json` - 축하 효과

### 색상 팔레트 활용
- 별 배경: `Gold.copy(alpha = 0.3f ~ 0.8f)`
- 파티클: 각 행성 색상 활용
- 빛 효과: `OwnerGlow`, `TenantGlow`

---

## 코드 리뷰 발견사항

### 잘 된 점 ✅
1. Clean Architecture 구조 준수
2. StateFlow/SharedFlow 올바른 사용
3. Hilt DI 깔끔한 구성
4. 도메인 모델 명확한 정의
5. Material3 테마 적절한 활용

### 개선 필요 ⚠️
1. **에러 핸들링**: try-catch만 있음 → Result sealed class 필요
2. **UseCase 없음**: Repository가 비즈니스 로직 직접 처리
3. **테스트 코드 없음**: 단위 테스트 필요
4. **애니메이션 단순**: 펄스만 있음, 인터랙티브 효과 부족
5. **신비로운 분위기 부족**: 텍스트 기반, 시각 효과 미흡

### 현재 화면별 상태

| 화면 | 현재 | 목표 |
|------|------|------|
| Opening | 텍스트 + ✦ 페이드인 | Lottie 황금 책 + 별 배경 |
| Onboarding | 일반 폼 | 마법 주문 입력 느낌 |
| Hall | 정적 3x4 그리드 | 빛나는 문 + 탐험 진행도 |
| HouseRoom | 펄스 애니메이션만 | 터치 반응 + 파티클 |

---

## 다음 작업 시작점

**추천 시작:** 5.1 별 배경 시스템

이유:
1. 모든 화면에 적용되어 일관된 분위기 형성
2. 한 번 만들면 재사용 가능
3. 구현 난이도 중간
4. 시각적 임팩트 큼
