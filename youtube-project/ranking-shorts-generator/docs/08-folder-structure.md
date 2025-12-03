# 폴더 구조 및 파일 명세

## 1. 전체 프로젝트 구조

```
ranking-shorts-generator/
├── docs/                           # 문서
├── frontend/                       # React 프론트엔드
├── backend/                        # FastAPI 백엔드
├── storage/                        # 파일 저장소
├── docker-compose.yml              # Docker 구성
├── .gitignore
└── README.md
```

---

## 2. Frontend 구조

```
frontend/
├── public/
│   ├── index.html
│   ├── favicon.ico
│   └── assets/
│       ├── logo.png
│       └── music/                  # 기본 배경음악
│           ├── energetic_1.mp3
│           ├── chill_1.mp3
│           └── epic_1.mp3
├── src/
│   ├── main.jsx                    # 앱 진입점
│   ├── App.jsx                     # 루트 컴포넌트
│   ├── index.css                   # 글로벌 스타일
│   │
│   ├── pages/                      # 페이지 컴포넌트
│   │   ├── HomePage.jsx
│   │   ├── SearchPage.jsx
│   │   ├── SelectPage.jsx
│   │   ├── GeneratePage.jsx
│   │   ├── PreviewPage.jsx
│   │   ├── LibraryPage.jsx
│   │   └── SettingsPage.jsx
│   │
│   ├── components/                 # 재사용 컴포넌트
│   │   ├── common/                 # 공통 컴포넌트
│   │   │   ├── Button.jsx
│   │   │   ├── Card.jsx
│   │   │   ├── Modal.jsx
│   │   │   ├── ProgressBar.jsx
│   │   │   ├── Toast.jsx
│   │   │   ├── Skeleton.jsx
│   │   │   └── Loading.jsx
│   │   │
│   │   ├── video/                  # 영상 관련 컴포넌트
│   │   │   ├── VideoCard.jsx
│   │   │   ├── VideoGrid.jsx
│   │   │   ├── VideoPlayer.jsx
│   │   │   └── VideoPreview.jsx
│   │   │
│   │   ├── search/                 # 검색 관련 컴포넌트
│   │   │   ├── SearchBar.jsx
│   │   │   ├── FilterPanel.jsx
│   │   │   └── SearchHistory.jsx
│   │   │
│   │   ├── project/                # 프로젝트 관련 컴포넌트
│   │   │   ├── DragDropList.jsx
│   │   │   ├── RankingItem.jsx
│   │   │   └── ProgressTracker.jsx
│   │   │
│   │   └── layout/                 # 레이아웃 컴포넌트
│   │       ├── Navbar.jsx
│   │       ├── Sidebar.jsx
│   │       └── Footer.jsx
│   │
│   ├── hooks/                      # Custom Hooks
│   │   ├── useVideoSearch.js
│   │   ├── useVideoSelection.js
│   │   ├── useVideoGeneration.js
│   │   ├── useWebSocket.js
│   │   └── useLocalStorage.js
│   │
│   ├── stores/                     # Zustand Stores
│   │   ├── videoStore.js
│   │   ├── projectStore.js
│   │   └── uiStore.js
│   │
│   ├── services/                   # API 서비스
│   │   ├── videoService.js
│   │   ├── projectService.js
│   │   └── settingsService.js
│   │
│   ├── utils/                      # 유틸리티 함수
│   │   ├── api.js                  # Axios 설정
│   │   ├── socket.js               # Socket.IO 설정
│   │   ├── formatters.js           # 포맷팅 함수
│   │   └── validators.js           # 검증 함수
│   │
│   ├── constants/                  # 상수
│   │   ├── routes.js
│   │   ├── apiEndpoints.js
│   │   └── config.js
│   │
│   └── styles/                     # 스타일
│       └── tailwind.css
│
├── .env                            # 환경변수
├── .env.example
├── .eslintrc.js
├── .prettierrc
├── package.json
├── tailwind.config.js
├── vite.config.js
└── README.md
```

---

## 3. Backend 구조

```
backend/
├── app/
│   ├── main.py                     # FastAPI 앱 진입점
│   ├── config.py                   # 설정
│   ├── dependencies.py             # 의존성 주입
│   │
│   ├── api/                        # API 라우터
│   │   └── v1/
│   │       ├── router.py           # API 라우터 통합
│   │       ├── endpoints/
│   │       │   ├── search.py
│   │       │   ├── projects.py
│   │       │   ├── videos.py
│   │       │   └── settings.py
│   │       └── websocket.py        # WebSocket 엔드포인트
│   │
│   ├── core/                       # 핵심 비즈니스 로직
│   │   ├── scraper.py              # TikTok 스크래핑
│   │   ├── downloader.py           # 영상 다운로드
│   │   ├── video_processor.py      # 영상 처리
│   │   ├── task_manager.py         # Celery 작업 관리
│   │   └── tasks.py                # Celery 작업 정의
│   │
│   ├── models/                     # SQLAlchemy 모델
│   │   ├── search.py
│   │   ├── video.py
│   │   ├── project.py
│   │   └── final_video.py
│   │
│   ├── schemas/                    # Pydantic 스키마
│   │   ├── search.py
│   │   ├── video.py
│   │   ├── project.py
│   │   └── settings.py
│   │
│   ├── db/                         # 데이터베이스
│   │   ├── database.py             # DB 설정
│   │   ├── session.py              # 세션 관리
│   │   └── base.py                 # Base 모델
│   │
│   ├── utils/                      # 유틸리티
│   │   ├── ffmpeg_helper.py
│   │   ├── file_manager.py
│   │   ├── logger.py
│   │   └── validators.py
│   │
│   └── middleware/                 # 미들웨어
│       ├── cors.py
│       └── error_handler.py
│
├── alembic/                        # DB 마이그레이션
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
│
├── celery_app.py                   # Celery 앱 설정
├── tests/                          # 테스트
│   ├── test_scraper.py
│   ├── test_video_processor.py
│   └── test_api.py
│
├── .env                            # 환경변수
├── .env.example
├── requirements.txt
├── pyproject.toml
├── pytest.ini
└── README.md
```

---

## 4. Storage 구조

```
storage/
├── downloads/                      # 다운로드한 원본 영상
│   ├── {video_id}.mp4
│   ├── {video_id}.mp4
│   └── ...
│
├── thumbnails/                     # 썸네일 이미지
│   ├── {video_id}.jpg
│   ├── {video_id}.jpg
│   └── ...
│
├── temp/                           # 임시 처리 파일
│   ├── {project_id}/
│   │   ├── preprocessed_0.mp4
│   │   ├── preprocessed_1.mp4
│   │   ├── ranked_0.mp4
│   │   ├── ranked_1.mp4
│   │   └── concatenated.mp4
│   └── ...
│
├── output/                         # 최종 출력 영상
│   ├── pending/                    # 검수 대기
│   │   ├── {project_id}.mp4
│   │   └── ...
│   └── approved/                   # 승인된 영상
│       ├── {final_video_id}.mp4
│       └── ...
│
└── music/                          # 배경음악 라이브러리
    ├── energetic_1.mp3
    ├── energetic_2.mp3
    ├── chill_1.mp3
    ├── epic_1.mp3
    └── ...
```

---

## 5. 데이터베이스 스키마 파일

```
backend/app/models/
```

### 5.1 `search.py`
```python
from sqlalchemy import Column, String, Integer, DateTime
from app.db.base import Base

class Search(Base):
    __tablename__ = "searches"

    id = Column(String, primary_key=True)
    keyword = Column(String, nullable=False)
    status = Column(String, nullable=False)
    total_found = Column(Integer, default=0)
    task_id = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
```

### 5.2 `video.py`
```python
from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey
from app.db.base import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True)
    search_id = Column(String, ForeignKey("searches.id"))
    tiktok_id = Column(String, unique=True)
    thumbnail_url = Column(Text)
    title = Column(Text)
    description = Column(Text, nullable=True)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    duration = Column(Integer)
    download_url = Column(Text)
    local_path = Column(Text, nullable=True)
    downloaded = Column(Boolean, default=False)
    created_at = Column(DateTime)
```

### 5.3 `project.py`
```python
from sqlalchemy import Column, String, JSON, DateTime
from app.db.base import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    settings = Column(JSON, nullable=True)
    task_id = Column(String, nullable=True)
    created_at = Column(DateTime)
    completed_at = Column(DateTime, nullable=True)
```

### 5.4 `final_video.py`
```python
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from app.db.base import Base

class FinalVideo(Base):
    __tablename__ = "final_videos"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"))
    file_path = Column(String, nullable=False)
    thumbnail_path = Column(String, nullable=True)
    file_size = Column(Integer)
    duration = Column(Integer)
    status = Column(String)  # pending, approved, rejected
    created_at = Column(DateTime)
    approved_at = Column(DateTime, nullable=True)
```

---

## 6. 환경변수 파일

### 6.1 Frontend `.env`
```env
# API
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# Feature Flags
VITE_ENABLE_DEBUG=false
```

### 6.2 Backend `.env`
```env
# Database
DATABASE_URL=sqlite:///./app.db
# DATABASE_URL=postgresql://user:pass@localhost:5432/ranking_shorts

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Storage
STORAGE_PATH=./storage
TEMP_PATH=./storage/temp
OUTPUT_PATH=./storage/output
DOWNLOADS_PATH=./storage/downloads
THUMBNAILS_PATH=./storage/thumbnails
MUSIC_PATH=./storage/music

# API
API_V1_PREFIX=/api/v1
SECRET_KEY=your-secret-key-change-in-production

# CORS
FRONTEND_URL=http://localhost:5173
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# TikTok (if using official API)
TIKTOK_API_KEY=
TIKTOK_API_SECRET=

# External Services (optional)
APIFY_API_KEY=

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

---

## 7. 설정 파일

### 7.1 `frontend/package.json`
```json
{
  "name": "ranking-shorts-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext .js,.jsx",
    "format": "prettier --write src/**/*.{js,jsx}"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.0",
    "zustand": "^4.5.0",
    "socket.io-client": "^4.6.0",
    "react-beautiful-dnd": "^13.1.1",
    "react-player": "^2.14.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.33",
    "eslint": "^8.56.0",
    "prettier": "^3.1.0"
  }
}
```

### 7.2 `backend/requirements.txt`
```txt
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
python-socketio==5.10.0

# Database
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9  # PostgreSQL

# Task Queue
celery==5.3.4
redis==5.0.1
flower==2.0.1

# Video Processing
moviepy==1.0.3
ffmpeg-python==0.2.0
Pillow==10.2.0
yt-dlp==2024.1.0

# Scraping
TikTokApi==6.0.0
playwright==1.40.0
beautifulsoup4==4.12.2
httpx==0.26.0

# Utilities
pydantic==2.5.3
python-dotenv==1.0.0
aiofiles==23.2.1
tenacity==8.2.3

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.12.1
ruff==0.1.9
```

### 7.3 `backend/pyproject.toml`
```toml
[tool.black]
line-length = 100
target-version = ['py310']

[tool.ruff]
line-length = 100
select = ["E", "F", "I"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
```

---

## 8. Git 설정

### 8.1 `.gitignore`
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/
dist/
build/

# Node
node_modules/
dist/
.DS_Store

# IDE
.vscode/
.idea/
*.swp
*.swo

# Env
.env
.env.local

# Database
*.db
*.sqlite

# Logs
logs/
*.log

# Storage (don't commit videos)
storage/downloads/
storage/temp/
storage/output/
storage/thumbnails/

# Keep structure
!storage/.gitkeep
!storage/music/.gitkeep
```

---

## 9. Docker 구성

### 9.1 `docker-compose.yml`
```yaml
version: '3.8'

services:
  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ranking_shorts
      POSTGRES_PASSWORD: password
      POSTGRES_DB: ranking_shorts
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./storage:/app/storage
    environment:
      - DATABASE_URL=postgresql://ranking_shorts:password@postgres:5432/ranking_shorts
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - postgres

  celery_worker:
    build: ./backend
    command: celery -A celery_app worker --loglevel=info
    volumes:
      - ./backend:/app
      - ./storage:/app/storage
    environment:
      - DATABASE_URL=postgresql://ranking_shorts:password@postgres:5432/ranking_shorts
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - postgres

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8000

volumes:
  redis_data:
  postgres_data:
```

---

## 10. README 구조

### 10.1 루트 `README.md`
```markdown
# Ranking Shorts Generator

자동으로 TikTok 랭킹 쇼츠를 생성하는 시스템

## Features
- TikTok 영상 자동 검색
- 웹 UI를 통한 영상 선택
- 자동 영상 편집 (랭킹 텍스트, 배경음악)
- 검수 프로세스

## Quick Start
...

## Documentation
- [프로젝트 개요](docs/01-project-overview.md)
- [시스템 아키텍처](docs/02-system-architecture.md)
- [기술 스택](docs/03-tech-stack.md)
...
```

---

**문서 버전**: 1.0
**작성일**: 2025-01-19
**최종 수정일**: 2025-01-19
