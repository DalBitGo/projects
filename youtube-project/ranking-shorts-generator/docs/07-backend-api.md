# 백엔드 API 설계 문서

## 1. API 개요

### 1.1 기본 정보
- **Base URL**: `http://localhost:8000/api/v1`
- **Protocol**: HTTP/HTTPS
- **Format**: JSON
- **Authentication**: None (Phase 1), JWT (Phase 2)
- **API 문서**: Swagger UI (`/api/docs`)

### 1.2 공통 응답 형식

**성공 응답**:
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

**에러 응답**:
```json
{
  "success": false,
  "error": {
    "code": "VIDEO_NOT_FOUND",
    "message": "The requested video does not exist",
    "details": { ... }
  }
}
```

---

## 2. API 엔드포인트

### 2.1 검색 API

#### POST `/api/v1/search`
TikTok 영상 검색 시작

**Request**:
```json
{
  "keyword": "football skills",
  "limit": 30,
  "filters": {
    "min_views": 100000,
    "min_likes": 5000,
    "max_duration": 60
  }
}
```

**Response (202 Accepted)**:
```json
{
  "search_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Search started"
}
```

---

#### GET `/api/v1/search/{search_id}`
검색 결과 조회

**Response (200 OK)** - 완료 시:
```json
{
  "search_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "keyword": "football skills",
  "total_found": 30,
  "videos": [
    {
      "id": "video-uuid-1",
      "tiktok_id": "7123456789",
      "thumbnail_url": "https://example.com/thumb.jpg",
      "title": "Amazing goal!",
      "description": "Check out this incredible goal",
      "views": 1500000,
      "likes": 75000,
      "comments": 1200,
      "shares": 800,
      "duration": 15,
      "download_url": "https://example.com/video.mp4",
      "author": {
        "username": "footballfan",
        "profile_image": "https://example.com/profile.jpg"
      },
      "created_at": "2025-01-15T10:30:00Z"
    },
    // ... more videos
  ]
}
```

**Response (202 Accepted)** - 처리 중:
```json
{
  "search_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45,
  "current_step": "Scraping videos...",
  "estimated_time": 30
}
```

---

### 2.2 프로젝트 API

#### POST `/api/v1/projects`
새 프로젝트 생성

**Request**:
```json
{
  "name": "Top 10 Football Goals",
  "selected_videos": [
    "video-uuid-1",
    "video-uuid-2",
    "video-uuid-3",
    "video-uuid-4",
    "video-uuid-5"
  ],
  "video_order": [0, 1, 2, 3, 4],
  "settings": {
    "background_music": "energetic_1.mp3",
    "font": "Arial-Bold",
    "text_color": "#FFFFFF",
    "text_position": "top-center",
    "video_duration": 7,
    "quality": "high"
  }
}
```

**Response (201 Created)**:
```json
{
  "project_id": "project-uuid",
  "name": "Top 10 Football Goals",
  "status": "created",
  "created_at": "2025-01-19T14:00:00Z"
}
```

---

#### GET `/api/v1/projects`
프로젝트 목록 조회

**Query Parameters**:
- `status`: Filter by status (`created`, `processing`, `completed`, `failed`)
- `limit`: Results per page (default: 20)
- `offset`: Pagination offset (default: 0)

**Response (200 OK)**:
```json
{
  "total": 15,
  "limit": 20,
  "offset": 0,
  "projects": [
    {
      "project_id": "project-uuid",
      "name": "Top 10 Football Goals",
      "status": "completed",
      "created_at": "2025-01-19T14:00:00Z",
      "completed_at": "2025-01-19T14:05:00Z",
      "video_count": 5
    },
    // ... more projects
  ]
}
```

---

#### GET `/api/v1/projects/{project_id}`
프로젝트 상세 조회

**Response (200 OK)**:
```json
{
  "project_id": "project-uuid",
  "name": "Top 10 Football Goals",
  "status": "completed",
  "created_at": "2025-01-19T14:00:00Z",
  "completed_at": "2025-01-19T14:05:00Z",
  "videos": [
    {
      "rank": 1,
      "video": {
        "id": "video-uuid-1",
        "title": "Amazing goal!",
        "thumbnail_url": "https://..."
      }
    },
    // ... more videos
  ],
  "settings": {
    "background_music": "energetic_1.mp3",
    "font": "Arial-Bold",
    "text_color": "#FFFFFF"
  },
  "final_video": {
    "id": "final-video-uuid",
    "file_path": "/api/v1/videos/final-video-uuid/stream",
    "thumbnail_path": "/api/v1/videos/final-video-uuid/thumbnail",
    "file_size": 15728640,
    "duration": 35,
    "status": "approved"
  }
}
```

---

#### POST `/api/v1/projects/{project_id}/generate`
영상 생성 시작

**Response (202 Accepted)**:
```json
{
  "task_id": "celery-task-uuid",
  "project_id": "project-uuid",
  "status": "queued",
  "message": "Video generation started"
}
```

---

#### GET `/api/v1/projects/{project_id}/status`
생성 진행 상황 조회

**Response (200 OK)**:
```json
{
  "project_id": "project-uuid",
  "status": "processing",
  "progress": 65,
  "current_step": "Concatenating videos",
  "steps_completed": [
    "Downloaded videos",
    "Preprocessed videos",
    "Added ranking text"
  ],
  "steps_pending": [
    "Adding background music",
    "Final rendering"
  ],
  "estimated_time": 120
}
```

---

#### DELETE `/api/v1/projects/{project_id}`
프로젝트 삭제

**Response (204 No Content)**

---

### 2.3 영상 API

#### GET `/api/v1/videos/{video_id}/stream`
영상 스트리밍

**Response (200 OK)**:
- Content-Type: `video/mp4`
- Stream: Video file content

**Headers**:
```
Accept-Ranges: bytes
Content-Length: 15728640
Content-Type: video/mp4
```

---

#### GET `/api/v1/videos/{video_id}/download`
영상 다운로드

**Response (200 OK)**:
- Content-Type: `video/mp4`
- Content-Disposition: `attachment; filename="ranking_short_20250119.mp4"`

---

#### GET `/api/v1/videos/{video_id}/thumbnail`
썸네일 조회

**Response (200 OK)**:
- Content-Type: `image/jpeg`

---

#### POST `/api/v1/videos/{video_id}/approve`
영상 승인

**Request**:
```json
{
  "approved": true,
  "notes": "Looks great!"
}
```

**Response (200 OK)**:
```json
{
  "video_id": "final-video-uuid",
  "status": "approved",
  "moved_to": "storage/output/approved/",
  "approved_at": "2025-01-19T15:00:00Z"
}
```

---

#### DELETE `/api/v1/videos/{video_id}`
영상 삭제

**Response (204 No Content)**

---

### 2.4 설정 API

#### GET `/api/v1/settings`
설정 조회

**Response (200 OK)**:
```json
{
  "video": {
    "default_duration": 7,
    "quality": "high",
    "fps": 30
  },
  "text_overlay": {
    "font": "Arial-Bold",
    "color": "#FFFFFF",
    "position": "top-center"
  },
  "background_music": {
    "default_track": "energetic_1.mp3",
    "volume": 0.3
  },
  "general": {
    "auto_approve": false,
    "auto_delete_temp": true
  }
}
```

---

#### PUT `/api/v1/settings`
설정 업데이트

**Request**:
```json
{
  "video": {
    "default_duration": 10
  },
  "text_overlay": {
    "color": "#FFD700"
  }
}
```

**Response (200 OK)**:
```json
{
  "message": "Settings updated successfully",
  "settings": { ... }
}
```

---

#### GET `/api/v1/templates`
템플릿 목록 조회

**Response (200 OK)**:
```json
{
  "templates": [
    {
      "id": "sports",
      "name": "Sports Highlights",
      "description": "Perfect for sports ranking videos",
      "preview_image": "/api/v1/templates/sports/preview.jpg",
      "settings": {
        "font": "Impact",
        "text_color": "#FFD700",
        "background_music": "epic_1.mp3"
      }
    },
    // ... more templates
  ]
}
```

---

## 3. WebSocket API

### 3.1 Connection
```
ws://localhost:8000/ws
```

### 3.2 이벤트

#### Client → Server

**Subscribe to Project**:
```json
{
  "event": "subscribe",
  "data": {
    "project_id": "project-uuid"
  }
}
```

**Unsubscribe**:
```json
{
  "event": "unsubscribe",
  "data": {
    "project_id": "project-uuid"
  }
}
```

---

#### Server → Client

**Progress Update**:
```json
{
  "event": "progress",
  "data": {
    "project_id": "project-uuid",
    "progress": 65,
    "current_step": "Concatenating videos",
    "percent": 65
  }
}
```

**Completion**:
```json
{
  "event": "completed",
  "data": {
    "project_id": "project-uuid",
    "video_id": "final-video-uuid",
    "video_url": "/api/v1/videos/final-video-uuid/stream"
  }
}
```

**Error**:
```json
{
  "event": "error",
  "data": {
    "project_id": "project-uuid",
    "error": "Failed to download video",
    "code": "DOWNLOAD_ERROR"
  }
}
```

---

## 4. 에러 코드

| 코드 | HTTP Status | 설명 |
|------|-------------|------|
| `SEARCH_FAILED` | 500 | 검색 실패 |
| `VIDEO_NOT_FOUND` | 404 | 영상을 찾을 수 없음 |
| `PROJECT_NOT_FOUND` | 404 | 프로젝트를 찾을 수 없음 |
| `INVALID_VIDEO_COUNT` | 400 | 영상 개수 부족 (5개 미만) |
| `DOWNLOAD_ERROR` | 500 | 다운로드 실패 |
| `PROCESSING_ERROR` | 500 | 영상 처리 실패 |
| `RATE_LIMIT_EXCEEDED` | 429 | 요청 제한 초과 |
| `VALIDATION_ERROR` | 422 | 입력 검증 실패 |

---

## 5. Rate Limiting

### 5.1 제한 정책
- **검색 API**: 10 req/min
- **영상 생성 API**: 5 req/hour
- **기타 API**: 100 req/min

### 5.2 응답 헤더
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1642598400
```

### 5.3 제한 초과 시 응답 (429)
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "retry_after": 60
  }
}
```

---

## 6. Pagination

### 6.1 Query Parameters
- `limit`: 페이지 크기 (기본: 20, 최대: 100)
- `offset`: 시작 위치 (기본: 0)

### 6.2 응답
```json
{
  "total": 150,
  "limit": 20,
  "offset": 40,
  "has_more": true,
  "data": [ ... ]
}
```

---

## 7. 구현 예시 (FastAPI)

### 7.1 프로젝트 구조
```
backend/app/api/v1/endpoints/
├── search.py
├── projects.py
├── videos.py
└── settings.py
```

### 7.2 Search Endpoint 구현

```python
# app/api/v1/endpoints/search.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import uuid

router = APIRouter()

class SearchRequest(BaseModel):
    keyword: str
    limit: int = 30
    filters: Optional[dict] = None

class SearchResponse(BaseModel):
    search_id: str
    status: str
    message: str

@router.post("/search", response_model=SearchResponse, status_code=202)
async def search_videos(
    request: SearchRequest,
    background_tasks: BackgroundTasks
):
    """
    TikTok 영상 검색 시작
    """
    search_id = str(uuid.uuid4())

    # DB에 검색 기록 저장
    # ...

    # Celery 작업 실행
    from app.core.tasks import scrape_tiktok_task
    task = scrape_tiktok_task.delay(search_id, request.keyword, request.limit)

    return SearchResponse(
        search_id=search_id,
        status="processing",
        message="Search started"
    )

@router.get("/search/{search_id}")
async def get_search_results(search_id: str):
    """
    검색 결과 조회
    """
    # DB에서 검색 결과 조회
    search = await get_search_by_id(search_id)

    if not search:
        raise HTTPException(status_code=404, detail="Search not found")

    if search.status == "completed":
        videos = await get_videos_by_search_id(search_id)
        return {
            "search_id": search_id,
            "status": "completed",
            "videos": videos
        }
    else:
        # 진행 상황 조회 (Celery)
        task = scrape_tiktok_task.AsyncResult(search.task_id)
        return {
            "search_id": search_id,
            "status": task.state,
            "progress": task.info.get('current', 0) if task.info else 0
        }
```

### 7.3 Projects Endpoint 구현

```python
# app/api/v1/endpoints/projects.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()

class ProjectCreate(BaseModel):
    name: str
    selected_videos: List[str]
    video_order: List[int]
    settings: dict

@router.post("/projects", status_code=201)
async def create_project(project: ProjectCreate):
    """
    프로젝트 생성
    """
    project_id = str(uuid.uuid4())

    # DB에 저장
    # ...

    return {
        "project_id": project_id,
        "name": project.name,
        "status": "created",
        "created_at": datetime.utcnow()
    }

@router.post("/projects/{project_id}/generate", status_code=202)
async def generate_video(project_id: str):
    """
    영상 생성 시작
    """
    # 프로젝트 조회
    project = await get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Celery 작업 실행
    from app.core.tasks import generate_ranking_video_task
    task = generate_ranking_video_task.delay(
        project_id=project_id,
        video_urls=[v.download_url for v in project.videos],
        music_path=project.settings.get('background_music')
    )

    return {
        "task_id": task.id,
        "project_id": project_id,
        "status": "queued"
    }
```

### 7.4 Videos Endpoint 구현

```python
# app/api/v1/endpoints/videos.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse, FileResponse
from pathlib import Path

router = APIRouter()

@router.get("/videos/{video_id}/stream")
async def stream_video(video_id: str):
    """
    영상 스트리밍
    """
    video = await get_video(video_id)

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    file_path = Path(video.file_path)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")

    return FileResponse(
        file_path,
        media_type="video/mp4",
        headers={
            "Accept-Ranges": "bytes"
        }
    )

@router.get("/videos/{video_id}/download")
async def download_video(video_id: str):
    """
    영상 다운로드
    """
    video = await get_video(video_id)
    file_path = Path(video.file_path)

    filename = f"ranking_short_{video.created_at.strftime('%Y%m%d')}.mp4"

    return FileResponse(
        file_path,
        media_type="video/mp4",
        filename=filename
    )
```

---

## 8. WebSocket 구현

```python
# app/api/v1/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, project_id: str):
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()
        self.active_connections[project_id].add(websocket)

    def disconnect(self, websocket: WebSocket, project_id: str):
        if project_id in self.active_connections:
            self.active_connections[project_id].discard(websocket)

    async def send_progress(self, project_id: str, data: dict):
        if project_id in self.active_connections:
            message = json.dumps({"event": "progress", "data": data})
            for connection in self.active_connections[project_id]:
                await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()

            if data["event"] == "subscribe":
                project_id = data["data"]["project_id"]
                await manager.connect(websocket, project_id)

            elif data["event"] == "unsubscribe":
                project_id = data["data"]["project_id"]
                manager.disconnect(websocket, project_id)

    except WebSocketDisconnect:
        # Cleanup
        pass
```

---

**문서 버전**: 1.0
**작성일**: 2025-01-19
**최종 수정일**: 2025-01-19
