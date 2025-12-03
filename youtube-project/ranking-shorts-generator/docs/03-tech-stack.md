# 기술 스택 및 의존성 문서

## 1. 전체 기술 스택 개요

### 1.1 기술 스택 요약

| 계층 | 기술 | 버전 | 목적 |
|------|------|------|------|
| **Frontend** | React.js | 18.2+ | 사용자 인터페이스 |
| | Vite | 5.0+ | 빌드 도구 |
| | Tailwind CSS | 3.4+ | 스타일링 |
| | shadcn/ui | Latest | UI 컴포넌트 |
| | Zustand | 4.5+ | 상태 관리 |
| | React Router | 6.20+ | 라우팅 |
| | Axios | 1.6+ | HTTP 클라이언트 |
| | Socket.IO Client | 4.6+ | WebSocket |
| | react-beautiful-dnd | 13.1+ | 드래그 앤 드롭 |
| **Backend** | Python | 3.10+ | 백엔드 언어 |
| | FastAPI | 0.109+ | REST API 프레임워크 |
| | Uvicorn | 0.27+ | ASGI 서버 |
| | Pydantic | 2.5+ | 데이터 검증 |
| | SQLAlchemy | 2.0+ | ORM |
| | Alembic | 1.13+ | DB 마이그레이션 |
| **Task Queue** | Celery | 5.3+ | 비동기 작업 처리 |
| | Redis | 7.2+ | 메시지 브로커 |
| **Database** | SQLite | 3.40+ | 데이터베이스 (개발) |
| | PostgreSQL | 15+ | 데이터베이스 (프로덕션) |
| **Video Processing** | FFmpeg | 6.0+ | 영상 편집 엔진 |
| | MoviePy | 1.0.3+ | Python 영상 처리 |
| | Pillow | 10.2+ | 이미지 처리 |
| **Scraping** | TikTokApi | 6.0+ | TikTok 스크래핑 |
| | Playwright | 1.40+ | 브라우저 자동화 |
| | BeautifulSoup4 | 4.12+ | HTML 파싱 |
| **Development** | pytest | 7.4+ | 테스팅 |
| | Black | 23.12+ | 코드 포맷팅 |
| | ESLint | 8.56+ | JS 린팅 |
| | Prettier | 3.1+ | JS 포맷팅 |

---

## 2. Frontend 상세 스택

### 2.1 Core Dependencies

#### React.js 18.2+
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0"
}
```
**선택 이유**:
- 컴포넌트 기반 아키텍처
- 풍부한 생태계 및 커뮤니티
- Concurrent Mode로 성능 향상
- 가장 대중적인 프론트엔드 프레임워크

**주요 기능**:
- Hooks (useState, useEffect, useMemo 등)
- Context API (글로벌 상태 관리)
- Suspense & Error Boundaries

---

#### Vite 5.0+
```json
{
  "vite": "^5.0.0",
  "@vitejs/plugin-react": "^4.2.0"
}
```
**선택 이유**:
- 빠른 HMR (Hot Module Replacement)
- Create React App 대비 10배 빠른 빌드
- 최신 ES 모듈 기반
- 간단한 설정

**설정 예시** (`vite.config.js`):
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
```

---

#### Tailwind CSS 3.4+
```json
{
  "tailwindcss": "^3.4.0",
  "autoprefixer": "^10.4.16",
  "postcss": "^8.4.33"
}
```
**선택 이유**:
- 유틸리티 우선 CSS
- 빠른 프로토타이핑
- 반응형 디자인 용이
- 빌드 시 사용하지 않는 CSS 자동 제거

**설정 예시** (`tailwind.config.js`):
```javascript
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        secondary: '#10B981',
      }
    }
  },
  plugins: []
}
```

---

#### shadcn/ui
```bash
npx shadcn-ui@latest init
```
**선택 이유**:
- Radix UI 기반 고품질 컴포넌트
- Tailwind와 완벽한 통합
- 커스터마이징 용이
- 접근성 (a11y) 기본 지원

**주요 컴포넌트**:
- Button, Card, Dialog, Dropdown
- Checkbox, Radio, Select
- Progress, Toast, Tooltip

---

### 2.2 State Management & Data Fetching

#### Zustand 4.5+
```json
{
  "zustand": "^4.5.0"
}
```
**선택 이유**:
- Redux 대비 간단한 설정
- 보일러플레이트 최소화
- TypeScript 친화적
- 작은 번들 사이즈 (1KB)

**사용 예시**:
```javascript
import { create } from 'zustand'

export const useVideoStore = create((set) => ({
  selectedVideos: [],
  addVideo: (video) => set((state) => ({
    selectedVideos: [...state.selectedVideos, video]
  })),
  removeVideo: (id) => set((state) => ({
    selectedVideos: state.selectedVideos.filter(v => v.id !== id)
  }))
}))
```

---

#### Axios 1.6+
```json
{
  "axios": "^1.6.0"
}
```
**설정 예시**:
```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 인터셉터
api.interceptors.response.use(
  response => response,
  error => {
    // 에러 처리
    return Promise.reject(error)
  }
)

export default api
```

---

### 2.3 UI/UX Libraries

#### React Router 6.20+
```json
{
  "react-router-dom": "^6.20.0"
}
```

#### Socket.IO Client 4.6+
```json
{
  "socket.io-client": "^4.6.0"
}
```
**사용 예시**:
```javascript
import { io } from 'socket.io-client'

const socket = io('http://localhost:8000', {
  transports: ['websocket'],
  autoConnect: false
})

socket.on('progress', (data) => {
  console.log('Progress:', data)
})

export default socket
```

---

#### react-beautiful-dnd 13.1+
```json
{
  "react-beautiful-dnd": "^13.1.1"
}
```
**목적**: 영상 순서 드래그 앤 드롭

---

#### react-player 2.14+
```json
{
  "react-player": "^2.14.0"
}
```
**목적**: 영상 미리보기 플레이어

---

### 2.4 개발 도구

#### ESLint & Prettier
```json
{
  "eslint": "^8.56.0",
  "eslint-config-prettier": "^9.1.0",
  "prettier": "^3.1.0"
}
```

**ESLint 설정** (`.eslintrc.js`):
```javascript
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
    'prettier'
  ],
  rules: {
    'react/prop-types': 'off',
    'no-unused-vars': 'warn'
  }
}
```

---

## 3. Backend 상세 스택

### 3.1 Core Framework

#### FastAPI 0.109+
```toml
# pyproject.toml or requirements.txt
fastapi = "^0.109.0"
uvicorn[standard] = "^0.27.0"
```

**선택 이유**:
- 자동 API 문서 (Swagger UI)
- Pydantic 기반 데이터 검증
- 비동기 지원 (async/await)
- WebSocket 내장 지원
- 빠른 성능 (Starlette 기반)

**기본 구조**:
```python
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Ranking Shorts Generator API",
    version="1.0.0",
    docs_url="/api/docs"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def root():
    return {"message": "Ranking Shorts Generator API"}
```

---

#### Uvicorn 0.27+
**ASGI 서버**

**실행 명령**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**프로덕션 설정**:
```bash
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

---

### 3.2 Database & ORM

#### SQLAlchemy 2.0+
```toml
sqlalchemy = "^2.0.0"
```

**ORM 예시**:
```python
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True)
    tiktok_id = Column(String, unique=True)
    title = Column(String)
    views = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

#### Alembic 1.13+
**데이터베이스 마이그레이션**

```bash
# 초기화
alembic init alembic

# 마이그레이션 생성
alembic revision --autogenerate -m "create videos table"

# 마이그레이션 적용
alembic upgrade head
```

---

### 3.3 Task Queue

#### Celery 5.3+
```toml
celery = "^5.3.0"
redis = "^5.0.0"
```

**Celery 설정** (`celery_app.py`):
```python
from celery import Celery

celery_app = Celery(
    "ranking_shorts",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Seoul',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30분
)
```

**Worker 실행**:
```bash
celery -A celery_app worker --loglevel=info
```

**Flower (모니터링)**:
```bash
celery -A celery_app flower --port=5555
```

---

#### Redis 7.2+
**설치** (Ubuntu):
```bash
sudo apt-get install redis-server
redis-server --version
```

**실행**:
```bash
redis-server
```

**확인**:
```bash
redis-cli ping
# PONG
```

---

### 3.4 Video Processing

#### FFmpeg 6.0+
**설치**:
```bash
# Ubuntu
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# 확인
ffmpeg -version
```

**Python 바인딩** (`ffmpeg-python`):
```toml
ffmpeg-python = "^0.2.0"
```

**사용 예시**:
```python
import ffmpeg

input_video = ffmpeg.input('input.mp4')
output = (
    input_video
    .filter('scale', 1080, 1920)
    .filter('crop', 'ih*9/16', 'ih')
    .output('output.mp4')
)
output.run()
```

---

#### MoviePy 1.0.3+
```toml
moviepy = "^1.0.3"
```

**사용 예시**:
```python
from moviepy.editor import *

# 영상 로드
clip = VideoFileClip("input.mp4")

# 텍스트 추가
txt_clip = TextClip("🥇 #1", fontsize=70, color='white', font='Arial-Bold')
txt_clip = txt_clip.set_position(('center', 100)).set_duration(clip.duration)

# 합성
final = CompositeVideoClip([clip, txt_clip])
final.write_videofile("output.mp4", fps=30)
```

---

#### Pillow 10.2+
```toml
Pillow = "^10.2.0"
```

**목적**: 썸네일 생성, 이미지 처리

```python
from PIL import Image, ImageDraw, ImageFont

# 썸네일 생성
img = Image.open("frame.jpg")
img.thumbnail((300, 400))
img.save("thumbnail.jpg")
```

---

### 3.5 Scraping

#### TikTokApi 6.0+
```toml
TikTokApi = "^6.0.0"
playwright = "^1.40.0"
```

**설치 후 Playwright 브라우저 설치**:
```bash
playwright install chromium
```

**사용 예시**:
```python
from TikTokApi import TikTokApi
import asyncio

async def get_videos():
    async with TikTokApi() as api:
        await api.create_sessions(num_sessions=1, sleep_after=3)

        tag = api.hashtag(name="football")
        async for video in tag.videos(count=30):
            print(video.id, video.stats['playCount'])

asyncio.run(get_videos())
```

---

#### Playwright 1.40+
**목적**: 브라우저 자동화 (TikTok 스크래핑 시 필요)

```python
from playwright.async_api import async_playwright

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.tiktok.com/tag/football")
        # 스크래핑 로직
        await browser.close()
```

---

### 3.6 Utilities

#### python-dotenv
```toml
python-dotenv = "^1.0.0"
```

**환경변수 관리** (`.env`):
```env
DATABASE_URL=sqlite:///./app.db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
```

```python
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
```

---

#### python-multipart
```toml
python-multipart = "^0.0.6"
```
**목적**: 파일 업로드 처리

---

#### aiofiles
```toml
aiofiles = "^23.2.0"
```
**목적**: 비동기 파일 I/O

---

## 4. 개발 도구

### 4.1 Python 개발 도구

#### pytest 7.4+
```toml
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.1.0"
```

**테스트 예시**:
```python
import pytest
from app.core.scraper import search_tiktok

@pytest.mark.asyncio
async def test_search_tiktok():
    results = await search_tiktok("football", limit=10)
    assert len(results) == 10
    assert results[0]['views'] > 0
```

---

#### Black 23.12+
```toml
black = "^23.12.0"
```

**설정** (`pyproject.toml`):
```toml
[tool.black]
line-length = 100
target-version = ['py310']
include = '\.pyi?$'
```

**실행**:
```bash
black app/
```

---

#### Ruff (빠른 린터)
```toml
ruff = "^0.1.0"
```

**설정** (`pyproject.toml`):
```toml
[tool.ruff]
line-length = 100
select = ["E", "F", "I"]
ignore = ["E501"]
```

---

### 4.2 버전 관리

#### Poetry (권장)
```toml
[tool.poetry]
name = "ranking-shorts-generator"
version = "1.0.0"
description = "Automated ranking shorts generator"
authors = ["Your Name <email@example.com>"]

[tool.poetry.dependencies]
python = "^3.10"
fastapi = "^0.109.0"
# ... 기타 의존성

[tool.poetry.dev-dependencies]
pytest = "^7.4.0"
black = "^23.12.0"
```

**설치**:
```bash
poetry install
```

**실행**:
```bash
poetry run uvicorn app.main:app
```

---

#### pip-tools (대안)
```bash
pip install pip-tools
```

**requirements.in**:
```
fastapi
uvicorn[standard]
sqlalchemy
celery[redis]
```

**컴파일**:
```bash
pip-compile requirements.in
pip install -r requirements.txt
```

---

## 5. 의존성 관리 전략

### 5.1 Frontend (package.json)
```json
{
  "name": "ranking-shorts-frontend",
  "version": "1.0.0",
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
    "eslint": "^8.56.0",
    "prettier": "^3.1.0"
  },
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext .js,.jsx",
    "format": "prettier --write src/**/*.{js,jsx}"
  }
}
```

---

### 5.2 Backend (requirements.txt)
```txt
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
alembic==1.13.1

# Task Queue
celery==5.3.4
redis==5.0.1

# Video Processing
moviepy==1.0.3
ffmpeg-python==0.2.0
Pillow==10.2.0

# Scraping
TikTokApi==6.0.0
playwright==1.40.0
beautifulsoup4==4.12.2

# Utilities
pydantic==2.5.3
python-dotenv==1.0.0
aiofiles==23.2.1

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.12.1
ruff==0.1.9
```

---

## 6. 시스템 요구사항

### 6.1 하드웨어 요구사항

**최소 사양**:
- CPU: 4 Core (Intel i5 이상)
- RAM: 8GB
- 저장공간: 100GB SSD
- 네트워크: 10Mbps

**권장 사양**:
- CPU: 8 Core (Intel i7/Ryzen 7 이상)
- RAM: 16GB
- 저장공간: 500GB SSD
- GPU: NVIDIA (NVENC 지원) - 영상 인코딩 가속
- 네트워크: 50Mbps+

---

### 6.2 소프트웨어 요구사항

**운영체제**:
- Ubuntu 22.04 LTS (권장)
- macOS 12+ (Monterey)
- Windows 10/11 (WSL2 권장)

**필수 설치**:
- Python 3.10+
- Node.js 18+
- Redis 7.2+
- FFmpeg 6.0+

**선택 설치**:
- Docker & Docker Compose
- PostgreSQL 15+ (프로덕션)

---

## 7. 설치 가이드

### 7.1 Python & 가상환경
```bash
# Python 버전 확인
python3 --version  # 3.10 이상

# 가상환경 생성
python3 -m venv venv

# 활성화 (Linux/Mac)
source venv/bin/activate

# 활성화 (Windows)
venv\Scripts\activate

# 의존성 설치
pip install -r backend/requirements.txt
```

---

### 7.2 Node.js & Frontend
```bash
# Node.js 버전 확인
node --version  # 18 이상

# 의존성 설치
cd frontend
npm install

# 개발 서버 실행
npm run dev
```

---

### 7.3 Redis
```bash
# Ubuntu
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# macOS
brew install redis
brew services start redis

# 확인
redis-cli ping
```

---

### 7.4 FFmpeg
```bash
# Ubuntu
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows (Chocolatey)
choco install ffmpeg

# 확인
ffmpeg -version
```

---

### 7.5 Playwright (TikTokApi용)
```bash
pip install playwright
playwright install chromium
```

---

## 8. 개발 환경 설정

### 8.1 VSCode 추천 확장

**Frontend**:
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- ES7+ React/Redux/React-Native snippets

**Backend**:
- Python
- Pylance
- Black Formatter
- autoDocstring

**공통**:
- GitLens
- Docker
- REST Client

---

### 8.2 환경변수 설정

**Backend** (`.env`):
```env
# Database
DATABASE_URL=sqlite:///./app.db

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Storage
STORAGE_PATH=./storage
TEMP_PATH=./storage/temp
OUTPUT_PATH=./storage/output

# API
API_V1_PREFIX=/api/v1
SECRET_KEY=your-secret-key-change-in-production

# CORS
FRONTEND_URL=http://localhost:5173
```

**Frontend** (`.env`):
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

---

## 9. 성능 최적화

### 9.1 Python 최적화
- **uvloop**: 더 빠른 이벤트 루프
  ```toml
  uvloop = "^0.19.0"
  ```

- **orjson**: 더 빠른 JSON 직렬화
  ```toml
  orjson = "^3.9.0"
  ```

---

### 9.2 Frontend 최적화
- **vite-plugin-compression**: Gzip/Brotli 압축
  ```json
  {
    "vite-plugin-compression": "^0.5.1"
  }
  ```

- **Code Splitting**: 라우트 기반 분할
  ```javascript
  const SearchPage = lazy(() => import('./pages/SearchPage'))
  ```

---

## 10. 라이선스

### 10.1 오픈소스 라이선스 확인

| 라이브러리 | 라이선스 | 상업적 사용 |
|-----------|---------|-----------|
| React | MIT | ✅ |
| FastAPI | MIT | ✅ |
| FFmpeg | LGPL/GPL | ⚠️ (동적 링크 시 OK) |
| TikTokApi | MIT | ✅ |
| MoviePy | MIT | ✅ |
| Celery | BSD | ✅ |

**주의사항**:
- FFmpeg: GPL 라이선스 플러그인 사용 시 주의
- TikTokApi: TikTok 이용약관 확인 필요

---

## 11. 업데이트 및 유지보수

### 11.1 의존성 업데이트

**Frontend**:
```bash
npm outdated
npm update
```

**Backend**:
```bash
pip list --outdated
pip install --upgrade <package>
```

### 11.2 보안 취약점 확인

**Frontend**:
```bash
npm audit
npm audit fix
```

**Backend**:
```bash
pip install safety
safety check
```

---

**문서 버전**: 1.0
**작성일**: 2025-10-19
**최종 수정일**: 2025-10-19
