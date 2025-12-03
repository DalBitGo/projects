# 🎬 Ranking Shorts Generator

TikTok 영상을 자동으로 수집하여 랭킹 형태의 YouTube Shorts를 생성하는 웹 애플리케이션입니다.

## 📋 프로젝트 개요

이 프로젝트는 TikTok에서 인기 영상을 검색하고, 사용자가 선택한 영상들을 자동으로 편집하여 랭킹 형태의 쇼츠 영상(9:16 비율)을 생성합니다.

### 주요 기능

- ✅ **TikTok 영상 자동 검색** - 키워드 기반 인기 영상 수집
- ✅ **영상 선택 및 순서 지정** - 드래그 앤 드롭으로 쉬운 순서 조정
- ✅ **자동 영상 편집**
  - 9:16 비율로 크롭 및 리사이즈
  - 각 영상 7초로 자동 트림
  - 랭킹 텍스트 오버레이 (🥇 #1, 🥈 #2, 🥉 #3)
  - 배경음악 자동 추가
- ✅ **실시간 진행 상황** - WebSocket을 통한 실시간 업데이트
- ✅ **미리보기 및 다운로드** - 생성된 영상 즉시 확인 및 다운로드

## 🏗️ 시스템 아키텍처

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Frontend   │─────▶│   Backend   │─────▶│   Celery    │
│ React+Vite  │      │   FastAPI   │      │   Workers   │
└─────────────┘      └─────────────┘      └─────────────┘
                           │                      │
                           ▼                      ▼
                     ┌──────────┐          ┌──────────┐
                     │ SQLite   │          │  Redis   │
                     │ Database │          │  Queue   │
                     └──────────┘          └──────────┘
```

## 🛠️ 기술 스택

### Backend
- **FastAPI** - 고성능 웹 프레임워크
- **SQLAlchemy** - ORM 및 데이터베이스 관리
- **Celery** - 비동기 작업 큐
- **Redis** - 메시지 브로커
- **FFmpeg** - 영상 처리
- **MoviePy** - 영상 합성 및 텍스트 오버레이
- **yt-dlp** - TikTok 영상 다운로드
- **TikTokApi** - TikTok 스크래핑

### Frontend
- **React 18** - UI 라이브러리
- **Vite** - 빌드 도구
- **Tailwind CSS** - 스타일링
- **Zustand** - 상태 관리
- **React Router** - 라우팅
- **Socket.IO** - WebSocket 실시간 통신
- **Axios** - HTTP 클라이언트

## 📦 설치 방법

### 1. 사전 요구사항

- Python 3.11+
- Node.js 18+
- FFmpeg
- Redis
- Git

### 2. 저장소 클론

```bash
git clone <repository-url>
cd ranking-shorts-generator
```

### 3. Backend 설정

```bash
cd backend

# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (Linux/Mac)
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# Playwright 브라우저 설치 (TikTokApi용)
playwright install

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 필요한 설정 수정
```

### 4. Frontend 설정

```bash
cd ../frontend

# 의존성 설치
npm install

# 환경 변수 설정
cp .env.example .env
```

### 5. Redis 실행

```bash
# Docker 사용 시
docker run -d -p 6379:6379 redis:latest

# 또는 로컬에 설치된 Redis 실행
redis-server
```

## 🚀 실행 방법

### Backend 실행

터미널 3개를 열어 각각 다음 명령어를 실행합니다:

#### 터미널 1: FastAPI 서버
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 터미널 2: Celery Worker
```bash
cd backend
celery -A celery_app worker --loglevel=info --concurrency=4
```

#### 터미널 3: Celery Beat (선택사항 - 주기적 작업용)
```bash
cd backend
celery -A celery_app beat --loglevel=info
```

### Frontend 실행

```bash
cd frontend
npm run dev
```

브라우저에서 `http://localhost:3000` 접속

## 📖 사용 방법

### 1단계: 검색
1. 메인 페이지에서 검색 키워드 입력 (예: "football", "skills")
2. 검색 결과 수 선택 (20~100개)
3. "검색 시작" 버튼 클릭

### 2단계: 선택
1. 검색 결과에서 원하는 영상 선택 (3~10개)
2. 선택한 영상의 순서는 나중에 조정 가능
3. "다음 단계로" 버튼 클릭

### 3단계: 생성
1. 선택한 영상 목록 확인
2. "영상 생성 시작" 버튼 클릭
3. 진행 상황을 실시간으로 확인
4. 완료까지 약 3~5분 소요

### 4단계: 미리보기 & 다운로드
1. 생성된 영상 미리보기
2. "영상 다운로드" 버튼으로 다운로드
3. YouTube Shorts에 업로드

## 🔧 환경 변수

### Backend (.env)
```env
DATABASE_URL=sqlite:///./app.db
REDIS_URL=redis://localhost:6379/0
STORAGE_PATH=../storage
API_V1_PREFIX=/api/v1
ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000
```

## 🎯 API 엔드포인트

### Search
- `POST /api/v1/search` - 검색 시작
- `GET /api/v1/search` - 검색 목록
- `GET /api/v1/search/{id}` - 검색 상세
- `GET /api/v1/search/{id}/status` - 검색 진행 상황

### Projects
- `POST /api/v1/projects` - 프로젝트 생성
- `GET /api/v1/projects` - 프로젝트 목록
- `POST /api/v1/projects/{id}/videos` - 영상 추가
- `POST /api/v1/projects/{id}/generate` - 영상 생성 시작
- `GET /api/v1/projects/{id}/status` - 생성 진행 상황

### Videos
- `GET /api/v1/videos` - 영상 목록
- `POST /api/v1/videos/{id}/download` - 영상 다운로드
- `POST /api/v1/videos/download-batch` - 일괄 다운로드

### WebSocket
- `WS /ws/{client_id}` - 실시간 통신

API 문서: `http://localhost:8000/api/v1/docs`

## 🐛 문제 해결

### FFmpeg 관련 오류
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# https://ffmpeg.org/download.html 에서 다운로드
```

### TikTokApi 오류
```bash
# Playwright 재설치
playwright install chromium
```

### Redis 연결 오류
```bash
# Redis가 실행 중인지 확인
redis-cli ping
# 응답: PONG
```

## 📚 상세 문서

- [프로젝트 요약](docs/00-project-summary.md)
- [프로젝트 개요](docs/01-project-overview.md)
- [시스템 아키텍처](docs/02-system-architecture.md)
- [기술 스택](docs/03-tech-stack.md)
- [스크래핑 설계](docs/04-scraping-design.md)
- [영상 처리](docs/05-video-processing.md)
- [Frontend UI/UX](docs/06-frontend-ui-ux.md)
- [Backend API](docs/07-backend-api.md)
- [폴더 구조](docs/08-folder-structure.md)
- [사용자 워크플로우](docs/09-user-workflow.md)
- [배포 가이드](docs/10-deployment-guide.md)
- [구현 진행 상황](docs/PROGRESS.md)

## 📄 라이선스

MIT License

## 👥 기여

버그 리포트 및 기능 제안은 GitHub Issues를 이용해주세요.

---

**🤖 Generated with Claude Code**
**개발 일자**: 2025-01-19
