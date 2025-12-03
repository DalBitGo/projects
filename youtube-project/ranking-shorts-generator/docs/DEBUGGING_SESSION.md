# 디버깅 세션 기록: "skills" 검색 Network Error 해결

## 문제 상황

**증상:**
- Frontend에서 "skills" 키워드로 검색 시 "Network Error" 발생
- 검색 버튼 클릭 후 즉시 실패

**사용자 경험:**
```
검색 키워드: skills
검색 결과 수: 30개
[검색 시작 버튼 클릭]
→ Network Error ❌
```

---

## 디버깅 과정

### 1단계: Backend 로그 확인

**명령어:**
```bash
# Backend 로그 확인
tail -f logs/backend.log

# 또는 실시간 출력 확인
BashOutput를 통해 uvicorn 로그 확인
```

**발견한 에러:**
```
INFO: 127.0.0.1:50052 - "POST /api/v1/search HTTP/1.1" 500 Internal Server Error

ERROR: Exception in ASGI application
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: searches
[SQL: INSERT INTO searches (id, keyword, status, total_found, task_id, created_at, completed_at) VALUES (?, ?, ?, ?, ?, ?, ?)]
```

**원인 파악:**
- HTTP 500 에러 → Backend 서버 내부 에러
- `no such table: searches` → 데이터베이스 테이블이 생성되지 않음

---

### 2단계: 데이터베이스 테이블 확인

**명령어:**
```bash
cd backend

# 데이터베이스 파일 확인
ls -lh app.db

# 테이블 목록 확인
sqlite3 app.db ".tables"
```

**결과:**
```bash
-rw-r--r-- 1 junhyun junhyun 0 Oct 19 12:31 app.db
# 파일 크기가 0 → 빈 파일!
```

**테이블 목록:**
```
(empty)  # 테이블이 하나도 없음
```

**원인:**
- 데이터베이스 파일은 존재하지만 테이블이 생성되지 않음
- Backend 시작 시 자동 초기화가 되지 않음

---

### 3단계: 첫 번째 시도 - 데이터베이스 초기화

**명령어:**
```bash
cd backend

python -c "
from app.database import engine, Base
from app.models import *
Base.metadata.create_all(bind=engine)
print('Database tables created successfully!')
"
```

**결과:**
```
Database tables created successfully!
```

**테이블 확인:**
```bash
sqlite3 app.db ".tables"
# → (empty)  여전히 비어있음!
```

**문제 발견:**
- `app/database.py`의 `Base`와 `app/db/base.py`의 `Base`가 다른 객체!
- 모델들은 `app.db.base.Base`를 사용하는데, 데이터베이스는 `app.database.Base`를 사용
- 서로 다른 Base를 사용해서 테이블이 생성되지 않음

**파일 내용 확인:**

```python
# app/database.py (잘못됨)
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()  # 새로운 Base

# app/db/base.py
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()  # 또 다른 새로운 Base

# app/models/search.py
from app.db.base import Base  # ← 이 Base를 사용

class Search(Base):  # 이 Base와
    __tablename__ = "searches"

# 데이터베이스는 app/database.py의 Base를 사용
# → 연결이 안 됨!
```

---

### 4단계: Base 클래스 통합

**수정 사항:**

**app/database.py 수정:**
```python
# 변경 전
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# 변경 후
from app.db.base import Base  # 기존 Base 재사용
```

**재초기화:**
```bash
cd backend

# 기존 파일 삭제
rm -f app.db

# 다시 생성
python -c "
from app.db.base import Base
from app.database import engine
from app.models import Search, Video, Project, ProjectVideo, FinalVideo

Base.metadata.create_all(bind=engine)

from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f'Created tables: {tables}')
"
```

**결과:**
```
Created tables: ['final_videos', 'project_videos', 'projects', 'searches', 'videos']
```

**성공!** 5개 테이블 모두 생성됨 ✅

---

### 5단계: API 테스트

**명령어:**
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "skills", "limit": 30}'
```

**첫 번째 결과:**
```
Internal Server Error
```

**에러 로그:**
```
sqlite3.OperationalError: attempt to write a readonly database
```

**새로운 문제 발견:**
- 데이터베이스 파일에 쓰기 권한이 없음
- 또는 Backend 서버가 이전 데이터베이스 파일을 캐시하고 있음

---

### 6단계: Backend 서버 재시작

**이유:**
- Uvicorn은 `--reload` 모드에서도 데이터베이스 연결은 재시작하지 않음
- 파일이 변경되어도 기존 연결을 유지
- 서버를 완전히 재시작해야 새 데이터베이스 파일 인식

**명령어:**
```bash
# 기존 서버 종료
kill [backend_pid]

# 데이터베이스 재생성 (깨끗하게)
cd backend
rm -f app.db app.db-*

python -c "
from app.db.base import Base
from app.database import engine
from app.models import Search, Video, Project, ProjectVideo, FinalVideo

Base.metadata.create_all(bind=engine)
"

# 서버 재시작
uvicorn app.main:app --reload
```

---

### 7단계: 최종 테스트

**API 테스트:**
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "skills", "limit": 30}'
```

**성공적인 응답:**
```json
{
  "id": "957c2c58-83ed-4a5b-94b1-718e25254880",
  "keyword": "skills",
  "status": "pending",
  "total_found": 0,
  "task_id": "15d819d6-6658-4f4c-9356-d04515e9a390",
  "created_at": "2025-10-19T03:53:02.530967"
}
```

**HTTP 상태 코드:** 200 OK ✅

---

## 근본 원인 분석

### 1. Base 클래스 중복 정의 (핵심 문제)

**문제:**
```
app/database.py → Base A 생성
app/db/base.py  → Base B 생성

모델들은 Base B 사용
engine은 Base A와 연결
→ 테이블이 생성되지 않음
```

**해결:**
```python
# app/database.py
from app.db.base import Base  # Base B 재사용

# 이제 모델과 engine이 같은 Base 사용
```

### 2. 자동 초기화 부재

**문제:**
- Backend 시작 시 테이블 자동 생성 로직 없음
- 수동으로 초기화 스크립트 실행 필요

**해결:**
- `start-dev.sh`에 자동 초기화 로직 추가
- 데이터베이스 파일이 없거나 비어있으면 자동 생성

### 3. 서버 재시작 필요성

**문제:**
- Uvicorn `--reload`는 코드 변경만 감지
- 데이터베이스 파일 변경은 감지하지 않음
- 기존 연결을 계속 사용

**해결:**
- 데이터베이스 재생성 후 서버 재시작 필수

---

## 해결 방법 요약

### 즉시 해결 (긴급 상황)

```bash
# 1. 모든 서비스 중지
./stop-dev.sh

# 2. 데이터베이스 초기화
cd backend
rm -f app.db
python -c "
from app.db.base import Base
from app.database import engine
from app.models import Search, Video, Project, ProjectVideo, FinalVideo
Base.metadata.create_all(bind=engine)
"

# 3. 서비스 재시작
cd ..
./start-dev.sh
```

### 자동 해결 (권장)

**start-dev.sh가 이미 업데이트되어 있음:**
```bash
# 이제 이 명령어 하나로 자동 해결
./start-dev.sh
```

**자동으로 수행되는 작업:**
1. 데이터베이스 파일 존재 여부 확인
2. 없거나 비어있으면 자동 생성
3. Backend 서버 시작

---

## 예방 조치

### 1. start-dev.sh 스크립트 개선

**추가된 로직:**
```bash
# 데이터베이스 초기화 (테이블이 없는 경우에만)
if [ ! -f "app.db" ] || [ ! -s "app.db" ]; then
    echo "데이터베이스 초기화 중..."
    python -c "
from app.db.base import Base
from app.database import engine
from app.models import Search, Video, Project, ProjectVideo, FinalVideo
Base.metadata.create_all(bind=engine)
"
    echo "✓ 데이터베이스 초기화 완료"
fi
```

### 2. init-db.sh 스크립트 생성

**전용 초기화 스크립트:**
```bash
# 일반 초기화 (데이터 유지)
./init-db.sh

# 완전 초기화 (데이터 삭제)
./init-db.sh --reset
```

### 3. app/main.py에 시작 이벤트 추가 (선택적)

**자동 테이블 생성:**
```python
@app.on_event("startup")
async def startup_event():
    """서버 시작 시 데이터베이스 테이블 생성"""
    from app.db.base import Base
    from app.database import engine
    import app.models  # 모든 모델 import

    Base.metadata.create_all(bind=engine)
    print("✓ Database tables initialized")
```

---

## 학습 포인트

### 1. SQLAlchemy의 Base 클래스

**핵심 개념:**
- `declarative_base()`는 **매번 새로운 객체**를 생성
- 모델들은 **하나의 Base 인스턴스**를 공유해야 함
- 여러 파일에서 `Base = declarative_base()` 실행 → 각각 다른 Base

**올바른 패턴:**
```python
# base.py (한 곳에서만 생성)
Base = declarative_base()

# 다른 파일들 (재사용)
from app.db.base import Base
```

### 2. Uvicorn --reload의 동작

**리로드 되는 것:**
- ✅ Python 코드 파일 (`.py`)
- ✅ 설정 파일 (`.env` - 일부)

**리로드 안 되는 것:**
- ❌ 데이터베이스 연결
- ❌ 이미 열린 파일 핸들
- ❌ 외부 리소스 (Redis, 등)

**대응:**
- 데이터베이스 변경 후 → 서버 재시작
- 환경 변수 변경 후 → 서버 재시작

### 3. SQLite의 특징

**파일 기반:**
- 서버 프로세스 불필요
- 파일 존재 ≠ 테이블 존재
- 빈 파일도 유효한 SQLite 파일

**권한 요구사항:**
- 데이터베이스 파일 쓰기 권한
- **디렉토리 쓰기 권한** (임시 파일용)
- 두 가지 모두 필요!

**Lock 파일:**
```
app.db          # 실제 데이터베이스
app.db-journal  # 트랜잭션 로그
app.db-wal      # Write-Ahead Log (WAL 모드)
app.db-shm      # 공유 메모리 파일
```

---

## 디버깅 체크리스트

### Backend API 에러 발생 시

1. **로그 확인**
```bash
# 실시간 로그
tail -f logs/backend.log

# 에러만 필터
tail -f logs/backend.log | grep ERROR
```

2. **데이터베이스 상태 확인**
```bash
# 파일 존재 여부
ls -lh backend/app.db

# 테이블 목록
sqlite3 backend/app.db ".tables"

# 레코드 수
sqlite3 backend/app.db "SELECT COUNT(*) FROM searches;"
```

3. **API 직접 테스트**
```bash
# Health check
curl http://localhost:8000/health

# 검색 API
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "test", "limit": 10}'
```

4. **서비스 상태 확인**
```bash
./status-dev.sh
```

### Frontend Network Error 발생 시

1. **Backend 연결 확인**
```bash
# Backend가 실행 중인지
lsof -ti:8000

# 응답하는지
curl http://localhost:8000/health
```

2. **CORS 설정 확인**
```bash
# .env 파일 확인
cat backend/.env | grep ALLOWED_ORIGINS

# 올바른 형식: ["http://localhost:3000"]
```

3. **브라우저 콘솔 확인**
```
F12 → Console 탭
→ 에러 메시지 확인
→ Network 탭에서 실제 요청/응답 확인
```

---

## 관련 명령어 모음

### 데이터베이스 관리

```bash
# 초기화
./init-db.sh

# 완전 초기화
./init-db.sh --reset

# 테이블 확인
sqlite3 backend/app.db ".tables"

# 스키마 확인
sqlite3 backend/app.db ".schema searches"

# 데이터 조회
sqlite3 backend/app.db "SELECT * FROM searches;"

# 백업
cp backend/app.db backend/app.db.backup.$(date +%Y%m%d)
```

### 서비스 관리

```bash
# 전체 시작
./start-dev.sh

# 전체 중지
./stop-dev.sh

# 상태 확인
./status-dev.sh

# Backend만 재시작
kill [backend_pid]
cd backend && uvicorn app.main:app --reload
```

### 로그 확인

```bash
# 실시간 로그
tail -f logs/backend.log
tail -f logs/celery.log
tail -f logs/frontend.log

# 에러만 보기
tail -f logs/backend.log | grep ERROR

# 최근 100줄
tail -100 logs/backend.log
```

---

## 최종 결과

✅ **문제 해결 완료**

- Base 클래스 중복 제거
- 데이터베이스 자동 초기화 추가
- Backend 서버 정상 작동
- API 정상 응답 (200 OK)
- Frontend에서 검색 가능

**테스트 명령어:**
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "skills", "limit": 30}'
```

**응답:**
```json
{
  "id": "957c2c58-83ed-4a5b-94b1-718e25254880",
  "keyword": "skills",
  "status": "pending",
  "total_found": 0,
  "task_id": "15d819d6-6658-4f4c-9356-d04515e9a390",
  "created_at": "2025-10-19T03:53:02.530967"
}
```

**HTTP 상태:** 200 OK ✅

---

## 다음 단계

1. **Celery Worker 확인**
   - 검색 작업이 실제로 실행되는지 확인
   - Celery 로그에서 진행 상황 모니터링

2. **TikTok API 연동 테스트**
   - 실제 TikTok 영상 검색 작동 여부
   - API 키/인증 필요 여부 확인

3. **WebSocket 연결 테스트**
   - 실시간 진행 상황 업데이트
   - Frontend와 Backend 통신 확인

4. **End-to-End 테스트**
   - 검색 → 결과 확인 → 프로젝트 생성 → 영상 생성
   - 전체 플로우 테스트
