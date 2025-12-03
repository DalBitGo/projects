# 시스템 아키텍처 및 실행 가이드

## 시스템 구성 요소 설명

### 1. Frontend (React + Vite)
**역할:** 사용자 인터페이스
- 사용자가 TikTok 키워드 입력
- 검색 결과 확인 및 영상 선택
- 랭킹 쇼츠 영상 생성 요청
- 진행 상황 실시간 모니터링

**왜 필요한가?**
- 사용자와 시스템 간의 상호작용 인터페이스
- 복잡한 백엔드 작업을 직관적으로 시각화

**포트:** 3000 (또는 5173)

---

### 2. Backend (FastAPI)
**역할:** API 서버 및 비즈니스 로직
- RESTful API 엔드포인트 제공
- 데이터베이스 CRUD 작업
- Celery 작업 큐에 작업 전달
- WebSocket으로 실시간 진행 상황 전송

**왜 필요한가?**
- 프론트엔드와 백엔드 로직 분리 (관심사의 분리)
- 데이터 검증 및 보안
- 비동기 작업 관리

**포트:** 8000

**주요 기능:**
```
GET  /api/v1/health          - 서버 상태 확인
POST /api/v1/search          - TikTok 검색 시작
GET  /api/v1/search/{id}     - 검색 결과 조회
POST /api/v1/projects        - 프로젝트 생성
POST /api/v1/projects/{id}/generate - 영상 생성 시작
```

---

### 3. Redis
**역할:** 메시지 브로커 및 결과 저장소

**왜 필요한가?**

#### 3-1. Celery의 메시지 브로커
- Backend가 "영상 다운로드 해줘"라는 작업을 Redis에 전달
- Celery Worker가 Redis에서 작업을 가져가서 실행
- **비유:** 우체통 역할 (작업 지시서를 넣어두면 Worker가 가져감)

#### 3-2. 작업 결과 저장
- Celery 작업이 완료되면 결과를 Redis에 저장
- Backend가 Redis에서 결과를 조회하여 프론트엔드에 전달

#### 3-3. 캐싱 (선택적)
- 자주 조회되는 데이터 임시 저장
- 데이터베이스 부하 감소

**포트:** 6379

**실행 방식:**
```bash
# Docker 사용 (현재 방식)
docker run -d -p 6379:6379 --name ranking-redis redis:latest

# 또는 로컬 설치
sudo apt-get install redis-server
redis-server
```

---

### 4. Celery Worker
**역할:** 백그라운드 작업 실행

**왜 필요한가?**

#### 4-1. 시간이 오래 걸리는 작업 처리
- TikTok 스크래핑: 30개 영상 검색 → 30초~2분
- 영상 다운로드: 10개 영상 → 1~5분
- 영상 편집 (FFmpeg): 1개 영상 생성 → 2~10분

만약 Backend에서 직접 처리하면:
```
사용자: "영상 만들어줘" → 클릭
Backend: 10분 동안 응답 없음... (브라우저 타임아웃)
사용자: "뭐야 안되잖아?" → 페이지 새로고침 → 작업 취소됨
```

Celery 사용 시:
```
사용자: "영상 만들어줘" → 클릭
Backend: "작업 접수! task_id: abc123" → 즉시 응답 (0.1초)
Celery Worker: 백그라운드에서 묵묵히 작업 진행...
Frontend: WebSocket으로 진행률 확인 (30%... 60%... 100%)
```

#### 4-2. 병렬 처리
- 10개 영상 동시 다운로드
- 여러 사용자의 요청 동시 처리
- CPU 코어를 효율적으로 활용 (현재 8개 프로세스)

**등록된 작업:**
1. `scrape_tiktok_task` - TikTok 검색
2. `download_video_task` - 단일 영상 다운로드
3. `download_videos_batch_task` - 여러 영상 일괄 다운로드
4. `generate_ranking_video_task` - 랭킹 쇼츠 생성
5. `cleanup_temp_files` - 임시 파일 정리

---

### 5. SQLite Database
**역할:** 데이터 영구 저장
- 검색 기록
- 프로젝트 정보
- 영상 메타데이터

**왜 Redis와 별도로 필요한가?**
- **Redis:** 임시 데이터, 빠른 속도 (메모리 기반)
- **SQLite:** 영구 데이터, 안정성 (디스크 기반)

**파일 위치:** `backend/app.db`

---

## 시스템 흐름도

```
사용자 입력 (키워드: "춤")
    ↓
Frontend (React)
    ↓ HTTP POST /api/v1/search
Backend (FastAPI)
    ↓ Celery Task 생성
Redis (메시지 브로커)
    ↓ 작업 전달
Celery Worker
    ↓ TikTok 스크래핑
    ↓ 결과 저장
SQLite Database
    ↓ 결과 조회
Backend → Frontend
    ↓
사용자에게 결과 표시
```

---

## 로컬 개발 환경 vs 운영 환경

### 현재 (로컬 개발 환경)

| 구성 요소 | 실행 방식 | 위치 |
|----------|----------|------|
| Frontend | `npm run dev` | localhost:3000 |
| Backend | `uvicorn` | localhost:8000 |
| Redis | Docker 컨테이너 | localhost:6379 |
| Celery Worker | 터미널 실행 | 같은 머신 |
| Database | SQLite 파일 | 로컬 파일 시스템 |

**장점:**
- ✅ 설정 간단
- ✅ 비용 없음
- ✅ 빠른 개발 및 테스트

**단점:**
- ❌ 컴퓨터 꺼지면 서비스 중단
- ❌ 외부에서 접속 불가
- ❌ 성능 제한
- ❌ 수동 관리 필요

---

### 운영 환경 (프로덕션) 제안

#### 옵션 1: 올인원 서버 (초기 단계 추천)

```
단일 서버 (AWS EC2, DigitalOcean, Vultr 등)
├── Nginx (리버스 프록시)
│   ├── Frontend (정적 파일)
│   └── Backend (API 프록시)
├── Backend (Gunicorn + Uvicorn)
├── Redis (로컬)
├── Celery Worker (Systemd 서비스)
└── PostgreSQL (SQLite 대체)
```

**예상 비용:** $20~40/월
- VPS 서버: $15~30/월 (4GB RAM, 2 CPU)
- 도메인: $10~15/년

**장점:**
- ✅ 비용 효율적
- ✅ 관리 단순
- ✅ 중소 규모 트래픽 처리 가능

**단점:**
- ❌ 확장성 제한
- ❌ 단일 장애점 (서버 다운 → 전체 중단)

---

#### 옵션 2: 마이크로서비스 (확장 고려)

```
도메인: ranking-shorts.com
├── Frontend (Vercel/Netlify) - 무료 또는 $0~20/월
│   └── CDN 자동 제공
│
├── Backend (AWS ECS, Google Cloud Run) - $30~100/월
│   ├── Auto Scaling (부하에 따라 자동 확장)
│   └── Load Balancer
│
├── Redis (AWS ElastiCache, Redis Cloud) - $15~50/월
│   └── 고가용성 클러스터
│
├── Celery Worker (별도 서버 또는 컨테이너) - $20~60/월
│   ├── 여러 인스턴스로 분산
│   └── 작업량에 따라 동적 스케일링
│
└── Database (AWS RDS PostgreSQL) - $15~50/월
    ├── 자동 백업
    └── 읽기 전용 복제본
```

**예상 비용:** $80~280/월

**장점:**
- ✅ 높은 확장성
- ✅ 높은 가용성 (99.9% 업타임)
- ✅ 자동 복구 및 스케일링
- ✅ 각 구성 요소 독립적 관리

**단점:**
- ❌ 초기 설정 복잡
- ❌ 비용 높음
- ❌ 운영 전문 지식 필요

---

#### 옵션 3: 하이브리드 (추천)

**초기:** 옵션 1 (올인원 서버)
- 사용자 검증 및 피드백 수집
- 비용 절감

**성장 후:** 옵션 2 (마이크로서비스)
- 트래픽 증가 시 점진적 마이그레이션
- Frontend만 먼저 Vercel로 이동 (무료)
- Backend/Celery는 계속 단일 서버 유지

---

## 운영 환경 전환 시 변경 사항

### 1. 환경 변수 분리
```bash
# 개발 환경 (.env.development)
DATABASE_URL=sqlite:///./app.db
REDIS_URL=redis://localhost:6379/0
FRONTEND_URL=http://localhost:3000

# 운영 환경 (.env.production)
DATABASE_URL=postgresql://user:pass@db.example.com:5432/ranking_db
REDIS_URL=redis://redis.example.com:6379/0
FRONTEND_URL=https://ranking-shorts.com
```

### 2. 데이터베이스 변경
```python
# SQLite → PostgreSQL
# requirements.txt에 추가
psycopg2-binary==2.9.9

# config.py 수정
DATABASE_URL = os.getenv("DATABASE_URL")
```

### 3. 정적 파일 서빙
```bash
# 개발: Vite dev server
npm run dev

# 운영: 빌드 후 Nginx 서빙
npm run build
# dist/ 폴더를 Nginx에 배포
```

### 4. 프로세스 관리
```bash
# 개발: 터미널에서 직접 실행
uvicorn app.main:app --reload

# 운영: Systemd 서비스로 관리
sudo systemctl start ranking-backend
sudo systemctl start ranking-celery
```

### 5. 보안 강화
- HTTPS 인증서 (Let's Encrypt)
- 환경 변수 암호화
- CORS 설정 엄격화
- API Rate Limiting
- 로그 모니터링 (Sentry, CloudWatch)

---

## 한 번에 실행하기

아래에서 자동 실행 스크립트를 제공합니다.

---

## 논의 포인트

### 1. 서버 선택
**질문:** 어떤 클라우드 서비스를 선호하시나요?
- AWS (가장 많은 기능, 복잡함)
- DigitalOcean (간단, 개발자 친화적)
- Google Cloud (AI/ML 도구 강력)
- Vultr, Linode (저렴함)
- Vercel + Railway (서버리스, 초간단)

### 2. 배포 전략
**질문:** 언제 운영 환경으로 전환할 계획인가요?
- [ ] MVP 완성 후 즉시
- [ ] 베타 테스터 확보 후
- [ ] 일정 사용자 수 달성 후 (예: 100명)

### 3. 비용 vs 편의성
**질문:** 초기 예산은?
- 옵션 A: $20~40/월 (직접 관리, 학습 필요)
- 옵션 B: $80~200/월 (관리형 서비스, 편리함)
- 옵션 C: 무료 티어 활용 (Vercel + Railway 무료 플랜)

### 4. 확장성 우선순위
**질문:** 예상 동시 사용자 수는?
- ~10명: 로컬 수준 (현재 설정 충분)
- ~100명: 올인원 서버
- ~1000명: 마이크로서비스 필요
- 1000명+: CDN + Auto Scaling + 다중 리전

### 5. 영상 저장 전략
**질문:** 생성된 영상을 어디에 저장할까요?
- 로컬 디스크 (서버 용량 제한)
- AWS S3 / Google Cloud Storage (확장 가능, 비용 발생)
- CDN 연동 (빠른 전송 속도)

### 6. 모니터링 및 로깅
**질문:** 서비스 상태를 어떻게 모니터링할까요?
- 무료: 직접 로그 확인
- 유료: Sentry (에러 추적), Datadog (성능 모니터링)
- 중간: Prometheus + Grafana (오픈소스, 자체 호스팅)

---

## 다음 단계 제안

### 즉시 할 것
1. ✅ 로컬 개발 환경 완성 (완료!)
2. ⏭️ 기능 테스트 및 버그 수정
3. ⏭️ 자동 실행 스크립트 작성 (아래 참고)

### 단기 (1~2주)
1. 도메인 구매 (선택)
2. 클라우드 서비스 선택
3. CI/CD 파이프라인 설정 (GitHub Actions)

### 중기 (1~2개월)
1. 운영 환경 배포
2. 모니터링 설정
3. 백업 자동화

---

## 요약

| 항목 | 로컬 개발 | 운영 초기 | 운영 확장 |
|-----|---------|----------|----------|
| Frontend | Vite Dev | Vercel/Nginx | Vercel + CDN |
| Backend | Uvicorn | Gunicorn | ECS/Cloud Run |
| Redis | Docker | 로컬 Redis | ElastiCache |
| Celery | 터미널 | Systemd | 별도 서버 |
| Database | SQLite | PostgreSQL | RDS + 복제본 |
| 비용/월 | $0 | $20~40 | $80~280 |
| 관리 난이도 | 쉬움 | 보통 | 어려움 |
| 확장성 | 1명 | ~100명 | 1000명+ |
