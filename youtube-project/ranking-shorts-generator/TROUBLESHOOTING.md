# 트러블슈팅 가이드

프로젝트 설정 중 발생한 문제들과 해결 방법을 정리한 문서입니다.

## 목차
1. [Frontend 이슈](#frontend-이슈)
2. [Backend 이슈](#backend-이슈)
3. [환경 설정 이슈](#환경-설정-이슈)
4. [데이터베이스 이슈](#데이터베이스-이슈)
5. [의존성 설치 이슈](#의존성-설치-이슈)

---

## Frontend 이슈

### 1. npm install이 멈춘 것처럼 보임

**증상:**
```bash
npm install
⠴  # 스피너만 계속 돌아감
```

**원인:**
- npm install은 정상적으로 진행 중
- 대량의 패키지(300+) 다운로드로 시간이 오래 걸림

**해결방법:**
```bash
# 3-5분 정도 기다리면 완료됨
# 진행 상황 확인이 필요하면:
npm install --verbose
```

**예상 소요 시간:** 3-5분 (네트워크 속도에 따라 다름)

---

### 2. Tailwind CSS 컴파일 에러

**증상:**
```
Error: The `border-border` class does not exist
```

**원인:**
- `index.css`에 정의되지 않은 Tailwind 클래스 사용
- Tailwind 설정에 해당 색상이 정의되지 않음

**해결방법:**
`frontend/src/index.css` 수정:
```css
@layer base {
  body {
    @apply bg-gray-50 text-gray-900 antialiased;
    /* border-border 제거 */
    font-family: 'Inter', system-ui, sans-serif;
  }
}
```

**파일 위치:** `frontend/src/index.css:6-9`

---

## Backend 이슈

### 1. pydantic_settings 모듈을 찾을 수 없음

**증상:**
```python
ModuleNotFoundError: No module named 'pydantic_settings'
```

**원인:**
- `pydantic-settings` 패키지가 requirements.txt에 누락됨
- Pydantic v2에서는 별도 패키지로 분리됨

**해결방법:**
`backend/requirements.txt`에 추가:
```txt
pydantic==2.5.3
pydantic-settings==2.1.0  # 이 줄 추가
```

그 후 설치:
```bash
pip install pydantic-settings==2.1.0
```

---

### 2. ALLOWED_ORIGINS 파싱 에러

**증상:**
```python
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
error parsing value for field "ALLOWED_ORIGINS" from source "DotEnvSettingsSource"
```

**원인:**
- `.env` 파일의 `ALLOWED_ORIGINS`가 잘못된 형식
- CSV 형식 대신 JSON 배열 형식 필요

**해결방법:**
`backend/.env` 수정:

❌ **잘못된 형식:**
```env
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

✅ **올바른 형식:**
```env
ALLOWED_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

**파일 위치:** `backend/.env:25`

---

### 3. app.database 모듈을 찾을 수 없음

**증상:**
```python
ModuleNotFoundError: No module named 'app.database'
```

**원인:**
- 데이터베이스 설정 파일이 누락됨
- SQLAlchemy 설정이 필요함

**해결방법:**
`backend/app/database.py` 파일 생성:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# SQLite 엔진 생성
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite용
)

# Session 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스
Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

### 4. 모델 클래스 Import 에러

**증상:**
```python
ImportError: cannot import name 'FinalVideo' from 'app.models.project'
ImportError: cannot import name 'SearchCreate' from 'app.schemas.search'
ImportError: cannot import name 'ProjectDetailResponse' from 'app.schemas.project'
```

**원인:**
- 모델/스키마 파일에 필요한 클래스가 정의되지 않음
- 중복 정의로 인한 충돌

**해결방법:**

#### 1) FinalVideo 모델 추가
`backend/app/models/project.py`에 추가:
```python
class FinalVideo(Base):
    __tablename__ = "final_videos"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"))
    file_path = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### 2) Search 스키마 추가
`backend/app/schemas/search.py`에 추가:
```python
class SearchCreate(BaseModel):
    keyword: str
    limit: int = 30


class SearchResponse(BaseModel):
    id: str
    keyword: str
    status: str
    total_found: int
    task_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SearchDetailResponse(BaseModel):
    id: str
    keyword: str
    status: str
    total_found: int
    task_id: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    videos: List[dict] = []

    class Config:
        from_attributes = True
```

#### 3) Project 스키마 추가
`backend/app/schemas/project.py`에 추가:
```python
class ProjectDetailResponse(BaseModel):
    id: str
    name: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    videos: List[dict] = []
    settings: Optional[Dict] = None
    task_id: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    settings: Optional[Dict] = None
```

#### 4) Video 스키마 추가
`backend/app/schemas/video.py`에 추가:
```python
class VideoDetailResponse(BaseModel):
    id: str
    tiktok_id: str
    thumbnail_url: str
    title: str
    description: Optional[str] = None
    views: int
    likes: int
    comments: int
    shares: int
    duration: int
    download_url: str
    author_username: Optional[str] = None
    file_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
```

---

### 5. SQLAlchemy 테이블 중복 정의 에러

**증상:**
```python
sqlalchemy.exc.InvalidRequestError: Table 'final_videos' is already defined for this MetaData instance.
Specify 'extend_existing=True' to redefine options and columns on an existing Table object.
```

**원인:**
- 같은 모델이 여러 파일에 정의됨
- `app/models/final_video.py`와 `app/models/project.py`에 중복 정의

**해결방법:**
```bash
# 중복 파일 제거
rm backend/app/models/final_video.py
```

`backend/app/models/__init__.py` 수정:
```python
from app.models.search import Search
from app.models.video import Video
from app.models.project import Project, ProjectVideo, FinalVideo  # FinalVideo를 여기서 import

__all__ = ["Search", "Video", "Project", "ProjectVideo", "FinalVideo"]
```

---

## 의존성 설치 이슈

### 1. yt-dlp 버전을 찾을 수 없음

**증상:**
```
ERROR: No matching distribution found for yt-dlp==2024.1.0
```

**원인:**
- 존재하지 않는 버전 지정
- yt-dlp는 자주 업데이트되는 패키지

**해결방법:**
`backend/requirements.txt` 수정:
```txt
# 특정 버전 대신 최소 버전 지정
yt-dlp>=2024.10.7
```

---

### 2. TikTokApi 설치 에러

**증상:**
```python
FileNotFoundError: [Errno 2] No such file or directory: '.../TikTokApi/stealth/js/chrome.csi.js'
```

**원인:**
- TikTokApi 6.0.0 버전의 패키징 이슈
- 필요한 JS 파일이 패키지에 포함되지 않음

**해결방법:**
```bash
# 잘못된 버전 제거
pip uninstall -y TikTokApi

# 안정적인 버전 설치
pip install TikTokApi==5.2.2
```

`backend/requirements.txt` 수정:
```txt
# 안정적인 버전으로 고정
TikTokApi==5.2.2
```

---

### 3. 누락된 Python 패키지들

**증상:**
```python
ModuleNotFoundError: No module named 'tenacity'
ModuleNotFoundError: No module named 'yt_dlp'
ModuleNotFoundError: No module named 'ffmpeg'
ModuleNotFoundError: No module named 'moviepy'
```

**해결방법:**
```bash
# 한 번에 설치
pip install tenacity==8.2.3
pip install yt-dlp
pip install ffmpeg-python==0.2.0
pip install moviepy==1.0.3

# 또는 requirements.txt에서 한 번에
pip install -r requirements.txt
```

---

## 환경 설정 이슈

### Docker Desktop이 실행되지 않음

**증상:**
```
docker: request returned Internal Server Error for API route
```

**원인:**
- Docker Desktop이 설치되지 않았거나 실행 중이 아님
- WSL 환경에서 Docker 설정 문제

**해결방법 1: 로컬 Redis 사용 (권장)**
```bash
# Ubuntu/WSL
sudo apt-get update
sudo apt-get install redis-server

# Redis 서버 실행
redis-server

# 다른 터미널에서 작동 확인
redis-cli ping
# 응답: PONG
```

**해결방법 2: Docker 설치**
```bash
# WSL2에서 Docker Desktop 사용
# Windows에서 Docker Desktop 설치 후
# Settings > Resources > WSL Integration 활성화
```

---

## 데이터베이스 이슈

### SQLite 데이터베이스 초기화

**데이터베이스 파일 생성:**
```bash
cd backend

# 데이터베이스 마이그레이션
alembic upgrade head

# 또는 Python에서 직접 생성
python -c "from app.database import engine; from app.models import *; Base.metadata.create_all(bind=engine)"
```

**데이터베이스 위치:** `backend/app.db`

---

## 전체 설정 체크리스트

### Backend 시작 전 체크리스트

- [ ] `.env` 파일 존재 및 형식 확인
- [ ] `ALLOWED_ORIGINS`이 JSON 배열 형식인지 확인
- [ ] `app/database.py` 파일 존재 확인
- [ ] 모든 필수 Python 패키지 설치 확인
- [ ] Redis 서버 실행 중인지 확인
- [ ] SQLite 데이터베이스 초기화 확인

### Frontend 시작 전 체크리스트

- [ ] `node_modules` 폴더 존재 (npm install 완료)
- [ ] `.env` 파일에 백엔드 URL 설정 확인
- [ ] Tailwind CSS 설정 파일 확인

### 전체 시스템 시작 순서

```bash
# 1. Redis 시작 (터미널 1)
redis-server

# 2. Backend 시작 (터미널 2)
cd backend
uvicorn app.main:app --reload

# 3. Celery Worker 시작 (터미널 3)
cd backend
celery -A celery_app worker --loglevel=info

# 4. Frontend 시작 (터미널 4)
cd frontend
npm run dev
```

---

## 디버깅 팁

### Python Import 에러 디버깅

```bash
# 특정 모듈 import 테스트
cd backend
python -c "from app.main import app; print('Success!')"

# 에러 발생 시 상세 정보 확인
python -c "from app.main import app" 2>&1 | grep -A 5 "Error"
```

### 환경 변수 확인

```bash
# .env 파일 로드 확인
cd backend
python -c "from app.config import settings; print(settings.DATABASE_URL)"
```

### 서비스 상태 확인

```bash
# Redis 연결 확인
redis-cli ping

# Backend API 확인
curl http://localhost:8000/health

# Celery Worker 확인
celery -A celery_app inspect active
```

---

## 자주 묻는 질문 (FAQ)

### Q: pip install이 너무 느려요

**A:** 미러 사이트 사용:
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: uvicorn 실행 시 포트가 이미 사용 중이라고 나와요

**A:** 포트 변경 또는 프로세스 종료:
```bash
# 다른 포트 사용
uvicorn app.main:app --reload --port 8001

# 또는 기존 프로세스 종료
lsof -ti:8000 | xargs kill -9
```

### Q: Celery Worker가 작업을 실행하지 않아요

**A:** Redis 연결 및 Celery 설정 확인:
```bash
# Redis 연결 확인
redis-cli ping

# Celery 설정 확인
python -c "from celery_app import celery_app; print(celery_app.conf.broker_url)"

# Worker 재시작
celery -A celery_app worker --loglevel=debug
```

---

## 추가 도움말

문제가 계속 발생하면:
1. 에러 메시지 전체 복사
2. 실행한 명령어 기록
3. 환경 정보 확인: Python 버전, OS, Node 버전
4. GitHub Issues에 상세히 작성

**환경 정보 확인:**
```bash
python --version
node --version
npm --version
redis-server --version
```
