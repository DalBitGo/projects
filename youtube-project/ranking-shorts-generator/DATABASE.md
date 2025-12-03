# 데이터베이스 가이드

## 데이터베이스 기본 개념

### SQLite란?

**SQLite**는 파일 기반의 경량 데이터베이스입니다.

**일반 데이터베이스 (MySQL, PostgreSQL):**
```
사용자 → Backend → 네트워크 → 데이터베이스 서버 (항상 실행 중)
```
- 별도의 서버 프로세스 필요
- 네트워크를 통해 통신
- 여러 사용자 동시 접속 가능

**SQLite:**
```
사용자 → Backend → 로컬 파일 (app.db)
```
- **서버 프로세스 불필요** ⭐
- 단순히 파일을 읽고 쓰기만 함
- 가볍고 설정이 간단

### SQLite는 별도로 실행하지 않습니다!

**중요한 차이점:**

| 구성 요소 | 별도 실행 필요? | 이유 |
|----------|---------------|-----|
| **Redis** | ✅ 필요 | 서버 프로그램 (`docker run` 또는 `redis-server`) |
| **Backend** | ✅ 필요 | API 서버 (`uvicorn`) |
| **Celery** | ✅ 필요 | Worker 프로세스 (`celery worker`) |
| **Frontend** | ✅ 필요 | 개발 서버 (`npm run dev`) |
| **SQLite** | ❌ 불필요 | 단순한 파일 (Backend가 자동으로 읽기/쓰기) |

### SQLite 동작 방식

```python
# Backend 코드에서
from app.database import engine  # 파일 app.db 연결
db.add(search)                   # 메모리에서 작업
db.commit()                      # 파일에 저장
```

**실행 흐름:**
1. Backend 시작 시 `app.db` 파일 열기
2. 데이터 읽기/쓰기 요청이 오면 파일 접근
3. Backend 종료 시 파일 닫기

**Redis와 비교:**

| | SQLite | Redis |
|---|--------|-------|
| **형태** | 파일 (`app.db`) | 서버 프로세스 |
| **실행** | Backend가 자동으로 | 수동으로 시작 필요 |
| **저장** | 디스크 (영구) | 메모리 (휘발성) |
| **용도** | 영구 데이터 저장 | 임시 데이터, 캐시, 메시지 큐 |

---

## 데이터베이스 구조

### 테이블 구성

프로젝트에는 5개의 테이블이 있습니다:

#### 1. searches (검색 기록)
```sql
CREATE TABLE searches (
    id TEXT PRIMARY KEY,              -- UUID
    keyword TEXT NOT NULL,            -- 검색 키워드 (예: "춤")
    status TEXT NOT NULL,             -- pending, processing, completed, failed
    total_found INTEGER DEFAULT 0,    -- 찾은 영상 수
    task_id TEXT,                     -- Celery 작업 ID
    created_at DATETIME,              -- 생성 시간
    completed_at DATETIME             -- 완료 시간
);
```

**예시 데이터:**
```
id: "abc-123"
keyword: "춤"
status: "completed"
total_found: 30
created_at: 2025-10-19 12:00:00
```

#### 2. videos (영상 정보)
```sql
CREATE TABLE videos (
    id TEXT PRIMARY KEY,              -- UUID
    tiktok_id TEXT UNIQUE,            -- TikTok 영상 ID
    search_id TEXT,                   -- 어떤 검색에서 찾았는지
    thumbnail_url TEXT,               -- 썸네일 URL
    title TEXT,                       -- 제목
    description TEXT,                 -- 설명
    views INTEGER,                    -- 조회수
    likes INTEGER,                    -- 좋아요
    comments INTEGER,                 -- 댓글 수
    shares INTEGER,                   -- 공유 수
    duration INTEGER,                 -- 길이 (초)
    download_url TEXT,                -- 다운로드 URL
    file_path TEXT,                   -- 로컬 파일 경로
    author_username TEXT,             -- 작성자
    created_at DATETIME
);
```

#### 3. projects (프로젝트)
```sql
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,               -- 프로젝트 이름
    status TEXT NOT NULL,             -- created, processing, completed, failed
    settings JSON,                    -- 영상 설정 (배경음악, 효과 등)
    task_id TEXT,                     -- Celery 작업 ID
    created_at DATETIME,
    completed_at DATETIME
);
```

#### 4. project_videos (프로젝트-영상 연결)
```sql
CREATE TABLE project_videos (
    project_id TEXT,
    video_id TEXT,
    rank_order INTEGER NOT NULL,      -- 랭킹 순서 (1위, 2위, ...)
    PRIMARY KEY (project_id, video_id)
);
```

#### 5. final_videos (생성된 최종 영상)
```sql
CREATE TABLE final_videos (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    file_path TEXT NOT NULL,          -- 생성된 영상 파일 경로
    duration INTEGER NOT NULL,        -- 영상 길이
    created_at DATETIME
);
```

---

## 데이터베이스 파일 위치

### 파일 경로
```
/home/junhyun/youtube-project/ranking-shorts-generator/backend/app.db
```

### 파일 확인
```bash
cd backend

# 파일 존재 확인
ls -lh app.db

# 파일 크기 확인
du -h app.db

# 테이블 목록 확인
sqlite3 app.db ".tables"

# 특정 테이블 데이터 조회
sqlite3 app.db "SELECT * FROM searches;"
```

---

## 데이터베이스 초기화

### 자동 초기화 (권장)

**start-dev.sh 사용 시 자동으로 처리됩니다:**
```bash
./start-dev.sh
# 데이터베이스가 없으면 자동 생성
```

### 수동 초기화

#### 방법 1: Python 스크립트
```bash
cd backend

python -c "
from app.db.base import Base
from app.database import engine
from app.models import Search, Video, Project, ProjectVideo, FinalVideo

# 모든 테이블 생성
Base.metadata.create_all(bind=engine)
print('Database initialized!')
"
```

#### 방법 2: 전용 스크립트 사용
```bash
# 데이터베이스 초기화 스크립트 실행
./init-db.sh
```

---

## 데이터베이스 작업

### 데이터 조회

#### SQLite CLI 사용
```bash
cd backend

# SQLite 쉘 열기
sqlite3 app.db

# 테이블 목록
.tables

# 테이블 구조 확인
.schema searches

# 데이터 조회
SELECT * FROM searches;
SELECT * FROM videos WHERE views > 100000;

# 예쁘게 출력
.mode column
.headers on
SELECT keyword, status, total_found FROM searches;

# 종료
.quit
```

#### Python으로 조회
```bash
cd backend

python -c "
from app.database import SessionLocal
from app.models.search import Search

db = SessionLocal()
searches = db.query(Search).all()

for s in searches:
    print(f'{s.keyword}: {s.total_found}개 영상')
"
```

### 데이터 백업

#### 방법 1: 파일 복사 (간단)
```bash
cd backend

# 백업
cp app.db app.db.backup.$(date +%Y%m%d)

# 복원
cp app.db.backup.20251019 app.db
```

#### 방법 2: SQL 덤프 (권장)
```bash
cd backend

# 백업 (텍스트 파일로 저장)
sqlite3 app.db .dump > backup.sql

# 복원
sqlite3 app.db < backup.sql
```

### 데이터베이스 초기화 (모든 데이터 삭제)

```bash
cd backend

# ⚠️ 주의: 모든 데이터가 삭제됩니다!
rm app.db

# 새로 생성
python -c "
from app.db.base import Base
from app.database import engine
from app.models import Search, Video, Project, ProjectVideo, FinalVideo
Base.metadata.create_all(bind=engine)
"
```

---

## 데이터베이스 관리 도구

### 1. SQLite CLI (기본)
```bash
# 설치 확인
sqlite3 --version

# 사용법
sqlite3 backend/app.db
```

### 2. DB Browser for SQLite (GUI, 추천)
```bash
# Ubuntu/WSL 설치
sudo apt-get install sqlitebrowser

# 실행
sqlitebrowser backend/app.db
```

**기능:**
- ✅ 테이블 시각화
- ✅ 데이터 편집
- ✅ SQL 쿼리 실행
- ✅ 스키마 확인

### 3. VS Code 확장 프로그램
```
SQLite Viewer 확장 설치
→ app.db 파일 클릭
→ 테이블 및 데이터 확인
```

---

## 데이터베이스 마이그레이션

### Alembic이란?

데이터베이스 스키마를 버전 관리하는 도구입니다.

**예시 시나리오:**
```
v1: searches 테이블에 keyword 컬럼만 있음
↓
v2: error_message 컬럼 추가 필요
↓
Alembic으로 마이그레이션 실행
→ 기존 데이터 유지하면서 컬럼 추가
```

### Alembic 사용법 (선택)

```bash
cd backend

# 초기 설정 (이미 되어 있음)
alembic init alembic

# 마이그레이션 파일 생성
alembic revision --autogenerate -m "Add error_message to searches"

# 마이그레이션 적용
alembic upgrade head

# 이전 버전으로 롤백
alembic downgrade -1
```

**현재 프로젝트에서는:**
- 혼자 사용 → Alembic 불필요
- 스키마 변경 시 → 그냥 테이블 삭제 후 재생성

---

## 자주 묻는 질문 (FAQ)

### Q1: SQLite 서버를 실행해야 하나요?
**A:** 아니요! SQLite는 파일 기반이라 별도 서버가 필요 없습니다.

### Q2: 데이터베이스가 실행 중인지 확인하려면?
**A:** SQLite는 "실행"되는 게 아닙니다. 파일이 있는지만 확인하면 됩니다:
```bash
ls -lh backend/app.db
```

### Q3: Redis는 왜 별도로 실행해야 하나요?
**A:** Redis는 **서버 프로그램**이기 때문입니다. SQLite는 **파일**입니다.

### Q4: 데이터베이스 파일을 삭제해도 되나요?
**A:** 네, 하지만 모든 데이터가 사라집니다. 다음 실행 시 자동으로 재생성됩니다.

### Q5: 여러 사용자가 동시에 접속하면?
**A:** SQLite는 동시 쓰기를 제한합니다. 혼자 쓸 때는 문제없지만, 여러 명이 쓴다면 PostgreSQL로 변경 필요.

### Q6: 데이터베이스가 너무 커지면?
**A:** SQLite는 최대 281TB까지 지원하므로 개인 사용에는 충분합니다. 걱정 말아도 됩니다!

### Q7: 백업은 언제 해야 하나요?
**A:** 중요한 작업 전이나 주 1회 정도 백업 추천:
```bash
./backup.sh
```

### Q8: 운영 환경에서도 SQLite를 쓰나요?
**A:**
- 혼자 사용: SQLite ✅
- 10명 미만: SQLite ✅
- 10명 이상: PostgreSQL 권장
- 동시 접속 많음: PostgreSQL 필수

---

## 문제 해결

### "no such table: searches" 에러

**원인:** 데이터베이스 테이블이 생성되지 않음

**해결:**
```bash
cd backend
python -c "
from app.db.base import Base
from app.database import engine
from app.models import Search, Video, Project, ProjectVideo, FinalVideo
Base.metadata.create_all(bind=engine)
"
```

### "database is locked" 에러

**원인:** 다른 프로세스가 데이터베이스 파일을 사용 중

**해결:**
```bash
# 모든 서비스 중지
./stop-dev.sh

# 다시 시작
./start-dev.sh
```

### 데이터베이스 파일이 손상됨

**해결:**
```bash
cd backend

# 백업 확인
ls -lh *.backup.*

# 백업에서 복원
cp app.db.backup.20251019 app.db

# 또는 새로 생성
rm app.db
./start-dev.sh
```

---

## 데이터베이스 초기화 스크립트

편의를 위해 전용 스크립트를 제공합니다:

### init-db.sh
```bash
./init-db.sh          # 데이터베이스 초기화
./init-db.sh --reset  # 기존 데이터 삭제 후 초기화
```

---

## 요약

### 핵심 요점

1. **SQLite는 별도로 실행하지 않습니다** ⭐
   - 단순한 파일 (`app.db`)
   - Backend가 자동으로 읽고 씁니다

2. **Redis는 별도로 실행해야 합니다**
   - 서버 프로그램
   - `docker run` 또는 `redis-server`로 실행

3. **데이터베이스 위치**
   - `backend/app.db`
   - 백업: `./backup.sh`

4. **자동 초기화**
   - `./start-dev.sh` 실행 시 자동 생성

5. **수동 관리**
   ```bash
   # 조회
   sqlite3 backend/app.db "SELECT * FROM searches;"

   # 백업
   cp backend/app.db backend/app.db.backup

   # 초기화
   rm backend/app.db && ./start-dev.sh
   ```

---

## 관련 문서

- [아키텍처 가이드](ARCHITECTURE.md) - 전체 시스템 구조
- [트러블슈팅](TROUBLESHOOTING.md) - 문제 해결
- [빠른 시작](QUICKSTART.md) - 처음 시작하기
