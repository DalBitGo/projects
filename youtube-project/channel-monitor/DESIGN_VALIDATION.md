# YouTube Intelligence - 설계 검증 문서

## 📋 목차
1. [전제 조건 확인](#1-전제-조건-확인)
2. [YouTube API 비교 분석](#2-youtube-api-비교-분석)
3. [실행 환경: 로컬 vs 클라우드](#3-실행-환경-로컬-vs-클라우드)
4. [OAuth 인증 구현](#4-oauth-인증-구현)
5. [데이터 수집 아키텍처](#5-데이터-수집-아키텍처)
6. [리스크 분석 및 완화 방안](#6-리스크-분석-및-완화-방안)
7. [POC 계획](#7-poc-계획)
8. [구현 로드맵](#8-구현-로드맵)

---

## 1. 전제 조건 확인

### ✅ 확정 사항

#### 1.1 채널 소유 구조
```
회사 소유 채널:
  ├── 계정1 (john@company.com)
  │     ├── 채널A (게임 메인)
  │     └── 채널B (게임 서브)
  │
  ├── 계정2 (jane@company.com)
  │     └── 채널C (먹방)
  │
  └── 계정3 (team@company.com)
        └── 채널D (브이로그)

총: 3개 계정, 4-10개 채널
```

**중요:** 모든 채널을 **우리가 소유**하고 있음 (로그인 가능)

#### 1.2 목적
- **주 목적**: 오전 9시 회의에서 우리 채널 성과 파악
- **핵심 질문**:
  1. 어제 올린 영상 성과는?
  2. 어떤 영상이 알고리즘에 선택됐나?
  3. 채널별 성과 비교는?

#### 1.3 실행 환경
- **로컬 PC에서 실행** (서버 불필요)
- SQLite (파일 기반 데이터베이스)
- Streamlit (로컬 대시보드)
- Windows 작업 스케줄러 또는 Cron (자동화)

---

## 2. YouTube API 비교 분석

### 2.1 API 종류

#### **YouTube Data API v3**
**용도:** 공개 정보 조회, 채널/영상 관리

**주요 기능:**
```
✅ 채널 정보 조회
  - 채널명, 구독자 수, 총 조회수, 영상 개수
  - 썸네일, 설명, 업로드 플레이리스트 ID

✅ 영상 목록 조회
  - 최근 업로드 영상 (playlistItems.list)
  - 영상 상세 정보 (videos.list)

✅ 영상 통계
  - 조회수, 좋아요, 댓글 수
  - 제목, 설명, 태그, 카테고리
  - 업로드 시간, 영상 길이

✅ 댓글 수집
  - 댓글 내용, 작성자, 작성 시간
  - 대댓글 지원

❌ 상세 Analytics 불가
  - 시청 유지율, 트래픽 소스 등
```

**할당량:**
- 일일 10,000 units (무료)
- 읽기: 1 unit, 쓰기: 50 units, 검색: 100 units

#### **YouTube Analytics API**
**용도:** 소유 채널의 상세 통계 분석 ⭐

**주요 기능:**
```
✅ 시청 패턴 분석
  - 총 시청 시간 (Watch time)
  - 평균 시청 시간 (Average view duration)
  - 시청 유지율 (Audience retention) ⭐⭐⭐
  - 클릭률 (CTR - Click-through rate)

✅ 트래픽 소스 분석 ⭐⭐⭐ (핵심!)
  - YouTube 검색
  - 추천 영상 (알고리즘!)
  - 외부 소스 (SNS, 블로그)
  - 직접 유입
  - 재생목록

✅ 인구통계
  - 연령대별 시청자 비율
  - 성별 분포
  - 국가/지역
  - 구독자 vs 비구독자

✅ 참여 메트릭
  - 구독자 증감
  - 좋아요/싫어요 비율
  - 댓글 참여율

✅ 수익 (선택적)
  - 예상 수익
  - RPM (1000회당 수익)
  - CPM (광고 단가)

❌ 개별 영상 메타데이터는 Data API가 나음
  - 제목, 설명, 태그 등
```

**할당량:**
- 더 관대함 (정확한 숫자는 문서화 안됨)
- 일반적으로 수만 건 쿼리 가능

**제약:**
- OAuth 인증 필수
- 소유 채널만 조회 가능
- 데이터 지연 가능 (최근 48시간은 부정확)

---

### 2.2 두 API 비교표

| 항목 | Data API v3 | Analytics API |
|------|-------------|---------------|
| **인증** | API Key 또는 OAuth | OAuth 필수 |
| **대상** | 모든 공개 채널 | 소유 채널만 |
| **조회수** | ✅ 기본 | ✅ 상세 |
| **시청 시간** | ❌ | ✅ |
| **시청 유지율** | ❌ | ✅ |
| **트래픽 소스** | ❌ | ✅ ⭐ |
| **인구통계** | ❌ | ✅ |
| **수익** | ❌ | ✅ |
| **영상 메타데이터** | ✅ ⭐ | ❌ |
| **댓글** | ✅ | ❌ |
| **실시간성** | 높음 | 낮음 (지연) |
| **할당량** | 10,000 units/day | 관대 |

---

### 2.3 우리 프로젝트 전략

**하이브리드 접근** ⭐ 추천

```python
# Step 1: Data API로 기본 정보 수집
채널 정보 = data_api.get_channel(channel_id)
영상 목록 = data_api.get_recent_videos(channel_id, limit=10)
영상 상세 = data_api.get_video_details(video_ids)

# Step 2: Analytics API로 상세 통계 수집
시청 통계 = analytics_api.get_watch_metrics(video_id)
트래픽 소스 = analytics_api.get_traffic_sources(video_id)
인구통계 = analytics_api.get_demographics(video_id)

# Step 3: 데이터 병합
완전한_데이터 = {
    **영상_상세,      # 제목, 설명, 태그 (Data API)
    **시청_통계,      # 시청시간, 유지율 (Analytics API)
    **트래픽_소스     # 알고리즘 분석! (Analytics API)
}
```

**장점:**
- ✅ 각 API의 강점 활용
- ✅ 완전한 데이터셋 구성
- ✅ 알고리즘 패턴 분석 가능

---

## 3. 실행 환경: 로컬 vs 클라우드

### 3.1 로컬 실행 (선택) ✅

#### 아키텍처
```
┌─────────────────────────────────────────┐
│  로컬 PC (Windows/Mac/Linux)             │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Python 스크립트                 │   │
│  │  - 데이터 수집                   │   │
│  │  - 분석                          │   │
│  │  - 대시보드                      │   │
│  └──────────┬──────────────────────┘   │
│             │                           │
│  ┌──────────▼──────────────────────┐   │
│  │  SQLite (intelligence.db)       │   │
│  │  - 파일 기반                     │   │
│  │  - 서버 불필요                   │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Streamlit                      │   │
│  │  - localhost:8501               │   │
│  │  - 브라우저에서 접속             │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
         │
         │ 인터넷 (API 호출만)
         ▼
┌─────────────────────────────────────────┐
│  YouTube API (Google)                   │
└─────────────────────────────────────────┘
```

#### 구성 요소
```
youtube-intelligence/
├── client_secrets.json      # OAuth 클라이언트 (GCP에서 다운로드)
├── tokens/
│   ├── account1_token.json  # 계정1 인증 토큰
│   ├── account2_token.json  # 계정2 인증 토큰
│   └── account3_token.json  # 계정3 인증 토큰
├── data/
│   ├── intelligence.db      # SQLite 데이터베이스
│   └── logs/                # 로그 파일
├── src/                     # 소스 코드
├── dashboards/              # Streamlit 대시보드
└── scripts/                 # 실행 스크립트
```

#### 자동화 (Windows)
```
작업 스케줄러:
  매일 오전 6시: collect_data.py 실행
  매일 오전 7시: analyze_trends.py 실행
  매일 오전 8시: generate_insights.py 실행

수동 실행:
  오전 9시 회의 전: streamlit run dashboards/Home.py
```

#### 장점
- ✅ **비용 0원** (서버 불필요)
- ✅ 간단한 설정
- ✅ 빠른 개발
- ✅ 데이터 완전 제어 (로컬 파일)
- ✅ 디버깅 쉬움

#### 단점
- ⚠️ PC가 꺼져있으면 수집 중단
- ⚠️ 팀원과 실시간 공유 어려움 (같은 PC 접속 필요)

---

### 3.2 Google Cloud Platform 역할

**오해하기 쉬운 점:**
- ❌ GCP 서버에서 코드 실행 (필요 없음!)
- ✅ GCP Console (관리 페이지)에서 API 등록만

**실제 사용:**
```
┌─────────────────────────────────────────┐
│  Google Cloud Console                   │
│  (웹 브라우저에서 1회 설정)              │
│                                         │
│  작업:                                  │
│  1. 프로젝트 생성                        │
│  2. YouTube API 활성화                  │
│  3. OAuth 클라이언트 생성               │
│  4. client_secrets.json 다운로드        │
│                                         │
│  비용: 무료                             │
│  시간: 10분                             │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  로컬 PC에 파일 복사                     │
│  → 이후 모든 코드는 로컬에서 실행!       │
└─────────────────────────────────────────┘
```

---

### 3.3 클라우드 배포 (선택 사항)

**필요한 경우:**
- PC를 항상 켜놓기 어려움
- 팀원들과 대시보드 실시간 공유

**옵션:**

#### Option A: Streamlit Cloud (무료)
```
- Streamlit 앱만 배포 (대시보드)
- 데이터 수집은 여전히 로컬
- 무료 (제한적)
```

#### Option B: 저렴한 VPS
```
- DigitalOcean, Lightsail 등
- 월 $5 정도
- 24/7 운영
```

#### Option C: 라즈베리파이
```
- 한 번 구입 (약 10만원)
- 전기료만 (월 1000원 정도)
- 24/7 운영
```

---

## 4. OAuth 인증 구현

### 4.1 OAuth 플로우

#### 초기 인증 (각 계정당 1회)
```
┌─────────────────────────────────────────┐
│  1. 로컬에서 스크립트 실행               │
│     python authenticate.py --account=1  │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│  2. 브라우저 자동 열림                   │
│     http://localhost:8080/authorize     │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│  3. Google 로그인                        │
│     (계정1: john@company.com)           │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│  4. 권한 승인 화면                       │
│     "YouTube Intelligence가              │
│      다음을 요청합니다:                  │
│      - YouTube 데이터 읽기               │
│      - Analytics 데이터 읽기"            │
│                                         │
│     [허용] [거부]                        │
└────────────┬────────────────────────────┘
             ▼ (허용 클릭)
┌─────────────────────────────────────────┐
│  5. 토큰 발급 및 저장                    │
│     tokens/account1_token.json 생성     │
│                                         │
│     내용:                               │
│     {                                   │
│       "access_token": "ya29.a0...",    │
│       "refresh_token": "1//0g...",     │
│       "expires_at": 1705334400         │
│     }                                   │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│  6. 완료!                               │
│     이후 자동으로 토큰 재사용            │
└─────────────────────────────────────────┘
```

#### 이후 자동 사용
```python
# 매번 실행 시
credentials = load_credentials('account1')

if credentials.expired:
    # Access Token 만료 (1시간)
    credentials.refresh()  # Refresh Token으로 자동 갱신
    save_credentials('account1', credentials)

# API 사용
youtube = build('youtube', 'v3', credentials=credentials)
analytics = build('youtubeAnalytics', 'v2', credentials=credentials)
```

---

### 4.2 토큰 관리 전략

#### 토큰 종류
```python
Access Token:
  - 유효기간: 1시간
  - API 호출에 사용
  - 만료 시 자동 갱신

Refresh Token:
  - 유효기간: 영구 (취소하지 않는 한)
  - Access Token 갱신에 사용
  - 한 번 받으면 계속 사용
```

#### 저장 구조
```json
// tokens/account1_token.json
{
  "token": "ya29.a0AfH6SMB...",           // Access Token
  "refresh_token": "1//0gOOO...",         // Refresh Token
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "XXX.apps.googleusercontent.com",
  "client_secret": "GOCSPX-XXX",
  "scopes": [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly"
  ],
  "expiry": "2024-01-15T12:00:00Z"
}
```

#### 갱신 로직
```python
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def get_credentials(account_name):
    """토큰 로드 및 자동 갱신"""
    token_path = f'tokens/{account_name}_token.json'

    # 토큰 로드
    credentials = Credentials.from_authorized_user_file(token_path)

    # 만료 확인 및 갱신
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

        # 갱신된 토큰 저장
        with open(token_path, 'w') as token_file:
            token_file.write(credentials.to_json())

    return credentials
```

---

### 4.3 에러 처리

#### 토큰 만료 시나리오
```python
try:
    credentials = get_credentials('account1')
    youtube = build('youtube', 'v3', credentials=credentials)
    response = youtube.channels().list(mine=True, part='snippet').execute()

except RefreshError:
    # Refresh Token도 만료 (드문 경우)
    logger.error("Refresh token expired. Need re-authentication.")
    send_notification("계정1 재인증 필요")

    # 재인증 필요
    # python authenticate.py --account=1

except HttpError as e:
    if e.resp.status == 401:
        # 인증 오류
        logger.error("Authentication failed")
    elif e.resp.status == 403:
        # 권한 오류 또는 할당량 초과
        logger.error("Permission denied or quota exceeded")
```

---

## 5. 데이터 수집 아키텍처

### 5.1 수집 계층

#### Layer 1: 기본 정보 (Data API)
```python
# 1시간마다 실행
def collect_basic_data(channel_id):
    """기본 채널/영상 정보 수집"""

    # 채널 정보
    channel = youtube.channels().list(
        part='snippet,statistics,contentDetails',
        id=channel_id
    ).execute()

    save_to_db('channels', channel)

    # 최신 영상 목록 (최근 10개)
    uploads_playlist_id = channel['contentDetails']['relatedPlaylists']['uploads']

    videos = youtube.playlistItems().list(
        part='snippet',
        playlistId=uploads_playlist_id,
        maxResults=10
    ).execute()

    video_ids = [item['snippet']['resourceId']['videoId']
                 for item in videos['items']]

    # 영상 상세 정보 (배치 조회)
    video_details = youtube.videos().list(
        part='snippet,statistics,contentDetails',
        id=','.join(video_ids)
    ).execute()

    save_to_db('videos', video_details)

    return video_ids
```

#### Layer 2: 상세 통계 (Analytics API)
```python
# 하루 1-2회 실행 (48시간 지난 데이터만)
def collect_analytics_data(channel_id, video_ids, date):
    """Analytics 상세 통계 수집"""

    analytics = build('youtubeAnalytics', 'v2', credentials=credentials)

    # 시청 메트릭
    watch_metrics = analytics.reports().query(
        ids=f'channel=={channel_id}',
        startDate=date,
        endDate=date,
        metrics='views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage',
        dimensions='video',
        filters=f'video=={",".join(video_ids)}'
    ).execute()

    save_to_db('video_analytics', watch_metrics)

    # 트래픽 소스 ⭐ 핵심!
    traffic_sources = analytics.reports().query(
        ids=f'channel=={channel_id}',
        startDate=date,
        endDate=date,
        metrics='views,estimatedMinutesWatched',
        dimensions='insightTrafficSourceType,video',
        filters=f'video=={",".join(video_ids)}'
    ).execute()

    save_to_db('traffic_sources', traffic_sources)

    # 인구통계 (선택적)
    demographics = analytics.reports().query(
        ids=f'channel=={channel_id}',
        startDate=date,
        endDate=date,
        metrics='views',
        dimensions='ageGroup,gender,video',
        filters=f'video=={",".join(video_ids)}'
    ).execute()

    save_to_db('demographics', demographics)
```

#### Layer 3: 시계열 스냅샷
```python
# 1시간마다 실행
def take_snapshot(video_ids):
    """조회수 증가율 계산용 스냅샷"""

    for video_id in video_ids:
        video = youtube.videos().list(
            part='statistics',
            id=video_id
        ).execute()

        stats = video['items'][0]['statistics']

        # 스냅샷 저장
        db.execute("""
            INSERT INTO video_stats_snapshots
                (video_id, views, likes, comments_count, snapshot_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            video_id,
            stats['viewCount'],
            stats['likeCount'],
            stats['commentCount'],
            datetime.now()
        ))

    # 증가율 계산
    calculate_growth_rate(video_ids)
```

---

### 5.2 데이터베이스 스키마 (최종)

```sql
-- 계정 정보
CREATE TABLE accounts (
    account_id VARCHAR(255) PRIMARY KEY,
    account_email VARCHAR(255) NOT NULL,
    account_name VARCHAR(255),
    token_path VARCHAR(500),
    last_auth_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 채널 정보
CREATE TABLE channels (
    channel_id VARCHAR(255) PRIMARY KEY,
    account_id VARCHAR(255) NOT NULL,
    channel_name VARCHAR(255) NOT NULL,
    channel_handle VARCHAR(255),

    -- 카테고리
    category VARCHAR(100),  -- 'gaming', 'food', 'vlog'

    -- 통계
    subscribers INTEGER,
    total_videos INTEGER,
    total_views INTEGER,

    -- 설정
    monitor_enabled BOOLEAN DEFAULT TRUE,

    -- 메타데이터
    thumbnail_url TEXT,
    description TEXT,
    uploads_playlist_id VARCHAR(255),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);

-- 영상 정보 (Data API)
CREATE TABLE videos (
    video_id VARCHAR(255) PRIMARY KEY,
    channel_id VARCHAR(255) NOT NULL,

    -- 기본 정보
    video_title TEXT NOT NULL,
    video_description TEXT,
    published_at TIMESTAMP NOT NULL,
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 메타데이터
    video_duration INTEGER,  -- seconds
    category_id VARCHAR(50),
    tags TEXT,  -- JSON array

    -- 통계 (스냅샷)
    views INTEGER,
    likes INTEGER,
    comments_count INTEGER,

    -- 미디어
    thumbnail_url TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE
);

-- 시계열 스냅샷 (증가율 계산용)
CREATE TABLE video_stats_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id VARCHAR(255) NOT NULL,

    -- 통계
    views INTEGER,
    likes INTEGER,
    comments_count INTEGER,

    -- 계산된 메트릭
    views_growth_1h REAL,      -- 1시간 증가율
    views_growth_24h REAL,     -- 24시간 증가율

    snapshot_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE
);

-- Analytics: 시청 메트릭
CREATE TABLE video_analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id VARCHAR(255) NOT NULL,

    -- 시청 메트릭
    watch_time_minutes INTEGER,
    average_view_duration INTEGER,        -- 초
    average_view_percentage REAL,         -- %

    -- 참여 메트릭
    ctr REAL,                             -- 클릭률 %
    subscribers_gained INTEGER,
    subscribers_lost INTEGER,

    -- 수익 (선택적)
    estimated_revenue REAL,
    estimated_rpm REAL,

    date DATE NOT NULL,

    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE,
    UNIQUE(video_id, date)
);

-- Analytics: 트래픽 소스 ⭐ 핵심!
CREATE TABLE traffic_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id VARCHAR(255) NOT NULL,

    -- 트래픽 유형
    source_type VARCHAR(100) NOT NULL,
    -- 'YT_SEARCH', 'RELATED_VIDEO', 'SUBSCRIBER',
    -- 'EXTERNAL', 'PLAYLIST', 'NOTIFICATION' 등

    -- 통계
    views INTEGER,
    watch_time_minutes INTEGER,

    date DATE NOT NULL,

    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE,
    UNIQUE(video_id, source_type, date)
);

-- Analytics: 인구통계 (선택적)
CREATE TABLE demographics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id VARCHAR(255) NOT NULL,

    -- 차원
    dimension VARCHAR(50) NOT NULL,        -- 'age', 'gender', 'country'
    dimension_value VARCHAR(100) NOT NULL, -- '18-24', 'male', 'US'

    -- 통계
    views INTEGER,
    watch_time_minutes INTEGER,

    date DATE NOT NULL,

    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE
);

-- 인덱스
CREATE INDEX idx_videos_channel ON videos(channel_id);
CREATE INDEX idx_videos_published ON videos(published_at DESC);
CREATE INDEX idx_snapshots_video_time ON video_stats_snapshots(video_id, snapshot_at DESC);
CREATE INDEX idx_analytics_video_date ON video_analytics(video_id, date DESC);
CREATE INDEX idx_traffic_video_date ON traffic_sources(video_id, date DESC);
```

---

## 6. 리스크 분석 및 완화 방안

### 6.1 기술적 리스크

#### Risk 1: OAuth 토큰 만료
**발생 확률:** 중간 (계정 비밀번호 변경 시)

**영향:**
- 데이터 수집 중단
- Analytics API 접근 불가

**완화 방안:**
```python
# 1. 자동 갱신 로직
if credentials.expired:
    credentials.refresh()

# 2. 에러 감지 및 알림
try:
    api_call()
except RefreshError:
    send_email_alert("계정1 재인증 필요")
    send_slack_notification("토큰 만료")

# 3. 대시보드에 상태 표시
"계정1: ✅ 정상"
"계정2: ⚠️ 재인증 필요"
```

---

#### Risk 2: API 할당량 초과
**발생 확률:** 낮음 (계산상 충분)

**예상 사용량:**
```
Data API (10개 채널, 1시간마다):
  - 채널 정보: 10 units
  - 영상 목록: 10 units
  - 영상 상세: 10 units
  ──────────────────────
  시간당: 30 units
  일일: 720 units (10,000 중 7.2%)

Analytics API:
  - 제한이 관대하여 문제 없을 것으로 예상
```

**완화 방안:**
```python
# 1. 할당량 추적
class QuotaTracker:
    def __init__(self):
        self.daily_limit = 10000
        self.used = 0

    def consume(self, units):
        self.used += units
        if self.used > self.daily_limit * 0.8:
            logger.warning(f"Quota 80% used: {self.used}/{self.daily_limit}")

# 2. 수집 빈도 조정
if quota_tracker.remaining() < 1000:
    # 2시간마다로 변경
    interval = 120  # minutes
```

---

#### Risk 3: Analytics API 데이터 지연
**발생 확률:** 높음 (정상 동작)

**영향:**
- 최근 48시간 데이터 부정확
- 실시간 분석 불가

**완화 방안:**
```python
# 1. 계층적 접근
실시간 (Data API):
  - 조회수, 좋아요 (1시간 지연)

상세 분석 (Analytics API):
  - 트래픽 소스, 시청 유지율 (48시간 후)

# 2. 대시보드 표시
"조회수: 15,000 (실시간)"
"트래픽 소스: 2일 전 데이터"
```

---

#### Risk 4: 채널 계정 변경
**발생 확률:** 낮음

**시나리오:**
- 계정 비밀번호 변경
- 2단계 인증 활성화
- 계정 이관

**완화 방안:**
```python
# 1. 에러 로깅
logger.error(f"Account {account_id} authentication failed")

# 2. 대시보드 알림
"⚠️ 계정2가 3일간 업데이트되지 않았습니다. 확인 필요."

# 3. 재인증 가이드
"설정 → 계정 관리 → 계정2 재인증"
```

---

### 6.2 운영 리스크

#### Risk 5: PC 전원 꺼짐
**발생 확률:** 중간

**영향:**
- 자동 수집 중단
- 데이터 공백

**완화 방안:**
```
Option 1: 항상 켜두기
Option 2: 라즈베리파이 (저전력 서버)
Option 3: 저렴한 VPS (월 $5)
```

---

#### Risk 6: YouTube API 정책 변경
**발생 확률:** 낮음 (1-2년 주기)

**완화 방안:**
```python
# 1. 버전 명시
youtube = build('youtube', 'v3')  # v3 고정
analytics = build('youtubeAnalytics', 'v2')  # v2 고정

# 2. 에러 처리
try:
    response = api_call()
except Exception as e:
    logger.error(f"API change detected: {e}")
    send_alert("API 정책 변경 확인 필요")
```

---

## 7. POC 계획

### 7.1 검증 목표

**핵심 질문:**
1. ✅ OAuth 인증이 실제로 작동하는가?
2. ✅ Analytics API로 트래픽 소스를 조회할 수 있는가?
3. ✅ 할당량이 충분한가?
4. ✅ 데이터 지연이 얼마나 되는가?

---

### 7.2 POC 스크립트

#### **poc_setup.py** (GCP 설정 체크리스트)
```python
"""
Google Cloud Console 설정 체크리스트
실행 전 수동으로 완료해야 할 항목들
"""

checklist = """
□ Google Cloud Console 접속
  https://console.cloud.google.com

□ 프로젝트 생성
  프로젝트 이름: YouTube Intelligence

□ YouTube Data API v3 활성화
  API 및 서비스 → 라이브러리 → 검색 → 활성화

□ YouTube Analytics API 활성화
  API 및 서비스 → 라이브러리 → 검색 → 활성화

□ OAuth 동의 화면 구성
  - 앱 이름: YouTube Intelligence
  - 사용자 지원 이메일: (본인 이메일)
  - 테스트 사용자 추가: (3개 계정 이메일)

□ OAuth 클라이언트 ID 생성
  - 애플리케이션 유형: 데스크톱 앱
  - 이름: Local App

□ client_secrets.json 다운로드
  - 프로젝트 폴더에 저장
  - 파일명 확인: client_secrets.json
"""

print(checklist)

# 파일 존재 확인
import os
if os.path.exists('client_secrets.json'):
    print("\n✅ client_secrets.json 파일 확인됨!")
    print("\n다음 단계: python poc_authenticate.py")
else:
    print("\n❌ client_secrets.json 파일이 없습니다.")
    print("위 체크리스트를 완료하고 파일을 다운로드하세요.")
```

#### **poc_authenticate.py** (OAuth 인증 테스트)
```python
"""
OAuth 인증 테스트
각 계정마다 실행 필요
"""

from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/yt-analytics.readonly'
]

def authenticate(account_name):
    """OAuth 인증 및 토큰 저장"""

    # OAuth 플로우 시작
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json',
        scopes=SCOPES
    )

    # 브라우저 열림 → 로그인 → 권한 승인
    credentials = flow.run_local_server(port=8080)

    # 토큰 저장
    os.makedirs('tokens', exist_ok=True)
    token_path = f'tokens/{account_name}_token.json'

    with open(token_path, 'w') as token_file:
        token_file.write(credentials.to_json())

    print(f"✅ {account_name} 인증 완료!")
    print(f"토큰 저장 위치: {token_path}")

    return credentials

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("사용법: python poc_authenticate.py <account_name>")
        print("예시: python poc_authenticate.py account1")
        sys.exit(1)

    account_name = sys.argv[1]

    print(f"\n🔐 {account_name} OAuth 인증 시작...")
    print("브라우저가 열리면 해당 계정으로 로그인하세요.\n")

    credentials = authenticate(account_name)

    print("\n✅ 인증 성공!")
    print(f"다음 단계: python poc_test_api.py {account_name}")
```

#### **poc_test_api.py** (API 테스트)
```python
"""
YouTube API 테스트
- Data API 조회
- Analytics API 조회
- 할당량 사용량 측정
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
from datetime import datetime, timedelta

def load_credentials(account_name):
    """저장된 토큰 로드"""
    token_path = f'tokens/{account_name}_token.json'
    return Credentials.from_authorized_user_file(token_path)

def test_data_api(credentials):
    """Data API 테스트"""
    print("\n" + "="*50)
    print("📊 YouTube Data API v3 테스트")
    print("="*50)

    youtube = build('youtube', 'v3', credentials=credentials)

    # 내 채널 정보
    response = youtube.channels().list(
        part='snippet,statistics,contentDetails',
        mine=True
    ).execute()

    if not response.get('items'):
        print("❌ 채널을 찾을 수 없습니다.")
        return None

    channel = response['items'][0]
    channel_id = channel['id']

    print(f"\n✅ 채널 정보:")
    print(f"   - 채널명: {channel['snippet']['title']}")
    print(f"   - 구독자: {channel['statistics']['subscriberCount']:,}")
    print(f"   - 총 조회수: {channel['statistics']['viewCount']:,}")
    print(f"   - 영상 수: {channel['statistics']['videoCount']:,}")

    # 최신 영상
    uploads_id = channel['contentDetails']['relatedPlaylists']['uploads']

    videos_response = youtube.playlistItems().list(
        part='snippet',
        playlistId=uploads_id,
        maxResults=5
    ).execute()

    print(f"\n✅ 최신 영상 5개:")
    for item in videos_response['items']:
        title = item['snippet']['title']
        published = item['snippet']['publishedAt']
        print(f"   - {title} ({published})")

    print(f"\n💰 할당량 사용: ~5 units")

    return channel_id

def test_analytics_api(credentials, channel_id):
    """Analytics API 테스트"""
    print("\n" + "="*50)
    print("📈 YouTube Analytics API 테스트")
    print("="*50)

    analytics = build('youtubeAnalytics', 'v2', credentials=credentials)

    # 날짜 설정 (최근 7일, 2일 전부터)
    end_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=9)).strftime('%Y-%m-%d')

    print(f"\n기간: {start_date} ~ {end_date}")

    # 1. 기본 메트릭
    try:
        basic_metrics = analytics.reports().query(
            ids=f'channel=={channel_id}',
            startDate=start_date,
            endDate=end_date,
            metrics='views,estimatedMinutesWatched,averageViewDuration',
            dimensions='day',
            sort='day'
        ).execute()

        print(f"\n✅ 기본 메트릭 조회 성공:")
        print(json.dumps(basic_metrics, indent=2))

    except Exception as e:
        print(f"❌ 기본 메트릭 조회 실패: {e}")

    # 2. 트래픽 소스 ⭐ 핵심!
    try:
        traffic = analytics.reports().query(
            ids=f'channel=={channel_id}',
            startDate=start_date,
            endDate=end_date,
            metrics='views,estimatedMinutesWatched',
            dimensions='insightTrafficSourceType',
            sort='-views'
        ).execute()

        print(f"\n✅ 트래픽 소스 조회 성공:")
        print(json.dumps(traffic, indent=2))

        # 트래픽 소스 해석
        if 'rows' in traffic:
            print(f"\n📊 트래픽 소스 분석:")
            for row in traffic['rows']:
                source = row[0]
                views = row[1]
                watch_time = row[2]
                print(f"   - {source}: {views:,} views, {watch_time:,} 분")

    except Exception as e:
        print(f"❌ 트래픽 소스 조회 실패: {e}")

    # 3. 영상별 메트릭
    try:
        video_metrics = analytics.reports().query(
            ids=f'channel=={channel_id}',
            startDate=start_date,
            endDate=end_date,
            metrics='views,likes,comments,shares',
            dimensions='video',
            sort='-views',
            maxResults=10
        ).execute()

        print(f"\n✅ 영상별 메트릭 조회 성공:")
        print(f"상위 10개 영상 데이터 확보")

    except Exception as e:
        print(f"❌ 영상별 메트릭 조회 실패: {e}")

def main(account_name):
    print(f"\n🧪 POC 테스트 시작: {account_name}")
    print("="*50)

    # 1. 토큰 로드
    print("\n1️⃣ 토큰 로드 중...")
    credentials = load_credentials(account_name)
    print("✅ 토큰 로드 완료")

    # 2. Data API 테스트
    print("\n2️⃣ Data API 테스트 중...")
    channel_id = test_data_api(credentials)

    if not channel_id:
        print("\n❌ 채널 ID를 가져올 수 없어 Analytics API 테스트를 건너뜁니다.")
        return

    # 3. Analytics API 테스트
    print("\n3️⃣ Analytics API 테스트 중...")
    test_analytics_api(credentials, channel_id)

    print("\n" + "="*50)
    print("✅ POC 테스트 완료!")
    print("="*50)

    print(f"\n💡 결과:")
    print("   - OAuth 인증: ✅")
    print("   - Data API: ✅")
    print("   - Analytics API: (위 결과 확인)")
    print("   - 트래픽 소스 조회: (위 결과 확인)")

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("사용법: python poc_test_api.py <account_name>")
        print("예시: python poc_test_api.py account1")
        sys.exit(1)

    account_name = sys.argv[1]
    main(account_name)
```

---

### 7.3 POC 실행 순서

```bash
# Step 0: 환경 설정
pip install google-auth google-auth-oauthlib google-api-python-client

# Step 1: GCP 설정 체크
python poc_setup.py

# Step 2: 계정1 인증
python poc_authenticate.py account1
# → 브라우저 열림 → 로그인 → 승인

# Step 3: 계정1 API 테스트
python poc_test_api.py account1
# → 실제 데이터 확인!

# Step 4: 계정2, 3 반복
python poc_authenticate.py account2
python poc_test_api.py account2

python poc_authenticate.py account3
python poc_test_api.py account3

# Step 5: 결과 분석
# → 트래픽 소스 데이터 확보 확인
# → 설계 최종 확정
```

---

## 8. 구현 로드맵

### Phase 0: 검증 (2-3일)
```
□ GCP 설정
□ OAuth 인증 (3개 계정)
□ POC 실행
□ Analytics API 트래픽 소스 확인
□ 설계 최종 확정
```

### Phase 1: 데이터 수집 (3-4일)
```
□ 데이터베이스 스키마 구현
□ YouTube API Wrapper 구현
  - Data API (채널, 영상, 통계)
  - Analytics API (트래픽 소스, 시청 메트릭)
□ 토큰 관리 시스템
□ 수집 스크립트 작성
□ 스케줄러 설정 (Cron/작업 스케줄러)
□ 테스트 (1-2개 채널로)
```

### Phase 2: 대시보드 A (3-4일)
```
□ Streamlit 기본 레이아웃
□ 사이드바 네비게이션
□ 전체 현황 페이지
  - KPI 카드
  - 전체 추이 그래프
  - 채널별 성과 카드
□ 채널 상세 페이지
  - 채널 KPI
  - 시청 통계
  - 트래픽 소스 분석 ⭐
  - 급상승 영상 리스트
□ 필터 및 날짜 선택
```

### Phase 3: 고도화 (1주)
```
□ 인사이트 자동 생성
  - "채널A 추천 알고리즘 선택률 증가"
  - "영상B 검색 유입 70% (SEO 성공)"
□ 알림 기능
  - 이메일, Discord, Slack
□ 성능 최적화
  - 쿼리 최적화
  - 캐싱
□ 에러 처리 강화
□ 문서화
□ 배포 (선택)
```

---

## 9. 성공 기준

### POC 성공 기준
- [ ] OAuth 인증 3개 계정 모두 성공
- [ ] Analytics API 트래픽 소스 데이터 조회 가능
- [ ] 트래픽 소스에 'YT_SEARCH', 'RELATED_VIDEO' 등 구분 확인
- [ ] 할당량 사용량 측정 (예상 범위 내)

### Phase 1 성공 기준
- [ ] 10개 채널 데이터 자동 수집
- [ ] 시계열 스냅샷 정상 저장
- [ ] Analytics 데이터 정상 저장
- [ ] 에러 없이 24시간 연속 실행

### Phase 2 성공 기준
- [ ] 대시보드 접속 시 5초 내 로딩
- [ ] 전체 현황 → 채널 상세 전환 매끄러움
- [ ] 트래픽 소스 차트 정상 표시
- [ ] 모바일에서도 사용 가능

### 최종 성공 기준
- [ ] 오전 9시 회의에서 실제 사용
- [ ] 팀원 피드백 긍정적
- [ ] "알고리즘 선택 패턴" 인사이트 발견
- [ ] 데이터 기반 의사결정 사례 1개 이상

---

## 10. 다음 단계

### 즉시 실행 가능
1. **GCP 설정** (10분)
   - Google Cloud Console 접속
   - 프로젝트 생성, API 활성화
   - OAuth 클라이언트 생성
   - client_secrets.json 다운로드

2. **POC 실행** (30분)
   ```bash
   pip install google-auth google-auth-oauthlib google-api-python-client
   python poc_setup.py
   python poc_authenticate.py account1
   python poc_test_api.py account1
   ```

3. **결과 확인 및 설계 확정** (1시간)
   - 트래픽 소스 데이터 확인
   - Analytics API 응답 형식 파악
   - 최종 데이터베이스 스키마 확정

---

## 부록

### A. 용어 정리

**OAuth (Open Authorization):**
- 사용자를 대신하여 API 접근 권한을 얻는 표준 프로토콜
- 비밀번호 공유 없이 권한 부여

**Access Token:**
- API 호출에 사용하는 인증 토큰
- 유효기간: 1시간
- 만료 시 Refresh Token으로 갱신

**Refresh Token:**
- Access Token 갱신용 토큰
- 유효기간: 영구 (취소 전까지)

**API 할당량 (Quota):**
- YouTube Data API: 일일 10,000 units
- 각 API 호출마다 unit 소비
- 초과 시 다음날까지 대기

**트래픽 소스 (Traffic Source):**
- 시청자가 영상을 발견한 경로
- 예: YouTube 검색, 추천 영상, 외부 링크 등
- 알고리즘 분석의 핵심 지표

---

### B. 참고 링크

**YouTube API 문서:**
- Data API v3: https://developers.google.com/youtube/v3
- Analytics API: https://developers.google.com/youtube/analytics
- OAuth 가이드: https://developers.google.com/identity/protocols/oauth2

**Google Cloud Console:**
- https://console.cloud.google.com

**Python 라이브러리:**
- google-api-python-client: https://github.com/googleapis/google-api-python-client
- google-auth: https://google-auth.readthedocs.io

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|-----------|
| 2024-01-15 | 1.0 | 초안 작성 |
