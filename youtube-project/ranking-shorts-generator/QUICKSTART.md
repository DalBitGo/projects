# 🚀 빠른 시작 가이드

이 문서는 프로젝트를 처음 실행하는 분들을 위한 단계별 가이드입니다.

## 📋 사전 준비

### 필수 소프트웨어 설치

1. **Python 3.11+**
   ```bash
   python --version  # 3.11 이상인지 확인
   ```

2. **Node.js 18+**
   ```bash
   node --version  # 18 이상인지 확인
   npm --version
   ```

3. **Redis**
   ```bash
   # Docker로 설치 (권장)
   docker pull redis:latest

   # 또는 직접 설치
   # Ubuntu/Debian: sudo apt-get install redis-server
   # macOS: brew install redis
   # Windows: https://redis.io/download
   ```

4. **FFmpeg**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg

   # macOS
   brew install ffmpeg

   # Windows
   # https://ffmpeg.org/download.html 에서 다운로드

   # 설치 확인
   ffmpeg -version
   ```

## 🔧 프로젝트 설정

### 1단계: Backend 설정

```bash
# 프로젝트 루트로 이동
cd /home/junhyun/youtube-project/ranking-shorts-generator

# Backend 디렉토리로 이동
cd backend

# Python 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Linux/Mac:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 의존성 설치 (2-3분 소요)
pip install -r requirements.txt

# Playwright 브라우저 설치 (TikTok 스크래핑용)
playwright install

# 환경 변수 설정
cp .env.example .env

# .env 파일 내용 확인 (수정 필요 시)
cat .env
```

### 2단계: Frontend 설정

```bash
# 프로젝트 루트로 이동
cd /home/junhyun/youtube-project/ranking-shorts-generator

# Frontend 디렉토리로 이동
cd frontend

# Node.js 의존성 설치 (2-3분 소요)
npm install

# 환경 변수 설정
cp .env.example .env

# .env 파일 내용 확인
cat .env
```

### 3단계: 저장소 디렉토리 생성

```bash
# 프로젝트 루트로 이동
cd /home/junhyun/youtube-project/ranking-shorts-generator

# 저장소 디렉토리 생성
mkdir -p storage/downloads
mkdir -p storage/outputs
mkdir -p storage/music
mkdir -p storage/temp
mkdir -p storage/thumbnails

# 권한 확인
ls -la storage/
```

## 🚀 실행 방법

### 실행 순서

**총 4개의 터미널이 필요합니다.**

#### 터미널 1: Redis 실행

```bash
# Docker 사용 시 (권장)
docker run -d -p 6379:6379 --name ranking-redis redis:latest

# 또는 로컬 설치된 Redis
redis-server

# Redis 실행 확인
redis-cli ping
# 응답: PONG
```

#### 터미널 2: Celery Worker 실행

```bash
cd /home/junhyun/youtube-project/ranking-shorts-generator/backend

# 가상환경 활성화
source venv/bin/activate

# Celery Worker 실행
celery -A celery_app worker --loglevel=info --concurrency=4

# 성공 시 출력:
# [tasks]
#   . app.core.tasks.scrape_tiktok_task
#   . app.core.tasks.download_video_task
#   . app.core.tasks.generate_ranking_video_task
#   ...
```

#### 터미널 3: FastAPI Backend 실행

```bash
cd /home/junhyun/youtube-project/ranking-shorts-generator/backend

# 가상환경 활성화
source venv/bin/activate

# FastAPI 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 성공 시 출력:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete.
```

**API 문서 확인**: http://localhost:8000/api/v1/docs

#### 터미널 4: Frontend 실행

```bash
cd /home/junhyun/youtube-project/ranking-shorts-generator/frontend

# Vite 개발 서버 실행
npm run dev

# 성공 시 출력:
# VITE v5.x.x  ready in xxx ms
# ➜  Local:   http://localhost:3000/
```

**웹 접속**: http://localhost:3000

## 🎯 사용 방법

### 1단계: 검색
1. 브라우저에서 http://localhost:3000 접속
2. 검색 키워드 입력 (예: "football", "skills", "goals")
3. 검색 결과 수 선택 (30개 권장)
4. "검색 시작" 버튼 클릭
5. 자동으로 선택 페이지로 이동

### 2단계: 영상 선택
1. 검색 결과에서 원하는 영상 클릭 (3~10개)
2. 선택된 영상에 체크 표시 확인
3. "다음 단계로" 버튼 클릭

### 3단계: 영상 생성
1. 선택된 영상 목록 확인
2. "영상 생성 시작" 버튼 클릭
3. 실시간 진행 상황 확인 (3~5분 소요)
4. 완료 시 자동으로 미리보기로 이동

### 4단계: 미리보기 & 다운로드
1. 생성된 영상 재생 확인
2. "영상 다운로드" 버튼 클릭
3. 다운로드된 영상을 YouTube Shorts에 업로드

## 🐛 문제 해결

### 1. Redis 연결 오류
```bash
# Redis 실행 확인
redis-cli ping

# Docker Redis 재시작
docker restart ranking-redis

# 포트 충돌 확인
lsof -i :6379
```

### 2. Backend 실행 오류
```bash
# 가상환경이 활성화되었는지 확인
which python
# /home/junhyun/.../backend/venv/bin/python 이어야 함

# 의존성 재설치
pip install -r requirements.txt --force-reinstall

# 데이터베이스 초기화
rm -f app.db
python -c "from app.database import engine, Base; Base.metadata.create_all(engine)"
```

### 3. Frontend 실행 오류
```bash
# node_modules 삭제 후 재설치
rm -rf node_modules package-lock.json
npm install

# 캐시 삭제
npm cache clean --force
```

### 4. Celery Worker 연결 안됨
```bash
# Redis 연결 확인
redis-cli ping

# Celery Worker 재시작
# Ctrl+C로 종료 후 다시 실행
celery -A celery_app worker --loglevel=info --concurrency=4
```

### 5. TikTok 스크래핑 오류
```bash
# Playwright 재설치
playwright install

# 브라우저 의존성 설치 (Linux)
playwright install-deps
```

### 6. FFmpeg 오류
```bash
# FFmpeg 설치 확인
ffmpeg -version

# MoviePy 재설치
pip uninstall moviepy
pip install moviepy==1.0.3
```

### 7. 포트 충돌
```bash
# 사용 중인 포트 확인
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
lsof -i :6379  # Redis

# 프로세스 종료
kill -9 <PID>
```

## 📊 실행 상태 확인

### Backend 상태 확인
```bash
# API Health Check
curl http://localhost:8000/health
# 응답: {"status":"healthy"}

# API 문서 접속
firefox http://localhost:8000/api/v1/docs
```

### Celery 상태 확인
```bash
# Celery 상태 확인
celery -A celery_app inspect active

# 등록된 Task 확인
celery -A celery_app inspect registered
```

### Redis 상태 확인
```bash
# Redis 연결 테스트
redis-cli ping

# Redis 모니터링
redis-cli monitor
```

## 🔄 재시작 방법

### 전체 재시작
```bash
# 1. 모든 프로세스 종료
pkill -f uvicorn
pkill -f celery
pkill -f "npm run dev"
docker stop ranking-redis

# 2. Redis 재시작
docker start ranking-redis

# 3. 터미널 2: Celery 재실행
cd backend && source venv/bin/activate
celery -A celery_app worker --loglevel=info --concurrency=4

# 4. 터미널 3: Backend 재실행
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. 터미널 4: Frontend 재실행
cd frontend
npm run dev
```

## 📁 중요 파일 위치

```
ranking-shorts-generator/
├── backend/
│   ├── app.db                    # SQLite 데이터베이스
│   ├── .env                      # Backend 환경 변수
│   └── app/main.py               # Backend 진입점
├── frontend/
│   ├── .env                      # Frontend 환경 변수
│   └── src/main.jsx              # Frontend 진입점
├── storage/
│   ├── downloads/                # 다운로드된 원본 영상
│   ├── outputs/                  # 생성된 최종 영상
│   ├── temp/                     # 임시 파일
│   └── music/                    # 배경음악 파일
└── docs/
    └── PROGRESS.md               # 구현 진행 상황
```

## ⚙️ 환경 변수 설정

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

## 📝 테스트 시나리오

### 기본 워크플로우 테스트
1. ✅ 검색: "football" 키워드로 30개 검색
2. ✅ 선택: 5개 영상 선택
3. ✅ 생성: 영상 생성 시작 및 진행 상황 확인
4. ✅ 미리보기: 생성된 영상 재생 확인
5. ✅ 다운로드: 영상 다운로드

### API 테스트
```bash
# 검색 API 테스트
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"keyword": "football", "limit": 30}'

# 프로젝트 목록 조회
curl http://localhost:8000/api/v1/projects
```

## 🎓 추가 학습 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [React 공식 문서](https://react.dev/)
- [Celery 공식 문서](https://docs.celeryq.dev/)
- [FFmpeg 문서](https://ffmpeg.org/documentation.html)

## 💡 유용한 명령어

```bash
# Backend 로그 실시간 확인
tail -f backend/logs/app.log

# 데이터베이스 내용 확인
sqlite3 backend/app.db "SELECT * FROM searches;"

# 저장소 사용량 확인
du -sh storage/*

# 임시 파일 정리
rm -rf storage/temp/*
```

## 🆘 도움말

문제가 해결되지 않으면:
1. 터미널의 에러 메시지를 확인하세요
2. `docs/PROGRESS.md`에서 구현 상태를 확인하세요
3. `README.md`의 상세 가이드를 참고하세요
4. GitHub Issues에 질문을 남겨주세요

---

**🎉 모든 준비가 완료되었습니다!**

위 단계를 순서대로 따라하시면 완벽하게 작동하는 랭킹 쇼츠 생성기를 사용할 수 있습니다.
