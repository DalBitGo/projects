# 배포 및 실행 가이드

## 1. 시스템 요구사항

### 1.1 하드웨어
- **CPU**: 4 Core 이상 (Intel i5 / AMD Ryzen 5 이상)
- **RAM**: 8GB 이상 (16GB 권장)
- **저장공간**: 100GB 이상 여유 공간 (SSD 권장)
- **네트워크**: 10Mbps 이상

### 1.2 소프트웨어
- **OS**: Ubuntu 22.04 LTS, macOS 12+, Windows 10/11 (WSL2)
- **Python**: 3.10 이상
- **Node.js**: 18 이상
- **Redis**: 7.2 이상
- **FFmpeg**: 6.0 이상

---

## 2. 로컬 개발 환경 설정

### 2.1 사전 준비

#### Python 설치 확인
```bash
python3 --version
# Python 3.10.x 이상
```

#### Node.js 설치 확인
```bash
node --version
# v18.x.x 이상

npm --version
# 9.x.x 이상
```

#### Redis 설치
```bash
# Ubuntu
sudo apt-get update
sudo apt-get install redis-server

# macOS
brew install redis

# 실행
redis-server

# 확인
redis-cli ping
# PONG
```

#### FFmpeg 설치
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

### 2.2 프로젝트 클론

```bash
cd ~/projects
git clone https://github.com/your-username/ranking-shorts-generator.git
cd ranking-shorts-generator
```

---

### 2.3 Backend 설정

#### 가상환경 생성 및 활성화
```bash
cd backend

# 가상환경 생성
python3 -m venv venv

# 활성화 (Linux/Mac)
source venv/bin/activate

# 활성화 (Windows)
venv\Scripts\activate
```

#### 의존성 설치
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Playwright 브라우저 설치 (TikTok 스크래핑용)
```bash
playwright install chromium
```

#### 환경변수 설정
```bash
cp .env.example .env
nano .env  # 또는 vi, code 등
```

**`.env` 내용**:
```env
# Database
DATABASE_URL=sqlite:///./app.db

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Storage
STORAGE_PATH=../storage
TEMP_PATH=../storage/temp
OUTPUT_PATH=../storage/output

# CORS
FRONTEND_URL=http://localhost:5173

# API
API_V1_PREFIX=/api/v1
SECRET_KEY=your-secret-key-change-this
```

#### 데이터베이스 마이그레이션
```bash
# 마이그레이션 생성
alembic revision --autogenerate -m "Initial migration"

# 마이그레이션 적용
alembic upgrade head
```

#### 저장소 폴더 생성
```bash
cd ..
mkdir -p storage/{downloads,thumbnails,temp,output/{pending,approved},music}
```

---

### 2.4 Frontend 설정

```bash
cd frontend

# 의존성 설치
npm install

# 환경변수 설정
cp .env.example .env
nano .env
```

**`.env` 내용**:
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

---

### 2.5 실행

#### Terminal 1: Redis
```bash
redis-server
```

#### Terminal 2: Backend API
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**출력**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx]
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### Terminal 3: Celery Worker
```bash
cd backend
source venv/bin/activate
celery -A celery_app worker --loglevel=info
```

**출력**:
```
 -------------- celery@hostname v5.3.4 (emerald-rush)
--- ***** -----
-- ******* ---- Linux-5.15.0-91-generic-x86_64-with-glibc2.35 2025-01-19 14:00:00
- *** --- * ---
- ** ---------- [config]
- ** ---------- .> app:         ranking_shorts:0x...
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     redis://localhost:6379/1
- *** --- * --- .> concurrency: 4 (prefork)
-- ******* ---- .> task events: OFF
--- ***** -----
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery

[tasks]
  . app.core.tasks.scrape_tiktok_task
  . app.core.tasks.generate_ranking_video_task
```

#### Terminal 4: Celery Flower (모니터링, 선택사항)
```bash
cd backend
source venv/bin/activate
celery -A celery_app flower --port=5555
```

브라우저에서 http://localhost:5555 접속

#### Terminal 5: Frontend
```bash
cd frontend
npm run dev
```

**출력**:
```
  VITE v5.0.0  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

---

### 2.6 접속 확인

1. **Frontend**: http://localhost:5173
2. **Backend API Docs**: http://localhost:8000/api/docs
3. **Flower (Celery)**: http://localhost:5555

---

## 3. Docker를 사용한 실행

### 3.1 Docker 설치 확인
```bash
docker --version
docker-compose --version
```

### 3.2 Docker Compose 실행
```bash
# 프로젝트 루트에서
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

### 3.3 `docker-compose.yml` 예시
```yaml
version: '3.8'

services:
  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./storage:/app/storage
    environment:
      - DATABASE_URL=sqlite:///./app.db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000

  celery_worker:
    build: ./backend
    volumes:
      - ./storage:/app/storage
    environment:
      - DATABASE_URL=sqlite:///./app.db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    command: celery -A celery_app worker --loglevel=info

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
    command: npm run dev -- --host
```

---

## 4. 프로덕션 배포

### 4.1 PostgreSQL 설정

#### 설치
```bash
# Ubuntu
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql
```

#### 데이터베이스 생성
```bash
sudo -u postgres psql

CREATE DATABASE ranking_shorts;
CREATE USER ranking_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE ranking_shorts TO ranking_user;
\q
```

#### `.env` 업데이트
```env
DATABASE_URL=postgresql://ranking_user:secure_password@localhost:5432/ranking_shorts
```

#### 마이그레이션
```bash
alembic upgrade head
```

---

### 4.2 Nginx 설정

#### 설치
```bash
sudo apt-get install nginx
```

#### 설정 파일
```bash
sudo nano /etc/nginx/sites-available/ranking-shorts
```

**내용**:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend (Static Files)
    location / {
        root /var/www/ranking-shorts/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Static Files (Videos)
    location /storage {
        alias /var/www/ranking-shorts/storage;
        add_header Cache-Control "public, max-age=3600";
    }
}
```

#### 활성화
```bash
sudo ln -s /etc/nginx/sites-available/ranking-shorts /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### 4.3 Gunicorn으로 Backend 실행

#### 설치
```bash
pip install gunicorn
```

#### 실행
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

#### Systemd 서비스 생성
```bash
sudo nano /etc/systemd/system/ranking-shorts-api.service
```

**내용**:
```ini
[Unit]
Description=Ranking Shorts API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/ranking-shorts/backend
Environment="PATH=/var/www/ranking-shorts/backend/venv/bin"
ExecStart=/var/www/ranking-shorts/backend/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

#### 시작
```bash
sudo systemctl start ranking-shorts-api
sudo systemctl enable ranking-shorts-api
sudo systemctl status ranking-shorts-api
```

---

### 4.4 Celery Worker 서비스

```bash
sudo nano /etc/systemd/system/ranking-shorts-celery.service
```

**내용**:
```ini
[Unit]
Description=Ranking Shorts Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/ranking-shorts/backend
Environment="PATH=/var/www/ranking-shorts/backend/venv/bin"
ExecStart=/var/www/ranking-shorts/backend/venv/bin/celery -A celery_app worker --loglevel=info --detach

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start ranking-shorts-celery
sudo systemctl enable ranking-shorts-celery
```

---

### 4.5 SSL/HTTPS 설정 (Let's Encrypt)

```bash
# Certbot 설치
sudo apt-get install certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d your-domain.com

# 자동 갱신 테스트
sudo certbot renew --dry-run
```

---

## 5. 클라우드 배포 (AWS 예시)

### 5.1 EC2 인스턴스 설정

1. **인스턴스 생성**:
   - AMI: Ubuntu 22.04 LTS
   - 인스턴스 타입: t3.medium (2 vCPU, 4GB RAM) 이상
   - 스토리지: 100GB SSD

2. **보안 그룹**:
   - 22 (SSH)
   - 80 (HTTP)
   - 443 (HTTPS)
   - 8000 (Backend API, 개발 시만)

3. **Elastic IP 할당**

---

### 5.2 S3를 사용한 파일 저장

#### AWS CLI 설치 및 설정
```bash
pip install boto3
aws configure
```

#### S3 버킷 생성
```bash
aws s3 mb s3://ranking-shorts-storage
```

#### 코드 수정 (파일 업로드)
```python
import boto3

s3 = boto3.client('s3')

def upload_to_s3(file_path, bucket, key):
    s3.upload_file(file_path, bucket, key)
    return f"https://{bucket}.s3.amazonaws.com/{key}"

# 사용
final_video_path = "storage/output/approved/video.mp4"
s3_url = upload_to_s3(final_video_path, "ranking-shorts-storage", "videos/video.mp4")
```

---

### 5.3 RDS (PostgreSQL) 설정

1. RDS 인스턴스 생성 (PostgreSQL 15)
2. 보안 그룹 설정 (EC2에서 접근 허용)
3. `.env` 업데이트:
   ```env
   DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/ranking_shorts
   ```

---

## 6. 모니터링 및 로깅

### 6.1 로깅 설정

#### Backend 로깅 (`app/utils/logger.py`)
```python
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = RotatingFileHandler('logs/app.log', maxBytes=10*1024*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
```

---

### 6.2 Flower (Celery 모니터링)

```bash
celery -A celery_app flower --port=5555 --basic_auth=admin:secure_password
```

---

### 6.3 프로메테우스 + 그라파나 (선택사항)

#### Prometheus Exporter 설치
```bash
pip install prometheus-client
```

#### FastAPI 통합
```python
from prometheus_client import Counter, Histogram, generate_latest

video_generation_counter = Counter('video_generation_total', 'Total video generations')

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

---

## 7. 백업 및 복구

### 7.1 데이터베이스 백업

#### SQLite
```bash
# 백업
cp app.db backups/app_$(date +%Y%m%d).db

# 복구
cp backups/app_20250119.db app.db
```

#### PostgreSQL
```bash
# 백업
pg_dump ranking_shorts > backups/db_$(date +%Y%m%d).sql

# 복구
psql ranking_shorts < backups/db_20250119.sql
```

---

### 7.2 파일 백업

```bash
# 승인된 영상만 백업
rsync -av storage/output/approved/ backups/videos/

# 전체 백업
tar -czf backups/storage_$(date +%Y%m%d).tar.gz storage/
```

---

## 8. 성능 튜닝

### 8.1 Celery Worker 최적화

```bash
# 워커 수 증가 (CPU 코어 수만큼)
celery -A celery_app worker --concurrency=8

# 메모리 제한 설정
celery -A celery_app worker --max-memory-per-child=500000  # 500MB
```

---

### 8.2 Redis 최적화

```bash
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

---

### 8.3 FFmpeg GPU 가속

```bash
# NVIDIA GPU 사용
ffmpeg -hwaccel cuda -i input.mp4 -c:v h264_nvenc output.mp4
```

---

## 9. 보안 체크리스트

- [ ] 환경변수 `.env` 파일을 Git에서 제외 (.gitignore)
- [ ] `SECRET_KEY` 변경 (프로덕션)
- [ ] HTTPS 설정 (Let's Encrypt)
- [ ] Firewall 설정 (UFW)
- [ ] 데이터베이스 비밀번호 강화
- [ ] CORS 설정 확인 (허용된 도메인만)
- [ ] Rate Limiting 활성화
- [ ] Flower 기본 인증 설정

---

## 10. 트러블슈팅

### 10.1 Redis 연결 실패
```bash
# Redis 실행 확인
redis-cli ping

# Redis 재시작
sudo systemctl restart redis-server
```

---

### 10.2 Celery Worker 미작동
```bash
# Worker 로그 확인
celery -A celery_app worker --loglevel=debug

# Redis 큐 확인
redis-cli
> LLEN celery
```

---

### 10.3 FFmpeg 에러
```bash
# FFmpeg 설치 확인
which ffmpeg
ffmpeg -version

# 권한 확인
chmod +x $(which ffmpeg)
```

---

### 10.4 TikTok 스크래핑 실패
```bash
# Playwright 브라우저 재설치
playwright install --force chromium

# TikTokApi 업데이트
pip install --upgrade TikTokApi
```

---

## 11. 업데이트 및 롤백

### 11.1 코드 업데이트
```bash
git pull origin main

# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart ranking-shorts-api
sudo systemctl restart ranking-shorts-celery

# Frontend
cd ../frontend
npm install
npm run build
sudo cp -r dist/* /var/www/ranking-shorts/frontend/dist/
```

---

### 11.2 롤백
```bash
git checkout <previous-commit-hash>
alembic downgrade -1
sudo systemctl restart ranking-shorts-api
```

---

## 12. FAQ

**Q: 영상 생성이 너무 느려요**
A: Celery Worker 수를 늘리거나 GPU 가속을 활성화하세요.

**Q: 디스크 용량이 부족해요**
A: 임시 파일 자동 삭제 설정을 활성화하거나, 오래된 영상을 정기적으로 정리하세요.

**Q: TikTok 스크래핑이 안 돼요**
A: TikTok 구조 변경 가능성이 있습니다. TikTokApi 라이브러리를 업데이트하세요.

---

**문서 버전**: 1.0
**작성일**: 2025-01-19
**최종 수정일**: 2025-01-19
