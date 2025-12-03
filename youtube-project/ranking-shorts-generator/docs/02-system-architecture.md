# 시스템 아키텍처 설계

## 1. 전체 시스템 개요

### 1.1 아키텍처 패턴
**3-Tier Architecture** (프레젠테이션 - 비즈니스 로직 - 데이터)

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                      │
│                  (React.js Web Frontend)                    │
│  - 검색 UI                                                   │
│  - 영상 선택 UI                                              │
│  - 미리보기 & 검수 UI                                        │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API (HTTP/WebSocket)
┌────────────────────▼────────────────────────────────────────┐
│                   Application Layer                         │
│              (Flask/FastAPI Backend Server)                 │
│  - API 엔드포인트                                            │
│  - 비즈니스 로직                                             │
│  - 작업 큐 관리                                              │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──────┐ ┌──▼───────┐ ┌─▼──────────────┐
│ Data Layer   │ │ External │ │ Processing     │
│              │ │ Services │ │ Layer          │
│ - SQLite DB  │ │          │ │                │
│ - File Store │ │ - TikTok │ │ - Video        │
│              │ │   API    │ │   Download     │
│              │ │          │ │ - FFmpeg       │
│              │ │          │ │   Processing   │
└──────────────┘ └──────────┘ └────────────────┘
```

### 1.2 주요 컴포넌트

| 컴포넌트 | 기술 스택 | 역할 |
|---------|----------|------|
| **Frontend** | React.js + Vite | 사용자 인터페이스 |
| **Backend API** | FastAPI (Python) | REST API 서버 |
| **Task Queue** | Celery + Redis | 비동기 작업 처리 |
| **Database** | SQLite | 메타데이터 저장 |
| **Video Processor** | FFmpeg + MoviePy | 영상 편집 |
| **Scraper** | TikTokApi | 콘텐츠 수집 |
| **File Storage** | Local Filesystem | 영상 파일 저장 |

---

## 2. 상세 컴포넌트 설계

### 2.1 Frontend (프레젠테이션 계층)

#### 2.1.1 기술 스택
- **Framework**: React.js 18+
- **Build Tool**: Vite
- **UI Library**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand 또는 React Query
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **WebSocket**: Socket.IO Client (실시간 진행 상황)

#### 2.1.2 페이지 구조
```
/                       → 홈 페이지 (프로젝트 목록)
/search                 → 영상 검색 페이지
/select/:searchId       → 영상 선택 페이지
/generate/:projectId    → 영상 생성 진행 페이지
/preview/:videoId       → 미리보기 & 검수 페이지
/library                → 완성된 영상 라이브러리
/settings               → 설정 페이지
```

#### 2.1.3 주요 컴포넌트
```
src/
├── components/
│   ├── SearchBar.jsx           # 검색 입력
│   ├── VideoCard.jsx            # 영상 카드
│   ├── VideoGrid.jsx            # 영상 그리드
│   ├── DragDropList.jsx         # 드래그 앤 드롭 정렬
│   ├── VideoPlayer.jsx          # 영상 플레이어
│   ├── ProgressBar.jsx          # 진행 상황 표시
│   └── SettingsPanel.jsx        # 편집 옵션 설정
├── pages/
│   ├── HomePage.jsx
│   ├── SearchPage.jsx
│   ├── SelectPage.jsx
│   ├── GeneratePage.jsx
│   ├── PreviewPage.jsx
│   └── LibraryPage.jsx
├── hooks/
│   ├── useVideoSearch.js
│   ├── useVideoSelection.js
│   └── useVideoGeneration.js
├── stores/
│   └── videoStore.js
└── utils/
    ├── api.js
    └── websocket.js
```

---

### 2.2 Backend API (애플리케이션 계층)

#### 2.2.1 기술 스택
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Task Queue**: Celery
- **Message Broker**: Redis
- **File Handling**: python-multipart
- **Video Processing**: MoviePy, FFmpeg-python

#### 2.2.2 API 엔드포인트 설계

**검색 API**
```
POST /api/v1/search
- Request: { "keyword": "football skills", "limit": 30 }
- Response: { "search_id": "uuid", "status": "processing" }

GET /api/v1/search/{search_id}
- Response: {
    "status": "completed",
    "videos": [
      {
        "id": "video_uuid",
        "tiktok_id": "123456",
        "thumbnail_url": "https://...",
        "title": "Amazing goal",
        "views": 1000000,
        "likes": 50000,
        "duration": 15,
        "download_url": "https://..."
      },
      ...
    ]
  }
```

**프로젝트 API**
```
POST /api/v1/projects
- Request: {
    "name": "Top 10 Football Goals",
    "selected_videos": ["video_uuid_1", "video_uuid_2", ...],
    "video_order": [0, 1, 2, 3, 4],
    "settings": {
      "background_music": "music.mp3",
      "font": "Arial",
      "text_color": "#FFFFFF"
    }
  }
- Response: { "project_id": "uuid", "status": "created" }

POST /api/v1/projects/{project_id}/generate
- Response: { "task_id": "celery_task_uuid", "status": "queued" }

GET /api/v1/projects/{project_id}/status
- Response: {
    "status": "processing",
    "progress": 45,
    "current_step": "Downloading video 3/5",
    "estimated_time": 120
  }

GET /api/v1/projects/{project_id}/result
- Response: {
    "status": "completed",
    "video_url": "/api/v1/videos/final_uuid/stream",
    "thumbnail_url": "/api/v1/videos/final_uuid/thumbnail",
    "file_size": 15728640,
    "duration": 45
  }
```

**영상 API**
```
GET /api/v1/videos/{video_id}/stream
- Response: video file stream (MP4)

GET /api/v1/videos/{video_id}/download
- Response: video file download

POST /api/v1/videos/{video_id}/approve
- Request: { "approved": true }
- Response: { "status": "approved", "moved_to": "output/approved/" }

DELETE /api/v1/videos/{video_id}
- Response: { "status": "deleted" }
```

**설정 API**
```
GET /api/v1/settings
POST /api/v1/settings
GET /api/v1/templates
```

#### 2.2.3 디렉토리 구조
```
backend/
├── app/
│   ├── main.py                 # FastAPI 앱 진입점
│   ├── config.py               # 설정 파일
│   ├── dependencies.py         # 의존성 주입
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── search.py
│   │   │   │   ├── projects.py
│   │   │   │   ├── videos.py
│   │   │   │   └── settings.py
│   │   │   └── router.py
│   ├── core/
│   │   ├── scraper.py          # TikTok 스크래핑
│   │   ├── downloader.py       # 영상 다운로드
│   │   ├── video_processor.py  # 영상 편집
│   │   └── task_manager.py     # Celery 작업 관리
│   ├── models/
│   │   ├── search.py
│   │   ├── project.py
│   │   └── video.py
│   ├── schemas/
│   │   ├── search.py
│   │   ├── project.py
│   │   └── video.py
│   ├── db/
│   │   ├── database.py
│   │   └── session.py
│   └── utils/
│       ├── ffmpeg_helper.py
│       ├── file_manager.py
│       └── logger.py
├── celery_app.py               # Celery worker 설정
├── requirements.txt
└── tests/
```

---

### 2.3 Task Queue (비동기 작업 처리)

#### 2.3.1 Celery 작업 구조
```python
# celery_app.py

@celery.task(bind=True)
def search_tiktok_videos(self, keyword, limit):
    """TikTok 영상 검색 작업"""
    self.update_state(state='PROGRESS', meta={'current': 0, 'total': limit})
    # 스크래핑 로직
    return {"videos": [...]}

@celery.task(bind=True)
def download_video(self, video_url, output_path):
    """영상 다운로드 작업"""
    # 다운로드 로직 with progress update
    return {"file_path": output_path}

@celery.task(bind=True)
def generate_ranking_video(self, project_id):
    """최종 랭킹 영상 생성 작업"""
    # 1. 영상 다운로드 (병렬)
    # 2. 영상 전처리 (크롭, 리사이즈)
    # 3. 랭킹 텍스트 오버레이
    # 4. 영상 합치기
    # 5. 배경음악 추가
    return {"video_path": "output/pending/video.mp4"}
```

#### 2.3.2 작업 흐름
```
User Request
    ↓
FastAPI Endpoint
    ↓
Create Celery Task
    ↓
[Task Queue] → Redis
    ↓
Celery Worker picks up task
    ↓
Execute Task (with progress updates)
    ↓
Update Database
    ↓
Send WebSocket notification
    ↓
Frontend updates UI
```

---

### 2.4 Video Processing Pipeline (영상 처리)

#### 2.4.1 처리 단계
```
1. Download
   ├─ TikTok URL → MP4 file
   └─ Progress tracking

2. Preprocessing
   ├─ Aspect ratio detection
   ├─ Crop to 9:16
   ├─ Resize to 1080x1920
   └─ Trim to 5-10 seconds

3. Text Overlay
   ├─ Generate ranking badge (🥇 #1)
   ├─ Position: top-center
   ├─ Animation: fade in
   └─ Font/color from settings

4. Concatenation
   ├─ Join videos in order
   ├─ Add transitions (fade/slide)
   └─ Adjust timing

5. Audio Processing
   ├─ Extract original audio (optional)
   ├─ Add background music
   ├─ Mix audio levels
   └─ Fade in/out

6. Final Rendering
   ├─ Encode to H.264
   ├─ Quality: 1080p, 30fps
   ├─ Bitrate: 8Mbps
   └─ Output: MP4
```

#### 2.4.2 FFmpeg 명령어 예시
```bash
# 1. 크롭 및 리사이즈
ffmpeg -i input.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920" output.mp4

# 2. 텍스트 오버레이
ffmpeg -i input.mp4 -vf "drawtext=text='🥇 #1':fontfile=/path/font.ttf:fontsize=72:fontcolor=white:x=(w-text_w)/2:y=100" output.mp4

# 3. 영상 합치기
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4

# 4. 배경음악 추가
ffmpeg -i video.mp4 -i music.mp3 -filter_complex "[0:a][1:a]amix=inputs=2:duration=first[a]" -map 0:v -map "[a]" output.mp4
```

#### 2.4.3 MoviePy 사용 예시
```python
from moviepy.editor import *

# 영상 로드
clips = [VideoFileClip(f"video_{i}.mp4") for i in range(5)]

# 텍스트 추가
txt_clips = [TextClip(f"#{i+1}", fontsize=70, color='white')
             .set_position(('center', 100))
             .set_duration(clip.duration)
             for i, clip in enumerate(clips)]

# 합성
final_clips = [CompositeVideoClip([clip, txt]) for clip, txt in zip(clips, txt_clips)]

# 이어붙이기
final = concatenate_videoclips(final_clips, method="compose")

# 배경음악 추가
audio = AudioFileClip("music.mp3").set_duration(final.duration)
final = final.set_audio(audio)

# 저장
final.write_videofile("output.mp4", fps=30)
```

---

### 2.5 Data Layer (데이터 계층)

#### 2.5.1 데이터베이스 스키마 (SQLite)

**searches 테이블**
```sql
CREATE TABLE searches (
    id VARCHAR PRIMARY KEY,
    keyword VARCHAR NOT NULL,
    status VARCHAR CHECK(status IN ('processing', 'completed', 'failed')),
    total_found INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

**videos 테이블**
```sql
CREATE TABLE videos (
    id VARCHAR PRIMARY KEY,
    search_id VARCHAR REFERENCES searches(id),
    tiktok_id VARCHAR UNIQUE,
    thumbnail_url TEXT,
    title TEXT,
    description TEXT,
    views INTEGER,
    likes INTEGER,
    duration INTEGER,
    download_url TEXT,
    local_path TEXT,
    downloaded BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**projects 테이블**
```sql
CREATE TABLE projects (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    status VARCHAR CHECK(status IN ('created', 'processing', 'completed', 'failed')),
    settings JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

**project_videos 테이블** (Many-to-Many)
```sql
CREATE TABLE project_videos (
    project_id VARCHAR REFERENCES projects(id),
    video_id VARCHAR REFERENCES videos(id),
    rank_order INTEGER NOT NULL,
    PRIMARY KEY (project_id, video_id)
);
```

**final_videos 테이블**
```sql
CREATE TABLE final_videos (
    id VARCHAR PRIMARY KEY,
    project_id VARCHAR REFERENCES projects(id),
    file_path TEXT NOT NULL,
    thumbnail_path TEXT,
    file_size INTEGER,
    duration INTEGER,
    status VARCHAR CHECK(status IN ('pending', 'approved', 'rejected')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP
);
```

#### 2.5.2 파일 스토리지 구조
```
storage/
├── downloads/              # 다운로드한 원본 영상
│   ├── {video_id}.mp4
│   └── ...
├── thumbnails/             # 썸네일
│   ├── {video_id}.jpg
│   └── ...
├── temp/                   # 임시 처리 파일
│   ├── {project_id}/
│   │   ├── video_1_processed.mp4
│   │   ├── video_2_processed.mp4
│   │   └── ...
│   └── ...
├── output/
│   ├── pending/            # 검수 대기
│   │   └── {final_video_id}.mp4
│   └── approved/           # 승인된 영상
│       └── {final_video_id}.mp4
└── music/                  # 배경음악 라이브러리
    ├── music_1.mp3
    └── ...
```

---

## 3. 통신 프로토콜

### 3.1 REST API
- **Content-Type**: `application/json`
- **Authentication**: JWT (향후 추가 시)
- **Error Format**:
```json
{
  "error": {
    "code": "VIDEO_DOWNLOAD_FAILED",
    "message": "Failed to download video from TikTok",
    "details": { ... }
  }
}
```

### 3.2 WebSocket (실시간 진행 상황)
```javascript
// Frontend
const socket = io('http://localhost:8000');

socket.on('connect', () => {
  socket.emit('subscribe', { project_id: 'xxx' });
});

socket.on('progress', (data) => {
  // { step: 'downloading', current: 3, total: 5, percent: 60 }
});

socket.on('completed', (data) => {
  // { project_id: 'xxx', video_url: '...' }
});
```

---

## 4. 보안 아키텍처

### 4.1 인증/인가
- **Phase 1**: 인증 없음 (로컬 단일 사용자)
- **Phase 2** (향후): JWT 기반 인증

### 4.2 입력 검증
- Pydantic을 통한 요청 데이터 검증
- 파일 업로드 시 확장자 및 크기 제한
- SQL Injection 방지 (SQLAlchemy ORM 사용)

### 4.3 파일 접근 제어
- 업로드된 파일은 UUID 기반 파일명 사용
- 직접 파일 경로 노출 방지
- API를 통한 스트리밍만 허용

---

## 5. 확장성 고려사항

### 5.1 수평 확장
- Celery Worker를 여러 인스턴스로 확장 가능
- Redis를 통한 작업 분산
- Stateless API 서버 (세션 정보는 DB/Redis에 저장)

### 5.2 성능 최적화
- 영상 다운로드: 병렬 처리 (asyncio)
- 영상 처리: GPU 가속 (NVENC) 지원 (선택 사항)
- 썸네일 캐싱: CDN 또는 로컬 캐시

### 5.3 모니터링
- Celery Flower: 작업 큐 모니터링
- FastAPI 로깅: 요청/응답 로그
- 디스크 사용량 모니터링

---

## 6. 장애 처리 및 복구

### 6.1 작업 실패 처리
```python
@celery.task(bind=True, max_retries=3)
def download_video(self, video_url):
    try:
        # 다운로드 로직
    except NetworkError as exc:
        # 네트워크 오류 시 재시도
        raise self.retry(exc=exc, countdown=60)
    except Exception as exc:
        # 그 외 오류는 실패 처리
        update_status(video_id, 'failed', error=str(exc))
        raise
```

### 6.2 데이터 정합성
- 트랜잭션 처리: SQLAlchemy 세션 관리
- 파일 삭제 시 DB 레코드도 함께 삭제
- 고아 파일 정리 스크립트 (크론)

### 6.3 백업
- 데이터베이스: 일일 자동 백업
- 승인된 영상: 외부 스토리지 동기화 (선택 사항)

---

## 7. 배포 아키텍처

### 7.1 로컬 개발 환경
```
┌─────────────────────────────────────┐
│         개발 PC (localhost)          │
│  ┌──────────┐  ┌──────────┐         │
│  │ Frontend │  │ Backend  │         │
│  │ :5173    │  │ :8000    │         │
│  └──────────┘  └──────────┘         │
│  ┌──────────┐  ┌──────────┐         │
│  │  Redis   │  │  Celery  │         │
│  │  :6379   │  │  Worker  │         │
│  └──────────┘  └──────────┘         │
│  ┌──────────────────────────┐       │
│  │  SQLite DB + File Storage│       │
│  └──────────────────────────┘       │
└─────────────────────────────────────┘
```

### 7.2 프로덕션 환경 (향후)
```
┌─────────────────────────────────────────────┐
│               Cloud Infrastructure           │
│  ┌──────────────┐   ┌──────────────┐       │
│  │  Nginx       │   │  Frontend    │       │
│  │  (Reverse    │──▶│  (Static)    │       │
│  │   Proxy)     │   │              │       │
│  └──────┬───────┘   └──────────────┘       │
│         │                                   │
│  ┌──────▼───────────────────┐              │
│  │  FastAPI (Gunicorn)      │              │
│  │  (Multiple instances)    │              │
│  └──────┬───────────────────┘              │
│         │                                   │
│  ┌──────▼───────┐   ┌──────────────┐       │
│  │  PostgreSQL  │   │  Redis       │       │
│  └──────────────┘   └──────┬───────┘       │
│                             │               │
│  ┌──────────────────────────▼──────┐       │
│  │  Celery Workers (Auto-scaling)  │       │
│  └─────────────────────────────────┘       │
│  ┌─────────────────────────────────┐       │
│  │  S3/Cloud Storage (Videos)      │       │
│  └─────────────────────────────────┘       │
└─────────────────────────────────────────────┘
```

---

## 8. 기술적 의사결정 (ADR - Architecture Decision Records)

### ADR-001: FastAPI vs Flask 선택
- **결정**: FastAPI 사용
- **이유**:
  - 자동 API 문서 생성 (Swagger)
  - Pydantic 기반 검증
  - 비동기 지원 (async/await)
  - 더 빠른 성능
- **대안**: Flask (간단하지만 기능 부족)

### ADR-002: SQLite vs PostgreSQL
- **결정**: SQLite (Phase 1)
- **이유**:
  - 단일 사용자 환경
  - 설치/설정 불필요
  - 충분한 성능
- **향후**: PostgreSQL로 마이그레이션 (다중 사용자 시)

### ADR-003: Celery vs RQ (Redis Queue)
- **결정**: Celery
- **이유**:
  - 더 강력한 기능 (재시도, 스케줄링)
  - 더 넓은 커뮤니티
  - 진행 상황 추적 용이
- **대안**: RQ (더 간단하지만 기능 제한적)

### ADR-004: MoviePy vs FFmpeg-python
- **결정**: 둘 다 사용
- **이유**:
  - MoviePy: 간단한 작업, Python 친화적
  - FFmpeg: 복잡한 작업, 성능 중요 시
- **트레이드오프**: 학습 곡선 vs 유연성

---

## 9. 다이어그램

### 9.1 시퀀스 다이어그램: 영상 생성 플로우
```
User          Frontend        Backend API      Celery Worker    FFmpeg
 │                │               │                  │             │
 │──Search────────▶│               │                  │             │
 │                │──POST /search─▶│                  │             │
 │                │               │──Create Task────▶│             │
 │                │◀──task_id─────│                  │             │
 │                │               │                  │──Scrape TikTok
 │                │               │                  │             │
 │◀─Video List────│◀──WebSocket───│◀──Results────────│             │
 │                │               │                  │             │
 │──Select 5 ─────▶│               │                  │             │
 │                │──POST /generate▶│                 │             │
 │                │               │──Create Task────▶│             │
 │                │               │                  │──Download───┤
 │                │               │                  │◀────────────┤
 │◀─Progress 20%──│◀──WebSocket───│◀──Progress───────│             │
 │                │               │                  │──Process────▶│
 │                │               │                  │             │──Crop
 │                │               │                  │             │──Overlay
 │                │               │                  │             │──Concat
 │◀─Progress 80%──│◀──WebSocket───│◀──Progress───────│◀─────────────│
 │                │               │                  │──Save────────│
 │◀─Completed─────│◀──WebSocket───│◀──Completed──────│             │
 │                │               │                  │             │
 │──Preview───────▶│──GET /video/──▶│                 │             │
 │◀─Video Stream──│◀──Stream──────│                  │             │
 │                │               │                  │             │
```

### 9.2 데이터 흐름 다이어그램
```
[User Input]
    │
    ├─ Keyword: "football skills"
    │
    ▼
[TikTok Scraper]
    │
    ├─ Video Metadata (20-30 items)
    │  ├─ URL
    │  ├─ Thumbnail
    │  └─ Stats (views, likes)
    ▼
[Database: searches, videos]
    │
    ▼
[Frontend: Selection UI]
    │
    ├─ User selects 5 videos
    ├─ User arranges order
    │
    ▼
[Database: projects, project_videos]
    │
    ▼
[Video Downloader]
    │
    ├─ Download 5 videos
    │
    ▼
[storage/downloads/]
    │
    ▼
[Video Processor]
    │
    ├─ Crop → Resize → Overlay → Concat → Audio
    │
    ▼
[storage/output/pending/]
    │
    ▼
[Frontend: Preview UI]
    │
    ├─ User approves
    │
    ▼
[storage/output/approved/]
    │
    ▼
[Final Download]
```

---

## 10. 확장 로드맵

### Phase 1: MVP (현재)
- TikTok 스크래핑
- 기본 영상 편집
- 웹 UI

### Phase 2: 기능 강화
- Instagram Reels 지원
- AI 추천 시스템
- 템플릿 다양화

### Phase 3: 클라우드 배포
- AWS/GCP 배포
- CDN 연동
- 다중 사용자 지원

### Phase 4: 엔터프라이즈
- 유튜브 자동 업로드
- 분석 대시보드
- API 제공

---

**문서 버전**: 1.0
**작성일**: 2025-10-19
**최종 수정일**: 2025-10-19
