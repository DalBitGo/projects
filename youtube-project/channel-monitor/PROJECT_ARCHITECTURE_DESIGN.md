# YouTube 채널 모니터링 프로젝트 - 아키텍처 설계

## 1. 프로젝트 목표 및 범위

### 1.1 핵심 목표
- **채널 모니터링**: 10개 YouTube 채널의 새로운 영상 업로드 감지
- **실시간 알림**: 새 영상 업로드 시 즉시 알림 전송
- **데이터 수집**: 영상 메타데이터 및 통계 저장
- **효율성**: 일일 API 할당량 10,000 units 내에서 운영

### 1.2 범위 정의

**포함 기능:**
- 채널별 최신 영상 모니터링
- 새 영상 감지 (이전 확인 시점 대비)
- 영상 메타데이터 저장 (제목, 설명, 조회수, 좋아요 등)
- 알림 전송 (이메일, 웹훅, 또는 CLI 출력)
- 모니터링 히스토리 추적

**제외 기능 (1차 버전):**
- 댓글 수집 및 분석
- 감정 분석
- 고급 통계 분석
- 대시보드 시각화

### 1.3 성능 요구사항

**API 할당량 계산:**
```
10개 채널 × 1시간마다 확인 × 24시간 = 240 API calls/day
채널 정보: 240 units
최신 영상 (50개씩): 240 units
영상 상세: 240 units
---
총계: ~720 units/day (10,000 units의 7.2%)
```

**모니터링 주기:**
- 기본: 1시간마다 확인
- 커스터마이즈 가능: 채널별 다른 주기 설정

**응답 시간:**
- 새 영상 감지 후 5분 이내 알림
- 전체 모니터링 사이클: 10분 이내 완료

---

## 2. 시스템 아키텍처

### 2.1 아키텍처 결정: Airflow vs 간단한 스크립트

#### Option A: Apache Airflow (JensBender 방식)
**장점:**
- 강력한 스케줄링 및 재시도 메커니즘
- 웹 UI를 통한 모니터링
- 태스크 의존성 관리
- 로그 및 히스토리 추적
- 확장 가능

**단점:**
- 복잡한 설정 (Docker, 데이터베이스 필요)
- 리소스 오버헤드 (메모리, CPU)
- 학습 곡선
- 10개 채널 모니터링에는 과도한 인프라

#### Option B: 경량 Python 스크립트 + Cron/Systemd Timer (권장)
**장점:**
- 빠른 구현 및 배포
- 최소한의 리소스 사용
- 유지보수 간단
- 현재 요구사항에 적합

**단점:**
- 수동으로 스케줄링 설정 (cron)
- 제한적인 모니터링 UI
- 복잡한 워크플로우 관리 어려움

**최종 선택: Option B (단계적 확장 가능)**
- 1단계: 간단한 Python 스크립트
- 2단계: 필요시 Airflow로 마이그레이션

### 2.2 시스템 구성 다이어그램

```
┌─────────────────────────────────────────────────────────────┐
│                     Cron Scheduler                          │
│                (Every hour: 0 * * * *)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 Channel Monitor Script                      │
│                                                             │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐         │
│  │  Extractor │──▶│ Comparator │──▶│  Notifier  │         │
│  └────────────┘   └────────────┘   └────────────┘         │
│         │                 │                  │              │
└─────────┼─────────────────┼──────────────────┼──────────────┘
          │                 │                  │
          ▼                 ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ YouTube API  │   │   SQLite DB  │   │ Notification │
│   (Read)     │   │  (Read/Write)│   │   Service    │
└──────────────┘   └──────────────┘   └──────────────┘
```

### 2.3 컴포넌트 설계

#### 2.3.1 Extractor (데이터 추출)
**책임:**
- YouTube API 호출
- 채널 정보 조회
- 최신 영상 목록 조회
- 영상 상세 정보 조회
- API 할당량 추적

**주요 메서드:**
```python
class YouTubeExtractor:
    def get_channel_info(channel_id: str) -> ChannelInfo
    def get_latest_videos(channel_id: str, limit: int = 10) -> List[Video]
    def get_video_details(video_ids: List[str]) -> List[VideoDetails]
```

#### 2.3.2 Comparator (변경 감지)
**책임:**
- 데이터베이스에서 마지막 확인 시점 조회
- 새로운 영상 식별
- 영상 통계 변화 추적 (옵션)

**주요 메서드:**
```python
class ChangeDetector:
    def get_last_check_time(channel_id: str) -> datetime
    def find_new_videos(channel_id: str, videos: List[Video]) -> List[Video]
    def update_last_check_time(channel_id: str, time: datetime) -> None
```

#### 2.3.3 Notifier (알림 전송)
**책임:**
- 새 영상 알림 포맷팅
- 알림 전송 (이메일, 웹훅, CLI)
- 알림 히스토리 저장

**주요 메서드:**
```python
class Notifier:
    def send_notification(video: Video, channel: Channel) -> bool
    def format_notification(video: Video) -> str
    def log_notification(video: Video, success: bool) -> None
```

---

## 3. 데이터베이스 설계

### 3.1 데이터베이스 선택: SQLite vs MySQL

**SQLite 선택 이유:**
- 10개 채널 규모에 충분
- 설치 불필요 (파일 기반)
- 빠른 읽기/쓰기
- 백업 간단 (파일 복사)
- 필요시 MySQL/PostgreSQL로 마이그레이션 가능

### 3.2 데이터베이스 스키마

```sql
-- 채널 정보
CREATE TABLE channels (
    channel_id VARCHAR(255) PRIMARY KEY,
    channel_name VARCHAR(255) NOT NULL,
    channel_handle VARCHAR(255),
    subscribers INTEGER,
    total_videos INTEGER,
    total_views INTEGER,
    thumbnail_url TEXT,
    monitor_enabled BOOLEAN DEFAULT TRUE,
    check_interval_minutes INTEGER DEFAULT 60,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 영상 정보
CREATE TABLE videos (
    video_id VARCHAR(255) PRIMARY KEY,
    channel_id VARCHAR(255) NOT NULL,
    video_title TEXT NOT NULL,
    video_description TEXT,
    published_at TIMESTAMP NOT NULL,
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    video_duration INTEGER,  -- seconds
    views INTEGER,
    likes INTEGER,
    comments_count INTEGER,
    thumbnail_url TEXT,
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE
);

-- 영상 통계 히스토리 (옵션 - 시간별 변화 추적)
CREATE TABLE video_stats_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id VARCHAR(255) NOT NULL,
    views INTEGER,
    likes INTEGER,
    comments_count INTEGER,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE
);

-- 모니터링 로그
CREATE TABLE monitor_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id VARCHAR(255) NOT NULL,
    check_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    new_videos_count INTEGER DEFAULT 0,
    api_units_used INTEGER,
    status VARCHAR(50),  -- success, error, quota_exceeded
    error_message TEXT,
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE
);

-- 알림 히스토리
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id VARCHAR(255) NOT NULL,
    notification_type VARCHAR(50),  -- email, webhook, cli
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN,
    error_message TEXT,
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE
);

-- 인덱스 생성
CREATE INDEX idx_videos_published_at ON videos(published_at DESC);
CREATE INDEX idx_videos_channel_id ON videos(channel_id);
CREATE INDEX idx_monitor_logs_check_time ON monitor_logs(check_time DESC);
CREATE INDEX idx_notifications_sent_at ON notifications(sent_at DESC);
```

### 3.3 JensBender와의 차이점

| 항목 | JensBender | 우리 프로젝트 |
|------|------------|---------------|
| **데이터베이스** | MySQL (AWS RDS) | SQLite (로컬 파일) |
| **테이블 전략** | 매번 DROP/CREATE | INSERT 기반 (증분 업데이트) |
| **댓글 테이블** | 있음 (대용량) | 없음 (1차 버전) |
| **히스토리 추적** | 없음 | monitor_logs, notifications 추가 |
| **모니터링 설정** | 하드코딩 | channels 테이블에 설정 저장 |

---

## 4. YouTube API 최적화 전략

### 4.1 JensBender에서 배운 패턴 적용

#### 4.1.1 페이지네이션 패턴
```python
def get_latest_videos(channel_id: str, limit: int = 10) -> List[Video]:
    """최신 영상 조회 (페이지네이션)"""
    videos = []
    next_page_token = None

    while len(videos) < limit:
        response = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=min(50, limit - len(videos)),
            pageToken=next_page_token
        ).execute()

        videos.extend(response['items'])

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return videos[:limit]
```

#### 4.1.2 배치 비디오 조회
```python
def get_video_details_batch(video_ids: List[str]) -> List[VideoDetails]:
    """영상 상세 정보 배치 조회 (최대 50개씩)"""
    all_details = []

    # 50개씩 청크로 나누기
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]

        response = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(chunk)
        ).execute()

        all_details.extend(response['items'])

    return all_details
```

#### 4.1.3 썸네일 폴백 패턴
```python
def get_thumbnail_url(thumbnails: dict) -> str:
    """썸네일 URL 추출 (폴백 포함)"""
    try:
        return thumbnails['maxres']['url']
    except KeyError:
        try:
            return thumbnails['high']['url']
        except KeyError:
            return thumbnails['default']['url']
```

### 4.2 API 할당량 추적

```python
class QuotaTracker:
    """API 할당량 추적"""

    # API 비용 상수
    COST_CHANNEL_INFO = 1
    COST_PLAYLIST_ITEMS = 1
    COST_VIDEO_DETAILS = 1

    def __init__(self, daily_limit: int = 10000):
        self.daily_limit = daily_limit
        self.used_units = 0
        self.reset_date = date.today()

    def check_quota(self, units_needed: int) -> bool:
        """할당량 체크"""
        if date.today() > self.reset_date:
            self.reset()

        return (self.used_units + units_needed) <= self.daily_limit

    def consume(self, units: int) -> None:
        """할당량 사용"""
        self.used_units += units
        logger.info(f"Used {units} units. Total: {self.used_units}/{self.daily_limit}")

    def reset(self) -> None:
        """일일 할당량 리셋"""
        self.used_units = 0
        self.reset_date = date.today()
        logger.info("Quota reset for new day")
```

### 4.3 API 호출 최적화

**최소 호출 전략:**
```python
def monitor_channel(channel_id: str, last_check_time: datetime) -> List[Video]:
    """채널 모니터링 (최적화)"""

    # 1. 최신 10개 영상만 조회 (1 unit)
    latest_videos = get_latest_videos(channel_id, limit=10)

    # 2. 마지막 확인 이후 영상만 필터링
    new_videos = [v for v in latest_videos
                  if v.published_at > last_check_time]

    if not new_videos:
        return []

    # 3. 새 영상만 상세 정보 조회 (1 unit)
    video_ids = [v.video_id for v in new_videos]
    video_details = get_video_details_batch(video_ids)

    # 총 비용: 2 units (채널당)
    return video_details
```

---

## 5. 에러 처리 및 재시도 전략

### 5.1 JensBender 패턴 적용

#### 5.1.1 Exponential Backoff
```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=2, max=10),
    retry=retry_if_exception_type(HttpError)
)
def api_call_with_retry(func):
    """API 호출 재시도 래퍼"""
    return func()
```

#### 5.1.2 Graceful Degradation
```python
def monitor_all_channels():
    """모든 채널 모니터링 (실패해도 계속 진행)"""
    results = []

    for channel in get_active_channels():
        try:
            new_videos = monitor_channel(channel.channel_id,
                                          channel.last_check_time)
            results.append({
                'channel': channel,
                'new_videos': new_videos,
                'status': 'success'
            })
        except QuotaExceeded:
            logger.error(f"Quota exceeded for {channel.channel_name}")
            results.append({
                'channel': channel,
                'status': 'quota_exceeded'
            })
            break  # 할당량 초과시 중단
        except Exception as e:
            logger.error(f"Failed to monitor {channel.channel_name}: {e}")
            results.append({
                'channel': channel,
                'status': 'error',
                'error': str(e)
            })
            # 다음 채널 계속 진행

    return results
```

### 5.2 에러 타입별 처리

```python
from googleapiclient.errors import HttpError

def handle_api_error(error: HttpError) -> str:
    """API 에러 처리"""
    if error.resp.status == 403:
        # 할당량 초과 또는 권한 문제
        if 'quota' in str(error).lower():
            return 'quota_exceeded'
        else:
            return 'permission_denied'
    elif error.resp.status == 404:
        return 'not_found'
    elif error.resp.status >= 500:
        return 'server_error'
    else:
        return 'unknown_error'
```

---

## 6. 프로젝트 구조

### 6.1 디렉토리 구조

```
channel-monitor/
├── src/
│   ├── __init__.py
│   ├── extractor.py          # YouTube API 호출
│   ├── detector.py            # 변경 감지
│   ├── notifier.py            # 알림 전송
│   ├── database.py            # 데이터베이스 작업
│   ├── models.py              # 데이터 모델
│   └── utils.py               # 유틸리티 함수
├── scripts/
│   └── monitor.py             # 메인 실행 스크립트
├── config/
│   ├── channels.yaml          # 채널 목록 설정
│   └── config.yaml            # 전역 설정
├── data/
│   ├── monitor.db             # SQLite 데이터베이스
│   └── logs/                  # 로그 파일
├── tests/
│   ├── test_extractor.py
│   ├── test_detector.py
│   └── test_notifier.py
├── docs/
│   ├── API_RESEARCH.md
│   ├── ANALYSIS_JensBender_ETL.md
│   └── PROJECT_ARCHITECTURE_DESIGN.md
├── .env.example               # 환경 변수 예시
├── requirements.txt           # Python 의존성
├── setup.sh                   # 초기 설정 스크립트
└── README.md                  # 프로젝트 소개
```

### 6.2 설정 파일 예시

**config/channels.yaml:**
```yaml
channels:
  - id: "UCX6OQ3DkcsbYNE6H8uQQuVA"
    name: "MrBeast"
    handle: "mrbeast"
    check_interval_minutes: 60
    enabled: true

  - id: "UC-lHJZR3Gqxm24_Vd_AJ5Yw"
    name: "PewDiePie"
    handle: "pewdiepie"
    check_interval_minutes: 30
    enabled: true
```

**config/config.yaml:**
```yaml
youtube:
  api_key: ${YOUTUBE_API_KEY}
  quota_limit: 10000

database:
  path: "data/monitor.db"

notifications:
  enabled: true
  types:
    - cli
    - email

  email:
    smtp_host: "smtp.gmail.com"
    smtp_port: 587
    from_address: ${EMAIL_FROM}
    to_addresses:
      - ${EMAIL_TO}

logging:
  level: "INFO"
  file: "data/logs/monitor.log"
  rotation: "1 day"
  retention: "30 days"
```

---

## 7. 구현 계획

### 7.1 Phase 1: 최소 기능 구현 (MVP)

**목표:** 기본적인 채널 모니터링 및 알림

**Tasks:**
1. [ ] 프로젝트 구조 생성
2. [ ] SQLite 데이터베이스 스키마 구현
3. [ ] YouTube API Extractor 구현
   - [ ] 채널 정보 조회
   - [ ] 최신 영상 조회
   - [ ] 영상 상세 정보 조회
4. [ ] Change Detector 구현
   - [ ] 마지막 확인 시점 조회
   - [ ] 새 영상 식별
5. [ ] Notifier 구현 (CLI 출력)
6. [ ] 메인 스크립트 구현
7. [ ] Cron 설정
8. [ ] 테스트 및 디버깅

**예상 소요 시간:** 2-3일

### 7.2 Phase 2: 고급 기능 추가

**목표:** 알림 다양화, 설정 관리, 모니터링

**Tasks:**
1. [ ] 이메일 알림 추가
2. [ ] 웹훅 알림 추가 (Discord, Slack)
3. [ ] 설정 파일 (YAML) 지원
4. [ ] 할당량 추적 및 알림
5. [ ] 로깅 개선
6. [ ] 에러 처리 강화
7. [ ] 유닛 테스트 작성

**예상 소요 시간:** 2-3일

### 7.3 Phase 3: 확장 및 최적화

**목표:** 성능 최적화, 추가 기능

**Tasks:**
1. [ ] 영상 통계 히스토리 추적
2. [ ] 채널별 커스텀 설정
3. [ ] 웹 대시보드 (선택 사항)
4. [ ] Docker 컨테이너화
5. [ ] 성능 최적화
6. [ ] 문서화 완성

**예상 소요 시간:** 3-5일

---

## 8. 기술 스택

### 8.1 핵심 라이브러리

```python
# requirements.txt
google-api-python-client==2.108.0  # YouTube API 클라이언트
tenacity==8.2.3                     # 재시도 로직
pyyaml==6.0.1                       # 설정 파일 파싱
python-dotenv==1.0.0                # 환경 변수 관리
loguru==0.7.2                       # 로깅
sqlite3                             # 데이터베이스 (내장)

# 알림
smtplib                             # 이메일 (내장)
requests==2.31.0                    # 웹훅

# 개발 도구
pytest==7.4.3                       # 테스팅
pytest-cov==4.1.0                   # 커버리지
black==23.12.0                      # 코드 포맷팅
mypy==1.7.1                         # 타입 체킹
```

### 8.2 개발 환경

- **Python**: 3.10+
- **OS**: Linux (권장), macOS, Windows
- **스케줄러**: Cron (Linux/macOS) 또는 Task Scheduler (Windows)

---

## 9. JensBender 프로젝트와의 비교

| 항목 | JensBender | 우리 프로젝트 |
|------|------------|---------------|
| **목적** | 채널 분석 (BI) | 채널 모니터링 (알림) |
| **데이터 범위** | 전체 히스토리 | 최신 영상만 |
| **스케줄링** | Airflow (복잡) | Cron (간단) |
| **데이터베이스** | MySQL (AWS RDS) | SQLite (로컬) |
| **댓글 수집** | 있음 | 없음 |
| **감정 분석** | 있음 (RoBERTa) | 없음 |
| **시각화** | Power BI | 없음 (1차) |
| **API 비용** | ~500 units/run | ~22 units/run |
| **실행 주기** | 1일 1회 | 1시간 1회 |
| **실행 시간** | 45-85분 | 2-5분 |
| **인프라** | Docker + EC2 | 로컬 스크립트 |

---

## 10. 다음 단계

### 10.1 즉시 시작 가능
1. **프로젝트 초기화**
   ```bash
   mkdir -p src config data/logs tests docs scripts
   touch src/__init__.py
   ```

2. **데이터베이스 스키마 생성**
   ```bash
   sqlite3 data/monitor.db < schema.sql
   ```

3. **Extractor 프로토타입 작성**
   - YouTube API 연결 테스트
   - 채널 정보 조회 테스트
   - 영상 목록 조회 테스트

### 10.2 질문 사항
- 알림 방식 선호도? (CLI, 이메일, Discord, Slack)
- 모니터링할 채널 목록 확정?
- 실행 환경? (로컬 PC, 서버, 라즈베리파이)
- Phase 1 구현 시작?

---

## 부록: 코드 스니펫 모음

### A.1 ISO 8601 Duration 변환
```python
import re

def convert_iso8601_duration(duration: str) -> int:
    """ISO 8601 duration을 초 단위로 변환

    예시:
        PT15M33S -> 933
        PT1H30M -> 5400
        PT45S -> 45
    """
    time_extractor = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
    extracted = time_extractor.match(duration)

    if extracted:
        hours = int(extracted.group(1)) if extracted.group(1) else 0
        minutes = int(extracted.group(2)) if extracted.group(2) else 0
        seconds = int(extracted.group(3)) if extracted.group(3) else 0
        return hours * 3600 + minutes * 60 + seconds
    return 0
```

### A.2 Service 객체 싱글톤
```python
from googleapiclient.discovery import build
from typing import Optional

class YouTubeService:
    _instance: Optional['YouTubeService'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.service = build(
                'youtube',
                'v3',
                developerKey=os.getenv('YOUTUBE_API_KEY')
            )
        return cls._instance

    def get_service(self):
        return self.service
```

### A.3 데이터베이스 Context Manager
```python
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db_connection(db_path: str):
    """데이터베이스 연결 컨텍스트 매니저"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # dict-like access
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# 사용 예시
with get_db_connection('data/monitor.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM channels WHERE monitor_enabled = 1")
    channels = cursor.fetchall()
```
