# 개발 과정 및 기술 문서

## 📅 개발 타임라인

### Phase 1: 기초 설정 및 POC (2025-10-22)

#### 1.1 GCP 설정 및 OAuth 구성
- **목표**: YouTube Data API v3 및 Analytics API 사용 권한 획득
- **작업**:
  - GCP Console에서 프로젝트 생성
  - YouTube Data API v3, YouTube Analytics API 활성화
  - OAuth 동의 화면 구성 (테스트 모드)
  - OAuth 클라이언트 ID 생성 (데스크톱 앱)
  - `client_secrets.json` 다운로드 및 저장

- **이슈 해결**:
  - 문제: `403: access_denied` - "Google 인증 절차 완료하지 않음"
  - 해결: OAuth 동의 화면에 테스트 사용자 추가 (junhyun1202@gmail.com)

#### 1.2 인증 테스트
- **작업**:
  - `poc_scripts/poc_authenticate.py` 실행
  - account1 (박준현), account2 (세상발견 World Discovery) 인증 완료
  - `tokens/account1_token.json`, `tokens/account2_token.json` 생성

- **결과**:
  - ✅ 2개 계정 인증 성공
  - ✅ 토큰 파일 로컬 저장 완료

---

### Phase 2: 데이터베이스 및 수집 시스템 (2025-10-22)

#### 2.1 SQLite 데이터베이스 설계
- **파일**: `database/schema.py`
- **테이블 구조**:
  ```
  accounts (계정 정보)
  channels (채널 정보)
  videos (영상 정보)
  video_snapshots (영상 통계 스냅샷 - 시계열)
  video_analytics_daily (영상별 일일 Analytics)
  channel_analytics_daily (채널별 일일 Analytics)
  traffic_sources (트래픽 소스 - 핵심!)
  ```

- **설계 결정**:
  - 파일 기반 SQLite 사용 (간단, 로컬 우선)
  - snake_case 네이밍 규칙 (Python 표준)
  - 인덱스 추가로 쿼리 성능 최적화

#### 2.2 YouTube API Wrapper
- **파일**: `collectors/youtube_api.py`
- **주요 메서드**:
  - `get_my_channel()`: 내 채널 정보
  - `get_uploaded_videos()`: 업로드 플레이리스트에서 영상 ID 추출
  - `get_video_details()`: 영상 상세 정보 (배치 처리)
  - `get_channel_analytics()`: 채널 Analytics (일별)
  - `get_traffic_sources()`: 트래픽 소스 (알고리즘 파악 핵심!)
  - `get_video_analytics()`: 영상별 Analytics
  - `get_video_traffic_sources()`: 영상별 트래픽 소스

- **API 할당량 고려**:
  - 일일 할당량: 10,000 units
  - 영상 100개 제한으로 할당량 절약
  - 배치 처리로 API 호출 최소화

#### 2.3 데이터 수집 스크립트
- **파일**: `collectors/collect_all.py`
- **수집 항목**:
  - 채널 정보
  - 최근 100개 영상 정보
  - 최근 30일 채널 Analytics
  - 채널 전체 트래픽 소스
  - 최근 10개 영상 Analytics
  - 최근 5개 영상 트래픽 소스

- **실행 결과** (최초 수집):
  ```
  ✅ 2개 계정 수집 완료
  ✅ 2개 채널 (박준현, 세상발견 World Discovery)
  ✅ 74개 영상
  ✅ 30일 Analytics 데이터
  ✅ 12개 트래픽 소스
  ```

---

### Phase 3: 대시보드 MVP (2025-10-22)

#### 3.1 Streamlit 대시보드 기본 구조
- **파일**: `app/dashboard.py`
- **초기 구현**:
  - 페이지 설정 (wide layout)
  - 사이드바 (채널 선택, 기간 선택)
  - 핵심 지표 카드
  - 트래픽 소스 분석 (파이 차트)
  - 영상 목록
  - 일별 성과 추이

#### 3.2 발생한 에러 및 해결

**에러 1: ModuleNotFoundError: No module named 'plotly'**
- 원인: requirements.txt에 패키지 누락
- 해결: `pip install plotly pandas streamlit`

**에러 2: Port 8501/8502 already in use**
- 원인: 여러 Streamlit 인스턴스 중복 실행
- 해결: 포트 8503으로 이동, 기존 프로세스 종료

**에러 3: KeyError: 'day'**
- 원인: Analytics API는 'day' 반환, DB는 'date' 컬럼명 사용
- 해결: 코드에서 'date'로 통일

**에러 4: KeyError: 'estimatedMinutesWatched'**
- 원인: camelCase vs snake_case 불일치
- 해결: 모든 컬럼을 snake_case로 통일

**에러 5: 영상 목록이 안 보임**
- 원인: 최근 7일 내 업로드된 영상 0개 (마지막 업로드 2개월 전)
- 해결: 탭으로 "최근" / "전체" 분리, 전체 영상 100개 표시

---

### Phase 4: 인사이트 기능 고도화 (2025-10-22)

#### 4.1 액션 필요 섹션 구현
- **위치**: `app/dashboard.py` (섹션 2)
- **기능**:
  - 🚨 **긴급**: 조회수 급락 자동 감지 (평균 대비 -70% 이하 & 1,000회 미만)
  - ⚠️ **주의**: 좋아요율 저조 (평균 대비 -50%)
  - ✅ **성공**: 평균 대비 2배 이상 조회수 또는 좋아요율 1.5배

- **분석 로직**:
  - 최근 5개 영상 대상
  - 채널 전체 평균과 비교
  - 3개 컬럼으로 시각적 분류

- **이슈 해결**:
  - TypeError: tz-naive vs tz-aware datetime 충돌
  - 해결: `pd.Timestamp.now(tz='UTC')` 사용, timezone 명시적 처리

#### 4.2 성공 패턴 분석
- **위치**: `app/dashboard.py` (섹션 3-1)
- **기능**:
  - **성공 영상 vs 일반 영상 비교**:
    - 상위 20% (quantile 0.8) vs 나머지
    - 평균 조회수, 좋아요율, 영상 길이 비교
    - 자동 인사이트 생성 (긴 영상 vs 짧은 영상)

  - **최적 업로드 타이밍**:
    - 요일별 평균 조회수 분석
    - 시간대별 평균 조회수 분석
    - 최고/최저 요일 및 시간 하이라이트
    - 구체적 추천 생성 (예: "월요일 18시")

#### 4.3 영상별 상세 분석 페이지
- **파일**: `app/pages/video_analysis.py`
- **기능**:
  - 사이드바에서 채널 + 영상 선택
  - 영상 기본 정보 (조회수, 좋아요, 댓글, 길이)
  - 트래픽 소스 분석 (파이 차트 + 상세)
  - 채널 평균 대비 성과 비교 (% 차이 표시)
  - YouTube 바로가기 링크

- **추가 DB 함수**:
  - `get_video_traffic_source_summary()`: 특정 영상의 트래픽 소스 집계

---

## 🛠 기술 스택

### Backend
- **Python 3.x**
- **SQLite**: 파일 기반 데이터베이스
- **google-api-python-client**: YouTube API 클라이언트
- **google-auth-oauthlib**: OAuth 2.0 인증

### Frontend
- **Streamlit**: 대시보드 프레임워크
- **Plotly**: 인터랙티브 차트
- **Pandas**: 데이터 처리

### API
- **YouTube Data API v3**: 채널/영상 정보
- **YouTube Analytics API**: 트래픽 소스, 성과 지표

---

## 📊 데이터 흐름

```
1. OAuth 인증 (utils/auth.py)
   ↓
2. YouTube API 호출 (collectors/youtube_api.py)
   ↓
3. 데이터 저장 (database/operations.py → SQLite)
   ↓
4. 대시보드 조회 (app/dashboard.py)
   ↓
5. 데이터 분석 및 인사이트 생성
   ↓
6. 사용자에게 시각화 표시
```

---

## 🎯 핵심 설계 결정

### 1. 로컬 우선 (Local-first)
- SQLite 파일 기반 → 서버 불필요
- 토큰 파일 로컬 저장 → 보안
- Streamlit → 별도 프론트엔드 불필요

### 2. 알고리즘 선택 중심
- 트래픽 소스에서 `RELATED_VIDEO` 비율 추적
- 알고리즘 선택률을 핵심 지표로 표시
- 성공 패턴 분석으로 알고리즘 선택 조건 파악

### 3. 액션 가능한 인사이트
- "이 영상은 조회수가 10,000회입니다" (X)
- "이 영상은 평균 대비 -70%로 개선 필요" (O)
- 자동 추천 생성 (업로드 타이밍, 영상 길이 등)

### 4. 데이터 지연 고려
- Analytics API는 48시간 지연 → end_date를 2일 전으로 설정
- 최신 영상은 트래픽 소스 데이터가 없을 수 있음 → 안내 메시지 표시

---

## 🔄 현재 워크플로우

### 일일 데이터 수집 (권장)
```bash
# 매일 오전 9시 실행 (크론 or 작업 스케줄러)
python collectors/collect_all.py
```

### 대시보드 실행
```bash
streamlit run app/dashboard.py
# http://localhost:8501
```

### 데이터 흐름
1. 매일 수집 스크립트 실행
2. 채널 정보 + 최근 영상 + Analytics 수집
3. SQLite에 누적 저장
4. 대시보드에서 조회 → 캐싱(5분)

---

## 📈 성과 지표 (이 프로젝트의)

- **개발 기간**: 1일 (POC → MVP → 고도화)
- **총 코드**: ~2,000 라인
- **수집 데이터**: 74개 영상, 30일 Analytics
- **대시보드 페이지**: 2개 (메인 + 영상 상세)
- **자동 인사이트**: 6가지 (긴급/주의/성공/패턴/타이밍/비교)

---

## 🐛 알려진 제약사항

### API 할당량
- YouTube Data API v3: 일일 10,000 units
- 영상 100개 제한으로 대규모 채널 완전 분석 불가
- 해결: GCP에서 할당량 증가 요청 가능

### Analytics 데이터 지연
- 48시간 지연 → 최신 데이터 부정확
- 실시간 모니터링 불가

### 트래픽 소스 제한
- 영상별 트래픽 소스는 최근 5개만 수집
- 전체 영상 분석 불가 → API 할당량 고려

### 다중 채널 UI
- 현재 채널 간 비교 기능 없음
- 채널을 드롭다운에서 선택만 가능

---

## 💡 배운 점

1. **YouTube Analytics API의 강력함**
   - 트래픽 소스 데이터가 성장 최적화의 핵심
   - RELATED_VIDEO 비율로 알고리즘 선택 여부 파악 가능

2. **Streamlit의 효율성**
   - 별도 프론트엔드 없이 빠른 프로토타이핑
   - 캐싱으로 성능 최적화 용이
   - 멀티페이지 지원으로 확장 가능

3. **데이터 기반 인사이트의 중요성**
   - 단순 데이터 조회 → 액션 불가
   - 평균과 비교, 자동 분류 → 즉시 실행 가능

4. **OAuth 인증의 복잡성**
   - 테스트 모드에서는 사용자 추가 필수
   - 토큰 만료 처리 필요 (향후 개선)

