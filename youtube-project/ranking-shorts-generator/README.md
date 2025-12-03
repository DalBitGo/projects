# TikTok Ranking Shorts Generator

TikTok 영상을 검색하고 자동으로 랭킹 쇼츠 영상을 생성하는 풀스택 애플리케이션입니다.

## 주요 기능

- 🔍 TikTok 키워드 검색 및 영상 수집
- 📊 조회수, 좋아요, 댓글 기반 영상 랭킹
- 🎬 자동 랭킹 쇼츠 영상 생성
- ⚡ 실시간 진행 상황 모니터링
- 💾 검색 기록 및 프로젝트 관리

## 기술 스택

### Frontend
- React 18
- Vite
- Tailwind CSS
- Axios

### Backend
- FastAPI
- SQLAlchemy
- Celery
- Redis
- SQLite

### 영상 처리
- FFmpeg
- MoviePy
- yt-dlp
- TikTokApi

## 빠른 시작

### 필수 요구사항

- Node.js 18+
- Python 3.10+
- Docker (Redis용)
- FFmpeg

### 1. 저장소 클론

```bash
git clone <repository-url>
cd ranking-shorts-generator
```

### 2. 한 번에 모든 서비스 시작

```bash
./start-dev.sh
```

이 명령어는 다음을 자동으로 실행합니다:
- ✅ Redis 컨테이너 시작
- ✅ Backend API 서버 (포트 8000)
- ✅ Celery Worker
- ✅ Frontend 개발 서버 (포트 3000)

### 3. 서비스 접속

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API 문서:** http://localhost:8000/docs

### 4. 서비스 중지

```bash
./stop-dev.sh
```

### 5. 서비스 상태 확인

```bash
./status-dev.sh
```

## 수동 설치 (선택사항)

자동 스크립트 없이 수동으로 설정하려면:

### Backend 설정

```bash
cd backend

# Python 패키지 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env

# 데이터베이스 초기화
alembic upgrade head

# 서버 실행
uvicorn app.main:app --reload
```

### Frontend 설정

```bash
cd frontend

# 패키지 설치
npm install

# 개발 서버 실행
npm run dev
```

### Redis 실행

```bash
docker run -d -p 6379:6379 --name ranking-redis redis:latest
```

### Celery Worker 실행

```bash
cd backend
celery -A celery_app worker --loglevel=info
```

## 사용 방법

### 1. TikTok 영상 검색

1. Frontend에서 키워드 입력 (예: "춤", "요리")
2. 검색 개수 설정 (기본: 30개)
3. "검색 시작" 클릭
4. 실시간 진행 상황 확인

### 2. 랭킹 쇼츠 생성

1. 검색 결과에서 원하는 영상 선택 (최대 10개)
2. 영상 순서 조정
3. "프로젝트 생성" 클릭
4. 설정 조정 (배경음악, 전환 효과 등)
5. "영상 생성" 클릭

### 3. 결과 다운로드

- 생성 완료 후 자동으로 다운로드 링크 제공
- `storage/output/` 폴더에서도 확인 가능

## 프로젝트 구조

```
ranking-shorts-generator/
├── frontend/              # React 프론트엔드
│   ├── src/
│   │   ├── components/   # UI 컴포넌트
│   │   ├── pages/        # 페이지 컴포넌트
│   │   ├── services/     # API 서비스
│   │   └── App.tsx
│   └── package.json
│
├── backend/              # FastAPI 백엔드
│   ├── app/
│   │   ├── core/        # 핵심 비즈니스 로직
│   │   ├── models/      # 데이터베이스 모델
│   │   ├── routers/     # API 라우터
│   │   ├── schemas/     # Pydantic 스키마
│   │   └── main.py
│   ├── celery_app.py    # Celery 설정
│   └── requirements.txt
│
├── storage/             # 영상 및 데이터 저장
│   ├── downloads/       # 다운로드된 영상
│   ├── thumbnails/      # 썸네일
│   ├── output/          # 생성된 영상
│   └── temp/            # 임시 파일
│
├── docs/                # 문서
├── logs/                # 로그 파일
│
├── start-dev.sh         # 개발 환경 시작
├── stop-dev.sh          # 개발 환경 중지
├── status-dev.sh        # 서비스 상태 확인
│
├── QUICKSTART.md        # 빠른 시작 가이드
├── TROUBLESHOOTING.md   # 트러블슈팅 가이드
└── ARCHITECTURE.md      # 아키텍처 문서
```

## API 엔드포인트

### 검색
- `POST /api/v1/search` - TikTok 검색 시작
- `GET /api/v1/search/{search_id}` - 검색 결과 조회
- `GET /api/v1/search/{search_id}/progress` - 검색 진행 상황

### 프로젝트
- `POST /api/v1/projects` - 프로젝트 생성
- `GET /api/v1/projects/{project_id}` - 프로젝트 조회
- `POST /api/v1/projects/{project_id}/generate` - 영상 생성 시작

### 영상
- `GET /api/v1/videos/{video_id}` - 영상 정보 조회
- `GET /api/v1/videos/{video_id}/download` - 영상 다운로드

## 환경 변수

### Backend (.env)

```env
# Database
DATABASE_URL=sqlite:///./app.db

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Storage
STORAGE_PATH=../storage
DOWNLOADS_PATH=../storage/downloads
OUTPUT_PATH=../storage/output

# API
SECRET_KEY=your-secret-key-here

# CORS
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

## 로그 확인

```bash
# Backend 로그
tail -f logs/backend.log

# Celery 로그
tail -f logs/celery.log

# Frontend 로그
tail -f logs/frontend.log
```

## 문제 해결

문제가 발생하면 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)를 참고하세요.

주요 해결 방법:
- 포트 충돌: `./stop-dev.sh` 실행 후 재시작
- Redis 연결 실패: `docker ps` 확인 후 `docker start ranking-redis`
- Python 패키지 오류: `pip install -r requirements.txt` 재실행

## 개발 가이드

### 코드 스타일

```bash
# Python (Black + Ruff)
cd backend
black .
ruff check .

# Frontend (ESLint + Prettier)
cd frontend
npm run lint
npm run format
```

### 테스트

```bash
# Backend 테스트
cd backend
pytest

# Frontend 테스트
cd frontend
npm test
```

## 운영 환경 배포

운영 환경 배포에 대한 자세한 내용은 [ARCHITECTURE.md](ARCHITECTURE.md)를 참고하세요.

## 라이선스

MIT License

## 기여

이슈 및 풀 리퀘스트를 환영합니다!

## 문서

- [빠른 시작](QUICKSTART.md)
- [아키텍처](ARCHITECTURE.md)
- [트러블슈팅](TROUBLESHOOTING.md)
- [구현 요약](docs/IMPLEMENTATION_SUMMARY.md)

## 지원

문제가 있거나 질문이 있으시면 GitHub Issues를 사용해주세요.
