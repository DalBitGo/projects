# Docker PostgreSQL 개발 환경 설정 가이드

## 🎯 문제: Docker PostgreSQL + Python asyncpg/psycopg 인증 실패

### 증상
```bash
asyncpg.exceptions.InvalidPasswordError: password authentication failed for user "storebridge"
```

---

## 🔍 근본 원인 분석

### 1. Docker 네트워크와 PostgreSQL 인증의 차이

**PostgreSQL의 인증 방식은 연결 출처에 따라 다름**:

| 연결 방식 | 예시 | PostgreSQL이 보는 관점 | pg_hba.conf 규칙 |
|-----------|------|------------------------|------------------|
| Unix Socket | `psql -U user` (컨테이너 내부) | 로컬 | `local all all trust` |
| 127.0.0.1 | `psql -h 127.0.0.1` (컨테이너 내부) | 로컬 | `host all all 127.0.0.1/32 trust` |
| Docker Bridge | `psql -h localhost` (호스트 → 컨테이너) | **외부** | `host all all 0.0.0.0/0 [METHOD]` |

**핵심**:
- 호스트에서 `localhost:5432`로 연결 시, Docker는 **bridge 네트워크를 거침**
- PostgreSQL 입장에서는 **외부 IP에서 오는 연결**로 인식
- 기본 trust 규칙 (127.0.0.1/32)이 **적용되지 않음**

### 2. POSTGRES_HOST_AUTH_METHOD=trust의 한계

```bash
docker run -e POSTGRES_HOST_AUTH_METHOD=trust postgres:15
```

이 환경 변수는 **pg_hba.conf 초기 설정**만 변경:
```conf
# 기본 생성되는 규칙
local   all             all                                     trust
host    all             all             127.0.0.1/32            trust
host    all             all             ::1/128                 trust
```

**문제**: `0.0.0.0/0` (모든 외부 IP) 규칙은 **자동 생성 안 됨**

### 3. asyncpg/psycopg의 인증 동작

1. Python 드라이버가 PostgreSQL에 연결 시도
2. PostgreSQL이 사용자 정보 확인:
   ```sql
   SELECT rolpassword FROM pg_authid WHERE rolname='storebridge';
   -- 결과: SCRAM-SHA-256$4096:... (암호화된 해시)
   ```
3. **패스워드가 설정되어 있으면**, PostgreSQL은 클라이언트에게 인증 요구
4. Python 드라이버가 `password=None` 또는 패스워드 미제공 → **인증 실패**

**asyncpg는 trust 모드여도 사용자에게 패스워드가 있으면 인증 시도**

---

## ✅ 영구적인 해결 방법 (환경별)

### 방법 1: 로컬 개발 환경 (추천) ⭐

완전히 trust 모드로 설정 + 외부 연결 허용

```bash
docker run -d --name postgres_dev \
  -e POSTGRES_HOST_AUTH_METHOD=trust \
  -e POSTGRES_USER=storebridge \
  -e POSTGRES_DB=storebridge \
  -p 5432:5432 \
  postgres:15

# pg_hba.conf에 외부 연결 trust 규칙 추가
docker exec postgres_dev sh -c "echo 'host all all 0.0.0.0/0 trust' >> /var/lib/postgresql/data/pg_hba.conf"

# 설정 리로드
docker exec postgres_dev psql -U storebridge -d storebridge -c 'SELECT pg_reload_conf();'

# 사용자 패스워드 제거 (선택)
docker exec postgres_dev psql -U storebridge -d storebridge -c 'ALTER USER storebridge WITH PASSWORD NULL;'
```

**장점**:
- ✅ 로컬 개발에서 인증 걱정 없음
- ✅ 모든 Python 드라이버 (asyncpg, psycopg, SQLAlchemy) 동작
- ✅ docker-compose, Alembic, 모든 툴 호환

**단점**:
- ⚠️ 보안 없음 (로컬 개발 전용)

---

### 방법 2: docker-compose로 자동화 (추천) ⭐⭐

`docker-compose.yml`:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: storebridge-postgres
    environment:
      POSTGRES_HOST_AUTH_METHOD: trust  # 초기 trust 설정
      POSTGRES_USER: storebridge
      POSTGRES_DB: storebridge
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/pg_hba.conf:/var/lib/postgresql/data/pg_hba.conf  # 커스텀 설정
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U storebridge"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

`docker/postgres/pg_hba.conf`:
```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     trust
host    all             all             127.0.0.1/32            trust
host    all             all             ::1/128                 trust
host    all             all             0.0.0.0/0               trust  # 모든 외부 연결 trust
```

실행:
```bash
docker-compose up -d postgres
```

**장점**:
- ✅ 한 번 설정하면 영구적
- ✅ 팀원들과 동일한 환경 공유
- ✅ 버전 관리 가능

---

### 방법 3: 패스워드 사용 (프로덕션 스타일)

**PostgreSQL 설정**:
```bash
docker run -d --name postgres_prod \
  -e POSTGRES_USER=storebridge \
  -e POSTGRES_PASSWORD=storebridge123 \
  -e POSTGRES_DB=storebridge \
  -p 5432:5432 \
  postgres:15
```

**Python 코드**:
```python
# .env
DATABASE_URL=postgresql+asyncpg://storebridge:storebridge123@localhost:5432/storebridge

# app/database.py
engine = create_async_engine(
    settings.database_url,  # 패스워드 포함된 URL
    echo=True
)
```

**장점**:
- ✅ 프로덕션과 동일한 보안 방식
- ✅ pg_hba.conf 수정 불필요

**단점**:
- ⚠️ 패스워드 관리 필요
- ⚠️ .env 파일 버전 관리 주의

---

### 방법 4: Docker 네트워크 내부에서만 접근

Python 애플리케이션도 Docker 컨테이너로 실행:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_HOST_AUTH_METHOD: trust
      POSTGRES_USER: storebridge
      POSTGRES_DB: storebridge
    networks:
      - backend
    # 포트를 호스트에 노출하지 않음

  app:
    build: .
    environment:
      DATABASE_URL: postgresql+asyncpg://storebridge@postgres:5432/storebridge
      # ↑ 'postgres' 호스트명 (Docker 내부 DNS)
    depends_on:
      - postgres
    networks:
      - backend

networks:
  backend:
```

**장점**:
- ✅ Docker 네트워크 내부 연결 → 127.0.0.1처럼 동작
- ✅ trust 모드 그대로 동작
- ✅ 호스트에서 PostgreSQL 접근 불가 (보안)

**단점**:
- ⚠️ 로컬에서 직접 psql 접속 불가
- ⚠️ 개발 중 디버깅 불편

---

## 🛠️ 트러블슈팅: 현재 상태 진단

### 1. PostgreSQL 인증 설정 확인

```bash
# pg_hba.conf 확인
docker exec postgres_db cat /var/lib/postgresql/data/pg_hba.conf | grep -v "^#" | grep -v "^$"

# 예상 출력:
# local   all             all                                     trust
# host    all             all             127.0.0.1/32            trust
# host    all             all             ::1/128                 trust
# host    all             all             0.0.0.0/0               trust  ← 이 줄이 있어야 함
```

### 2. 사용자 패스워드 상태 확인

```bash
docker exec postgres_db psql -U storebridge -d storebridge -c \
  "SELECT rolname, CASE WHEN rolpassword IS NULL THEN 'NO PASSWORD' ELSE 'HAS PASSWORD' END AS password_status FROM pg_authid WHERE rolname='storebridge';"

# 예상 출력:
#   rolname   | password_status
# ------------+-----------------
#  storebridge | HAS PASSWORD  또는 NO PASSWORD
```

- `HAS PASSWORD`: 인증 필요 → trust 규칙 또는 패스워드 제공 필요
- `NO PASSWORD`: 패스워드 없음 → trust 규칙만으로 충분

### 3. Python 연결 테스트

```bash
python3 -c "
import asyncio
import asyncpg

async def test():
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='storebridge',
        database='storebridge'
    )
    result = await conn.fetchval('SELECT version()')
    print(f'✅ 연결 성공!')
    print(f'PostgreSQL: {result[:50]}...')
    await conn.close()

asyncio.run(test())
"
```

**성공 시**: `✅ 연결 성공!`
**실패 시**: `asyncpg.exceptions.InvalidPasswordError` → 위 방법 1~4 적용

---

## 📋 체크리스트: 새 프로젝트 시작 시

- [ ] `docker-compose.yml`에 PostgreSQL 설정 추가
- [ ] `docker/postgres/pg_hba.conf` 파일 생성 (trust 규칙 포함)
- [ ] `.env.example`에 DATABASE_URL 예시 추가
- [ ] `README.md`에 "로컬 개발 시 trust 모드 사용" 명시
- [ ] 팀원에게 보안 주의사항 공유

---

## ⚠️ 보안 주의사항

### 로컬 개발 환경

- ✅ `trust` 모드 사용 OK (로컬 네트워크만 접근)
- ✅ 간단한 패스워드 (예: `dev`, `123`) OK
- ⚠️ localhost가 아닌 0.0.0.0으로 바인딩 시 주의

### 프로덕션 환경

- ❌ **절대** `trust` 모드 사용 금지
- ✅ 강력한 패스워드 필수
- ✅ SSL/TLS 연결 필수 (`sslmode=require`)
- ✅ IP 화이트리스트 설정
- ✅ 패스워드는 환경 변수 또는 Secret Manager 사용

```yaml
# 프로덕션 docker-compose.yml (나쁜 예)
environment:
  POSTGRES_HOST_AUTH_METHOD: trust  # ❌ 절대 금지!

# 프로덕션 docker-compose.yml (좋은 예)
environment:
  POSTGRES_PASSWORD_FILE: /run/secrets/db_password  # ✅ Docker secrets
```

---

## 🔗 참고 자료

- [PostgreSQL pg_hba.conf 문서](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html)
- [asyncpg 연결 파라미터](https://magicstack.github.io/asyncpg/current/api/index.html#connection)
- [Docker PostgreSQL 이미지](https://hub.docker.com/_/postgres)

---

**작성일**: 2025-10-17
**버전**: 1.0
**프로젝트**: StoreBridge
