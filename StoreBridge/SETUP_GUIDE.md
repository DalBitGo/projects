# StoreBridge 설치 및 실행 가이드

이 문서는 StoreBridge 프로젝트를 로컬 환경에서 설정하고 실행하는 전체 과정을 설명합니다.

## 📋 목차

1. [사전 요구사항](#사전-요구사항)
2. [발생한 문제와 해결 방법](#발생한-문제와-해결-방법)
3. [설치 및 실행 단계](#설치-및-실행-단계)
4. [시스템 구성 요소](#시스템-구성-요소)
5. [API 테스트](#api-테스트)
6. [트러블슈팅](#트러블슈팅)

---

## 🔧 사전 요구사항

- **Python**: 3.10+ (프로젝트는 Python 3.10.12로 테스트됨)
- **Docker**: PostgreSQL, Redis 컨테이너 실행용
- **Git**: 소스 코드 관리

---

## ⚠️ 발생한 문제와 해결 방법

### 1. **PostgreSQL asyncpg 인증 문제**

**문제**: asyncpg 드라이버가 PostgreSQL에 연결 시 `password authentication failed` 에러 반복 발생

**원인**:
- PostgreSQL Docker 컨테이너의 pg_hba.conf 설정 문제
- asyncpg가 PostgreSQL의 인증 방식(scram-sha-256)과 호환 이슈
- 비밀번호 설정 후 재로딩이 제대로 반영되지 않음

**시도한 해결 방법들**:
1. ❌ `ALTER USER` 명령으로 비밀번호 재설정 → 실패
2. ❌ pg_hba.conf에 `host all all 0.0.0.0/0 scram-sha-256` 추가 → 실패
3. ❌ PostgreSQL 컨테이너 재시작 → 실패
4. ❌ 컨테이너 재생성 (trust 모드 포함) → 여전히 실패
5. ❌ psycopg3 드라이버로 변경 → 동일한 인증 문제 발생

**최종 해결 방법**:
- **Alembic 마이그레이션 우회**: 직접 SQL 스크립트(`schema.sql`)로 테이블 생성
- **DATABASE_URL 단순화**: 패스워드 제거, trust 모드 사용
  ```bash
  DATABASE_URL=postgresql+psycopg://storebridge@localhost:5432/storebridge
  ```
- **Docker 컨테이너 설정**:
  ```bash
  docker run -d --name postgres_db \
    -e POSTGRES_HOST_AUTH_METHOD=trust \
    -e POSTGRES_USER=storebridge \
    -e POSTGRES_DB=storebridge \
    -p 5432:5432 \
    postgres:15
  ```

**교훈**:
- 로컬 개발 환경에서는 trust 모드가 더 안정적
- asyncpg는 PostgreSQL 인증 설정에 민감함
- 마이그레이션 도구가 실패할 경우 SQL 직접 실행도 옵션

---

### 2. **SQLAlchemy 모델 `metadata` 예약어 충돌**

**문제**: `ProductRegistration` 모델에서 `metadata` 필드 사용 시 에러 발생
```python
sqlalchemy.exc.InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.
```

**원인**:
- SQLAlchemy의 `Base` 클래스가 이미 `metadata` 속성을 사용 중

**해결 방법**:
```python
# Before (잘못됨)
metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

# After (수정)
registration_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
```

**파일**: `app/models/product.py:115`

---

### 3. **Import 순환 참조 및 누락**

**문제**: FastAPI 서버 시작 시 `ImportError: cannot import name 'JobStatus'` 발생

**원인**:
- `app/models/__init__.py`에서 `JobStatus`, `JobType` export 누락

**해결 방법**:
```python
# app/models/__init__.py
from app.models.product import (
    CategoryMapping,
    Job,
    JobStatus,  # 추가
    JobType,    # 추가
    Product,
    ProductRegistration,
    State,
)

__all__ = [
    "Base",
    "Product",
    "ProductRegistration",
    "Job",
    "JobStatus",  # 추가
    "JobType",    # 추가
    "CategoryMapping",
    "State",
]
```

---

## 📦 설치 및 실행 단계

### 1. 프로젝트 클론 및 의존성 설치

```bash
cd /path/to/StoreBridge

# Python 의존성 설치
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 추가 드라이버 설치 (psycopg)
pip install psycopg[binary]
```

### 2. 환경 설정

```bash
# .env 파일 생성 (이미 생성됨)
cp .env.example .env

# .env 내용 확인 및 수정
cat .env
```

**주요 설정 (.env)**:
```bash
ENVIRONMENT=development

# PostgreSQL (trust 모드, 패스워드 없음)
DATABASE_URL=postgresql+psycopg://storebridge@localhost:5432/storebridge

# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys (테스트용 더미 값)
DOMEGGOOK_API_KEY=test_key
NAVER_CLIENT_ID=test_client
NAVER_CLIENT_SECRET=test_secret
```

### 3. 인프라 실행 (PostgreSQL, Redis)

#### 기존 컨테이너 정리 (필요시)
```bash
docker ps -a | grep postgres
docker stop postgres_db && docker rm postgres_db
```

#### PostgreSQL 컨테이너 실행
```bash
docker run -d --name postgres_db \
  -e POSTGRES_HOST_AUTH_METHOD=trust \
  -e POSTGRES_USER=storebridge \
  -e POSTGRES_DB=storebridge \
  -p 5432:5432 \
  postgres:15

# 컨테이너 준비 대기
sleep 5
```

#### Redis 컨테이너 실행 (docker-compose 사용)
```bash
docker-compose up -d redis
```

**확인**:
```bash
docker ps | grep postgres_db    # PostgreSQL 실행 확인
docker ps | grep redis          # Redis 실행 확인
```

### 4. 데이터베이스 테이블 생성

```bash
# SQL 스크립트로 테이블 생성
docker exec -i postgres_db psql -U storebridge -d storebridge < schema.sql

# 테이블 생성 확인
docker exec postgres_db psql -U storebridge -d storebridge -c "\dt"
```

**출력 예시**:
```
                  List of relations
 Schema |         Name          | Type  |    Owner
--------+-----------------------+-------+-------------
 public | category_mappings     | table | storebridge
 public | jobs                  | table | storebridge
 public | product_registrations | table | storebridge
 public | products              | table | storebridge
(4 rows)
```

### 5. FastAPI 서버 실행

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**확인**:
```bash
curl http://localhost:8000/
```

**출력**:
```json
{
  "service": "StoreBridge API",
  "version": "0.1.0",
  "status": "healthy",
  "environment": "development"
}
```

### 6. Celery Worker 실행 (별도 터미널)

```bash
# 새 터미널 열기
cd /path/to/StoreBridge

celery -A app.workers.celery_app worker --loglevel=info
```

---

## 🏗️ 시스템 구성 요소

| 구성 요소 | 역할 | 포트 | 상태 확인 |
|-----------|------|------|-----------|
| **FastAPI** | REST API 서버 | 8000 | `curl http://localhost:8000/` |
| **PostgreSQL** | 메인 데이터베이스 | 5432 | `docker ps \| grep postgres_db` |
| **Redis** | Rate Limiter, Celery Broker | 6379 | `docker ps \| grep redis` |
| **Celery Worker** | 백그라운드 작업 처리 | - | Celery 로그 확인 |

---

## 🧪 API 테스트

### 1. Health Check
```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

### 2. Job 생성 (Import)
```bash
curl -X POST http://localhost:8000/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "type": "IMPORT",
    "config": {
      "source": "domeggook",
      "filter": {
        "category": "패션의류",
        "price_min": 10000
      },
      "limit": 10,
      "auto_register": true
    }
  }'
```

**응답 예시**:
```json
{
  "success": true,
  "data": {
    "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "type": "IMPORT",
    "status": "PENDING",
    "total_count": 0,
    "estimated_duration_minutes": 15
  }
}
```

### 3. Job 상태 조회
```bash
# job_id는 위에서 받은 값 사용
curl http://localhost:8000/v1/jobs/3fa85f64-5717-4562-b3fc-2c963f66afa6
```

### 4. Job 리스트 조회
```bash
curl "http://localhost:8000/v1/jobs?page=1&page_size=20"
```

---

## 🔍 트러블슈팅

### PostgreSQL 연결 실패
```bash
# 에러: connection refused
docker ps | grep postgres_db  # 컨테이너 실행 확인
docker logs postgres_db       # 로그 확인

# 재시작
docker restart postgres_db
```

### Redis 연결 실패
```bash
docker ps | grep redis
docker logs storebridge-redis

# 재시작
docker-compose restart redis
```

### Celery Worker가 Job을 처리하지 않음
```bash
# Celery Worker 재시작
# Ctrl+C로 종료 후
celery -A app.workers.celery_app worker --loglevel=debug

# Redis 큐 확인
docker exec storebridge-redis redis-cli KEYS "*"
```

### 테이블이 없다는 에러
```bash
# schema.sql 재실행
docker exec -i postgres_db psql -U storebridge -d storebridge < schema.sql
```

### Import Error (모듈 누락)
```bash
# Python 경로 확인
export PYTHONPATH=/path/to/StoreBridge:$PYTHONPATH

# 또는 프로젝트 루트에서 실행
cd /path/to/StoreBridge
python -m app.main
```

---

## 📊 구현된 기능

✅ **완료**:
- Celery Worker (Import, Register, Update Job Status)
- Job API (Create, Get, List, Cancel)
- Rate Limiter (Lua script, 2 TPS for Naver)
- Option Mapper (1D/2D/3D parsing)
- Validators (Forbidden words, Product)
- PostgreSQL Tables (4 tables, 11 indexes)

🚧 **미완성** (향후 구현 필요):
- 도매꾹/네이버 API 실제 연동 (현재 목 데이터 사용)
- 이미지 처리 파이프라인
- 카테고리 매핑 로직
- Integration/E2E 테스트

---

## 📝 주요 파일

```
StoreBridge/
├── app/
│   ├── workers/
│   │   ├── celery_app.py      # Celery 설정
│   │   └── tasks.py            # 백그라운드 작업 (Import, Register)
│   ├── api/
│   │   └── jobs.py             # Job API 엔드포인트
│   ├── models/
│   │   └── product.py          # DB 모델 (Product, Job, etc.)
│   ├── connectors/
│   │   ├── domeggook_client.py # 도매꾹 API 클라이언트
│   │   └── naver_client.py     # 네이버 API 클라이언트
│   ├── services/
│   │   ├── rate_limiter.py     # Rate Limiter (2 TPS)
│   │   └── option_mapper.py    # 옵션 파싱 및 변환
│   └── main.py                 # FastAPI 앱
├── schema.sql                  # 테이블 생성 SQL
├── .env                        # 환경 변수
├── docker-compose.yml          # Redis 설정
└── SETUP_GUIDE.md              # 이 문서
```

---

## 🎯 다음 단계

1. **도매꾹 API 키 발급** - [https://openapi.domeggook.com](https://openapi.domeggook.com)에서 발급
2. **네이버 Commerce API 인증** - 네이버 스마트스토어 개발자 센터에서 발급
3. **.env 파일 업데이트** - 실제 API 키로 교체
4. **실제 데이터로 테스트** - 도매꾹에서 상품 import 후 네이버 등록

---

**작성일**: 2025-10-17
**작성자**: Claude Code (with StoreBridge Project)
**버전**: 0.1.0 (Alpha)
