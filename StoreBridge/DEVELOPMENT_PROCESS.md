# 실전 개발 프로세스 학습 가이드

> StoreBridge 프로젝트를 통해 배우는 **실무 소프트웨어 개발 방법론**

**작성일**: 2025-10-16
**대상**: 주니어~미드 개발자, 실무 프로세스 학습자

---

## 📋 목차

1. [개요: 왜 이 과정이 중요한가?](#개요-왜-이-과정이-중요한가)
2. [Phase 0: 요구사항 분석 & 기술 조사](#phase-0-요구사항-분석--기술-조사)
3. [Phase 1: 아키텍처 설계](#phase-1-아키텍처-설계)
4. [Phase 2: 프로토타입 & 스파이크](#phase-2-프로토타입--스파이크)
5. [Phase 3: 반복 개발 (Iterative Development)](#phase-3-반복-개발-iterative-development)
6. [Phase 4: 테스트 & 품질 관리](#phase-4-테스트--품질-관리)
7. [Phase 5: 배포 & 운영](#phase-5-배포--운영)
8. [실전 팁 & 안티패턴](#실전-팁--안티패턴)
9. [학습 체크리스트](#학습-체크리스트)

---

## 개요: 왜 이 과정이 중요한가?

### ❌ 초보자가 흔히 하는 실수

```
요구사항 듣자마자 → 바로 코딩 시작 → 중간에 막힘 → 처음부터 다시
```

**문제점:**
- 전체 구조 파악 없이 시작 → 나중에 리팩토링 지옥
- API 제약 사항 모름 → 중간에 방향 전환
- 에러 케이스 고려 안 함 → 실전 투입 시 장애
- 확장성 없음 → 기능 추가할 때마다 전체 수정

---

### ✅ 올바른 프로세스

```
요구사항 분석 → 기술 조사 → 아키텍처 설계 →
프로토타입 → 반복 개발 → 테스트 → 배포 → 운영/모니터링
```

**장점:**
- 🎯 **명확한 목표**: 어디로 가는지 알고 시작
- ⏱️ **시간 절약**: 나중에 뒤집을 일이 줄어듦
- 🛡️ **리스크 관리**: 미리 장애 요인 제거
- 📈 **확장 가능**: 기능 추가가 쉬움
- 🤝 **협업 용이**: 팀원이 이해하기 쉬움

---

## Phase 0: 요구사항 분석 & 기술 조사

### 0-1. 요구사항 명확화

#### ❓ **질문으로 시작하기**

초기 요구사항:
> "도매꾹 상품을 네이버 스마트스토어에 자동 등록해줘"

**명확화 질문 목록:**
```
1. 기능 범위
   - 상품 등록만? 수정/삭제도?
   - 재고/가격 동기화 필요?
   - 주문 연동까지?

2. 데이터 볼륨
   - 몇 개나 등록? (100개? 10,000개?)
   - 하루에 몇 번? (1회? 계속?)

3. 제약 사항
   - API 키 있어? 발급 방법은?
   - Rate Limit은?
   - 비용 예산은?

4. 성공 기준
   - 등록 성공률 목표? (100%? 80%?)
   - 반려되면 어떻게? (수동 처리? 자동 재시도?)
   - 속도는? (10초/개? 1분/개?)

5. 운영
   - 누가 사용? (개발자? 비개발자?)
   - 모니터링 필요? (대시보드? 알림?)
   - 장애 시 대응 절차는?
```

#### 📝 **요구사항 문서 작성**

```markdown
# StoreBridge 요구사항 명세서 (PRD - Product Requirements Document)

## 1. 비즈니스 목표
- 도매꾹 상품을 네이버 스마트스토어에 자동 등록하여 수동 작업 시간 90% 절감
- 하루 5,000개 상품 등록 지원

## 2. 기능 요구사항 (Functional Requirements)
- [FR-01] 도매꾹 상품 검색/카테고리 기반 수집
- [FR-02] 상품 정보 정규화 (이미지, 옵션, 가격)
- [FR-03] 네이버 스마트스토어 자동 등록
- [FR-04] 반려 상품 수동 검토 큐
- [FR-05] 가격/재고 동기화 (선택)

## 3. 비기능 요구사항 (Non-Functional Requirements)
- [NFR-01] 등록 성공률 85% 이상
- [NFR-02] 평균 처리 시간 30초/상품 이하
- [NFR-03] API Rate Limit 준수 (도매꾹 180/분, 네이버 2/초)
- [NFR-04] 24/7 무중단 운영
- [NFR-05] 에러 발생 시 5분 이내 알림

## 4. 제약 사항 (Constraints)
- 도매꾹 API: EUC-KR 인코딩, 15K 호출/일
- 네이버 API: OAuth 2.0, IP 화이트리스트, 초당 2회
- 예산: 월 $100 이하 (AWS/GCP 기준)

## 5. 범위 외 (Out of Scope)
- 주문 자동 처리
- 고객 문의 자동 응답
- 경쟁사 가격 분석
```

---

### 0-2. 기술 조사 (Tech Spike)

#### 🔍 **조사해야 할 항목**

```
1. 외부 API
   ✅ 도매꾹 API 문서 읽기
   ✅ 네이버 커머스 API 문서 읽기
   ✅ 실제 호출 테스트 (Postman/curl)
   ✅ Rate Limit 확인
   ✅ 에러 코드 목록 확인

2. 기술 스택 후보
   ✅ 언어: Python vs Node.js vs Go
   ✅ 큐: Celery vs BullMQ vs AWS SQS
   ✅ DB: PostgreSQL vs MongoDB
   ✅ 캐시: Redis vs Memcached

3. 유사 사례 조사
   ✅ GitHub에서 "상품 등록 자동화" 검색
   ✅ 기술 블로그 읽기
   ✅ Stack Overflow 질문 확인

4. 리스크 식별
   ⚠️ 네이버 API 2 TPS 제약 → 병목 가능성
   ⚠️ 옵션 구조 차이 → 변환 복잡도 높음
   ⚠️ 금지어 자동 검출 → 반려율 예측 어려움
```

#### 📊 **기술 조사 결과 문서**

```markdown
# API 조사 결과

## 도매꾹 OpenAPI
- ✅ 공식 API 존재
- ⚠️ EUC-KR 인코딩 필수 (한글 처리 주의)
- ⚠️ Rate Limit: 180/분, 15K/일 → **병목 확인**
- ✅ JSON/XML 응답 지원
- ❓ 상세 스펙 불명확 (실제 테스트 필요)

## 네이버 커머스 API
- ✅ 공식 API 존재
- 🚨 **Rate Limit: 초당 2회 (치명적 제약!)**
- ⚠️ OAuth 2.0 + IP 화이트리스트 (설정 복잡)
- ⚠️ 카테고리별 필수 속성 다름 (사전 매핑 필요)
- ⚠️ 금지어 자동 검출 (블랙박스)
- ✅ GitHub 기술지원 채널 존재

## 기술 스택 결정
| 항목 | 선택 | 이유 |
|------|------|------|
| 언어 | Python 3.11 | 한글 처리 우수, 비동기 I/O, 타입힌트 |
| 웹 프레임워크 | FastAPI | 비동기, 자동 문서화, Pydantic |
| 태스크 큐 | Celery | 복잡한 워크플로우, 우선순위 큐 |
| DB | PostgreSQL | 트랜잭션, JSONB 타입 |
| 캐시 | Redis | 빠름, 메시지 브로커 겸용 |

## 주요 리스크
1. 🚨 네이버 2 TPS 제약 → **병목 최우선 대응 필요**
2. ⚠️ 옵션 구조 변환 복잡도 → **프로토타입 필수**
3. ⚠️ 반려율 예측 불가 → **수동 검토 프로세스 필요**
```

---

### 0-3. 실제 API 테스트 (Proof of Concept)

#### 🧪 **Postman/curl로 먼저 손으로 해보기**

```bash
# 1. 도매꾹 API 테스트
curl -X GET "https://domeggook.com/ssl/api/" \
  -d "ver=4.1" \
  -d "mode=getItemList" \
  -d "aid=YOUR_API_KEY" \
  -d "market=dome" \
  -d "om=json" \
  | jq '.'

# 2. 응답 구조 확인
{
  "success": true,
  "data": {
    "items": [...],
    "total": 100
  }
}

# 3. 네이버 API 토큰 발급 테스트
curl -X POST "https://api.commerce.naver.com/oauth2/token" \
  -d "client_id=..." \
  -d "client_secret=..." \
  -d "grant_type=client_credentials"

# 4. 상품 등록 테스트 (수동으로 JSON 작성)
curl -X POST "https://api.commerce.naver.com/v2/products" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "leafCategoryId": "50000123",
    "name": "테스트 상품",
    "statusType": "SALE",
    "salePrice": 10000
  }'
```

#### 📝 **테스트 결과 기록**

```markdown
# API 테스트 결과

## 도매꾹 getItemList (2025-10-16)
- ✅ 호출 성공
- 응답 시간: 1.2초
- 실제 필드:
  - `item_id`: "DG123456"
  - `name`: "상품명"
  - `price`: 10000 (정수)
  - `images`: ["url1", "url2"] (배열)
  - `options`: null (옵션 없는 상품일 때)
- ⚠️ EUC-KR 인코딩 안 하면 한글 깨짐 확인

## 네이버 상품 등록 (2025-10-16)
- ✅ 1차 시도: 성공
- ❌ 2차 시도: 400 에러 "제조일자 필수"
  → 카테고리별 필수 속성 확인 필요!
- ⚠️ Rate Limit: 5회 연속 호출 시 6번째 429 에러
  → 정확히 초당 2회 제한 확인
```

---

## Phase 1: 아키텍처 설계

### 1-1. High-Level 구조 먼저 그리기

#### 📐 **레이어 아키텍처 결정**

```
1. 어떤 레이어가 필요한가?
   - Client Layer (UI/API)
   - Application Layer (FastAPI)
   - Queue Layer (Celery)
   - Service Layer (비즈니스 로직)
   - Integration Layer (외부 API)
   - Data Layer (DB/Cache/Storage)

2. 각 레이어의 책임은?
   - Client: 사용자 요청 받기
   - Application: 요청 검증, 잡 생성
   - Queue: 비동기 처리, 재시도
   - Service: 데이터 변환, 검증
   - Integration: 외부 API 호출
   - Data: 영속성, 캐싱

3. 레이어 간 통신 방식은?
   - Client → Application: HTTP REST
   - Application → Queue: Celery task
   - Queue → Service: 함수 호출
   - Service → Integration: async/await
   - Service → Data: ORM/Redis client
```

---

### 1-2. 데이터 플로우 설계

#### 🔄 **ETL 파이프라인 상세화**

```
[사용자] "신상품 100개 등록해줘"
   ↓
[FastAPI] POST /jobs
   - 요청 검증
   - Job 레코드 생성 (DB)
   - Celery 태스크 큐에 추가
   ↓
[Celery Worker - Extract]
   - 도매꾹 API 호출 (100개)
   - Rate Limiter 통과
   - Redis 캐시 체크
   - DB에 원본 데이터 저장
   ↓
[Celery Worker - Transform]
   - HTML 클린업
   - 이미지 다운로드/리사이즈
   - 카테고리 매핑
   - 옵션 정규화
   - 검증 (Validator)
   ↓
   검증 실패 → [Manual Review Queue]
   검증 성공 ↓
[Celery Worker - Load]
   - Rate Limiter 획득 (2 TPS)
   - 네이버 API 호출
   - 성공 시 매핑 저장
   - 실패 시 에러 분석 → 재시도 or Review Queue
   ↓
[사용자] GET /jobs/{id}
   - 진행률 조회
   - 에러 목록 확인
```

#### 🎨 **상태 다이어그램**

```
PENDING → VALIDATED → UPLOADING → REGISTERING → COMPLETED
    ↓         ↓            ↓            ↓
 FAILED   MANUAL     RETRYING      MANUAL
         REVIEW                    REVIEW
```

---

### 1-3. 모듈 구조 설계

#### 📁 **디렉토리 구조 결정 원칙**

```
1. 관심사의 분리 (Separation of Concerns)
   - connectors/ : 외부 API만
   - services/ : 비즈니스 로직만
   - models/ : 데이터 구조만

2. 순환 의존성 방지
   - 상위 레이어 → 하위 레이어 (O)
   - 하위 레이어 → 상위 레이어 (X)

   예: api/ → services/ → connectors/ (O)
       connectors/ → api/ (X)

3. 테스트 가능성
   - 각 모듈이 독립적으로 테스트 가능
   - Mock 객체 주입 용이

4. 확장 가능성
   - 새 공급처 추가 시 connectors/에만 파일 추가
   - 새 검증 룰 추가 시 validators/에만 파일 추가
```

#### 🗂️ **실제 구조 예시**

```
app/
├── api/              # 엔드포인트 정의
│   └── jobs.py
├── connectors/       # 외부 시스템 연동
│   ├── domeggook.py
│   └── naver.py
├── services/         # 비즈니스 로직
│   ├── product_service.py
│   └── mapping_service.py
├── workers/          # 백그라운드 작업
│   ├── extract.py
│   ├── transform.py
│   └── load.py
├── models/           # 데이터 모델
│   ├── product.py
│   └── job.py
└── utils/            # 공통 유틸리티
    ├── cache.py
    └── logger.py
```

---

### 1-4. 핵심 컴포넌트 설계

#### ⚙️ **Rate Limiter 설계 사례**

```python
# 1. 요구사항 정리
"""
- 네이버: 초당 2회
- 도매꾹: 초당 3회
- 멀티 워커 환경 (분산)
- Burst 허용 (다음 초 선빌림)
"""

# 2. 알고리즘 선택
"""
✅ Token Bucket
- 이유: Burst 지원, 구현 단순
- 대안: Leaky Bucket (너무 strict)
"""

# 3. 저장소 선택
"""
✅ Redis
- 이유: 분산 환경, INCR 원자성
- 대안: In-memory (단일 프로세스만 가능)
"""

# 4. 인터페이스 설계
"""
class RateLimiter:
    async def acquire(timeout: Optional[float]) -> bool
    async def release()  # 필요시
    async def get_remaining() -> int  # 디버깅용
"""

# 5. 엣지 케이스 고려
"""
- Redis 장애 시? → fallback to in-memory
- 시각 동기화 문제? → 서버 시간 사용
- Race condition? → Lua script로 원자성
"""
```

---

### 1-5. 데이터베이스 스키마 설계

#### 🗄️ **ERD 작성 원칙**

```
1. 정규화 (Normalization)
   - 1NF: 원자값 (배열 컬럼 금지)
   - 2NF: 부분 함수 종속 제거
   - 3NF: 이행 함수 종속 제거

2. 인덱스 전략
   - WHERE 절에 자주 사용되는 컬럼
   - JOIN 키
   - 정렬(ORDER BY) 컬럼

3. JSONB 사용 시기
   - 스키마가 자주 바뀌는 데이터 (metadata)
   - 쿼리 거의 안 하는 데이터 (raw API 응답)

4. 타임스탬프 필수
   - created_at, updated_at 항상 추가
   - 디버깅/분석에 필수
```

#### 📊 **실제 스키마 예시**

```sql
-- 1. 상품 원본 데이터 (도매꾹)
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domeggook_item_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    price INTEGER,
    category VARCHAR(200),
    raw_data JSONB NOT NULL,  -- 도매꾹 응답 전체 (변환 전)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_domeggook_id ON products(domeggook_item_id);

-- 2. 등록 상태 추적
CREATE TABLE product_registrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    state VARCHAR(50) NOT NULL CHECK (state IN (
        'PENDING', 'VALIDATED', 'UPLOADING',
        'REGISTERING', 'COMPLETED', 'RETRYING',
        'MANUAL_REVIEW', 'FAILED'
    )),
    naver_product_id VARCHAR(100),  -- 등록 성공 후 채워짐
    seller_product_code VARCHAR(100) UNIQUE,  -- SKU
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    metadata JSONB,  -- 변환된 데이터, 이미지 URL 등
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_registrations_state ON product_registrations(state);
CREATE INDEX idx_registrations_product ON product_registrations(product_id);

-- 3. 카테고리 매핑
CREATE TABLE category_mappings (
    id SERIAL PRIMARY KEY,
    domeggook_category VARCHAR(200) NOT NULL,
    naver_leaf_category_id VARCHAR(50) NOT NULL,
    required_attributes JSONB,  -- {"제조일자": "required", ...}
    confidence FLOAT DEFAULT 1.0,  -- 자동 매핑 신뢰도
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(domeggook_category, naver_leaf_category_id)
);
CREATE INDEX idx_category_dg ON category_mappings(domeggook_category);

-- 4. 작업 추적
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) NOT NULL,  -- IMPORT, SYNC, etc.
    status VARCHAR(50) NOT NULL,  -- PENDING, RUNNING, COMPLETED, FAILED
    total_count INTEGER,
    success_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    error_summary TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created ON jobs(created_at DESC);
```

---

## Phase 2: 프로토타입 & 스파이크

### 2-1. 핵심 리스크부터 검증

#### 🧪 **"가장 어려운 부분"을 먼저 만들어보기**

StoreBridge 프로젝트의 핵심 리스크:
1. ⚠️ **네이버 2 TPS 제약**
2. ⚠️ **옵션 구조 변환**
3. ⚠️ **카테고리 속성 매핑**

**프로토타입 목표:**
```
✅ 1개 상품 End-to-End 성공
   - 도매꾹에서 조회
   - 옵션 변환
   - 네이버에 등록
   - 실제 스마트스토어에서 확인

⏱️ 시간 제한: 3일
📦 코드 품질: 낮아도 OK (나중에 리팩토링)
🎯 목적: "실현 가능성" 검증
```

---

### 2-2. 프로토타입 코드 예시

#### 🛠️ **빠르게 던져보기 (Throwaway Prototype)**

```python
# prototype.py - 품질 낮아도 OK, 일단 돌아가게!

import requests
import json

# 1. 도매꾹에서 상품 1개 조회
def fetch_product():
    response = requests.get('https://domeggook.com/ssl/api/', params={
        'ver': '4.5',
        'mode': 'getItemView',
        'aid': 'YOUR_KEY',
        'market': 'dome',
        'om': 'json',
        'item_id': '12345'
    })
    return response.json()

# 2. 네이버 형식으로 변환 (하드코딩 OK)
def transform(product):
    return {
        'leafCategoryId': '50000123',  # 일단 고정값
        'name': product['name'],
        'statusType': 'SALE',
        'salePrice': product['price'],
        'detailContent': '<div>' + product['description'] + '</div>',
        'images': [{'url': img} for img in product['images'][:10]],
        # 옵션은 일단 단순 케이스만
        'options': None if not product.get('options') else [
            {
                'type': 'SIMPLE',
                'name': '색상',
                'values': [{'name': opt, 'price': 0} for opt in product['options']]
            }
        ]
    }

# 3. 네이버에 등록
def register_to_naver(product_data):
    # OAuth 토큰 발급
    token_response = requests.post('https://api.commerce.naver.com/oauth2/token', data={
        'client_id': 'YOUR_ID',
        'client_secret': 'YOUR_SECRET',
        'grant_type': 'client_credentials'
    })
    token = token_response.json()['access_token']

    # 상품 등록
    response = requests.post(
        'https://api.commerce.naver.com/v2/products',
        headers={'Authorization': f'Bearer {token}'},
        json=product_data
    )
    return response.json()

# 4. 실행
if __name__ == '__main__':
    print("1. 도매꾹에서 상품 조회...")
    product = fetch_product()
    print(f"   ✅ {product['name']}")

    print("2. 네이버 형식으로 변환...")
    naver_product = transform(product)
    print(f"   ✅ 변환 완료")

    print("3. 네이버에 등록...")
    result = register_to_naver(naver_product)
    print(f"   ✅ 등록 완료: {result.get('productId')}")
```

#### 📝 **프로토타입 결과 기록**

```markdown
# 프로토타입 테스트 결과 (2025-10-16)

## 테스트 1: 옵션 없는 단순 상품
- ✅ 성공
- 소요 시간: 3.2초

## 테스트 2: 단일 옵션 상품 (색상)
- ✅ 성공
- 소요 시간: 4.1초

## 테스트 3: 조합 옵션 상품 (색상 × 사이즈)
- ❌ 실패: 400 에러 "Invalid option structure"
- 원인: 네이버는 COMBINATION 타입 필요
- 해결: 옵션 파서 로직 보강 필요

## 테스트 4: 카테고리 속성 누락
- ❌ 실패: 400 에러 "제조일자 필수"
- 원인: 리프 카테고리마다 필수 속성 다름
- 해결: 카테고리 속성 조회 API 먼저 호출 필요

## 결론
✅ 기본 플로우 실현 가능성 확인
⚠️ 옵션 변환 로직 복잡 → 별도 모듈로 분리
⚠️ 카테고리 속성 사전 체크 필수
```

---

### 2-3. 프로토타입에서 본격 코드로 전환

#### 🔄 **리팩토링 체크리스트**

```
[ ] 하드코딩 제거
    - API 키 → 환경변수
    - URL → 상수
    - 카테고리 ID → DB/CSV

[ ] 에러 처리 추가
    - try-except
    - 재시도 로직
    - 로깅

[ ] 함수 분리
    - 한 함수 = 한 가지 역할
    - 긴 함수 쪼개기

[ ] 타입 힌트 추가
    - def fetch_product() -> Dict[str, Any]

[ ] 테스트 작성
    - 단위 테스트
    - Mock 사용

[ ] 문서화
    - Docstring
    - README
```

---

## Phase 3: 반복 개발 (Iterative Development)

### 3-1. 작은 단위로 쪼개기

#### 📦 **Feature 단위 개발**

```
❌ 나쁜 예: "상품 등록 기능 완성" (너무 큼, 3주 소요)

✅ 좋은 예:
  Week 1:
    - [ ] 도매꾹 커넥터 (API 호출만)
    - [ ] 단위 테스트
    - [ ] 1개 상품 조회 성공

  Week 2:
    - [ ] 네이버 커넥터 (OAuth + 1개 등록)
    - [ ] Rate Limiter
    - [ ] 1개 상품 등록 성공

  Week 3:
    - [ ] Transform 레이어 (HTML, 이미지)
    - [ ] 10개 배치 테스트

  Week 4:
    - [ ] Validator (카테고리, 금지어)
    - [ ] 상태 기계
    - [ ] 에러 핸들링
```

---

### 3-2. TDD (Test-Driven Development) 적용

#### 🔴 **Red → Green → Refactor**

```python
# 1단계: 실패하는 테스트 먼저 작성 (Red)
def test_rate_limiter_allows_two_requests_per_second():
    limiter = RateLimiter(max_tps=2)

    # 첫 2개는 성공
    assert limiter.acquire() == True
    assert limiter.acquire() == True

    # 3번째는 실패
    assert limiter.acquire() == False

# 실행: pytest → FAILED (RateLimiter가 아직 없음)

# 2단계: 최소한으로 통과시키기 (Green)
class RateLimiter:
    def __init__(self, max_tps):
        self.max_tps = max_tps
        self.count = 0

    def acquire(self):
        if self.count < self.max_tps:
            self.count += 1
            return True
        return False

# 실행: pytest → PASSED

# 3단계: 리팩토링 (Refactor)
# - Redis 연동 추가
# - 시간 기반 리셋 추가
# - Lua script로 원자성 보장
```

---

### 3-3. 코드 리뷰 문화

#### 👀 **셀프 리뷰 체크리스트**

```
[ ] 읽기 쉬운가?
    - 변수명이 명확한가?
    - 함수가 너무 길지 않은가? (50줄 이내)

[ ] 테스트 가능한가?
    - Mock 주입 가능한가?
    - 부수 효과(side effect)가 명확한가?

[ ] 에러 처리했는가?
    - 외부 API 실패 시?
    - DB 연결 끊김 시?

[ ] 로그 남겼는가?
    - 디버깅 가능한 정보?
    - 민감 정보 (API 키) 제외?

[ ] 문서화했는가?
    - Docstring?
    - 복잡한 로직에 주석?

[ ] 성능 고려했는가?
    - N+1 쿼리?
    - 불필요한 반복문?
```

---

## Phase 4: 테스트 & 품질 관리

### 4-1. 테스트 피라미드

```
       /\
      /  \  E2E (10%)
     /____\
    /      \  Integration (30%)
   /________\
  /          \ Unit (60%)
 /____________\
```

#### 🧪 **각 레벨별 테스트**

```python
# 1. Unit Test (단위 테스트)
def test_option_mapper_parses_combination():
    mapper = OptionMapper()
    raw = ['블랙-S', '블랙-M', '화이트-S', '화이트-M']

    result = mapper.parse_combination(raw)

    assert result['type'] == 'COMBINATION'
    assert len(result['dimensions']) == 2
    assert result['dimensions'][0]['name'] == '색상'

# 2. Integration Test (통합 테스트)
@pytest.mark.integration
async def test_domeggook_client_fetches_product():
    client = DomeggookClient(api_key=os.getenv('DOMEGGOOK_API_KEY'))

    product = await client.get_item_view('12345')

    assert product['item_id'] == '12345'
    assert 'name' in product
    assert 'price' in product

# 3. E2E Test (종단간 테스트)
@pytest.mark.e2e
async def test_full_registration_flow():
    # 1. 상품 수집
    product = await domeggook_client.get_item_view('12345')

    # 2. 변환
    transformed = await transform_service.transform(product)

    # 3. 검증
    is_valid = await validator.validate(transformed)
    assert is_valid

    # 4. 등록
    naver_product_id = await naver_client.create_product(transformed)
    assert naver_product_id is not None
```

---

### 4-2. 외부 API 테스트: VCR.py

#### 📼 **API 응답 녹화/재생**

```python
import vcr

# 1. 첫 실행: 실제 API 호출 & 녹화
@vcr.use_cassette('tests/fixtures/domeggook_item_12345.yaml')
def test_fetch_product():
    client = DomeggookClient(api_key='test_key')
    product = client.get_item_view('12345')

    assert product['name'] == '테스트 상품'

# 2. 두 번째 실행부터: 녹화된 응답 재생 (실제 API 호출 안 함!)
# → 빠름, API 쿼터 소비 안 함, 오프라인 가능
```

녹화 파일 (`tests/fixtures/domeggook_item_12345.yaml`):
```yaml
interactions:
- request:
    method: GET
    uri: https://domeggook.com/ssl/api/?ver=4.5&mode=getItemView&item_id=12345
  response:
    status: 200
    body:
      string: '{"success": true, "data": {"item_id": "12345", "name": "테스트 상품"}}'
```

---

### 4-3. 정적 분석 도구

#### 🔍 **자동화된 코드 품질 검사**

```bash
# 1. Ruff (린터 + 포매터)
ruff check app/
ruff format app/

# 2. Mypy (타입 체크)
mypy app/ --strict

# 3. Bandit (보안 취약점)
bandit -r app/

# 4. Coverage (테스트 커버리지)
pytest --cov=app --cov-report=html
```

#### ⚙️ **pre-commit 훅 설정**

`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.0
    hooks:
      - id: mypy
```

```bash
# 설치
pre-commit install

# 이제 git commit 시 자동 실행!
```

---

## Phase 5: 배포 & 운영

### 5-1. 배포 전 체크리스트

```
[ ] 환경 변수 설정
    - .env 파일 준비
    - 프로덕션 API 키 확인

[ ] 데이터베이스 마이그레이션
    - alembic upgrade head
    - 백업 확인

[ ] 시드 데이터
    - 카테고리 매핑 테이블
    - 금지어 목록

[ ] 보안
    - API 키 노출 확인 (git secrets)
    - HTTPS 설정
    - CORS 설정

[ ] 모니터링
    - Prometheus/Grafana 대시보드
    - Sentry 알림 테스트
    - 로그 수집 확인

[ ] 성능 테스트
    - 100개 상품 등록 테스트
    - Rate Limit 체크
    - 메모리 누수 확인

[ ] 장애 대응 계획
    - Rollback 절차
    - 긴급 연락처
    - 매뉴얼 작성
```

---

### 5-2. 단계적 배포 (Staged Rollout)

#### 🚦 **점진적으로 확대하기**

```
Day 1: Canary (카나리 배포)
  - 1개 상품만 등록
  - 모든 로그 확인
  - 에러 없으면 다음 단계

Day 3: Pilot (파일럿)
  - 10개 상품 등록
  - 반려 사유 수집
  - 매핑 룰 보강

Week 2: Beta
  - 100개 상품 등록
  - 성능 메트릭 수집
  - 병목 구간 최적화

Week 3: Full Rollout
  - 1,000개 상품 등록
  - 24/7 모니터링
  - On-call 대기
```

---

### 5-3. 모니터링 & 알림

#### 📊 **핵심 메트릭 정의**

```python
from prometheus_client import Counter, Histogram, Gauge

# 1. 비즈니스 메트릭
products_registered_total = Counter(
    'storebridge_products_registered_total',
    'Total products registered',
    ['status']  # success/failed
)

registration_success_rate = Gauge(
    'storebridge_registration_success_rate',
    'Success rate (last 1 hour)'
)

# 2. 성능 메트릭
api_call_duration = Histogram(
    'storebridge_api_call_duration_seconds',
    'API call duration',
    ['api_name'],  # domeggook/naver
    buckets=[0.1, 0.5, 1, 2, 5, 10]
)

# 3. 인프라 메트릭
queue_depth = Gauge(
    'storebridge_queue_depth',
    'Current queue depth',
    ['queue_name']
)

rate_limit_remaining = Gauge(
    'storebridge_rate_limit_remaining',
    'Remaining rate limit',
    ['api_name']
)
```

#### 🚨 **알림 규칙**

```yaml
# alerting_rules.yml
groups:
  - name: storebridge
    interval: 1m
    rules:
      # 성공률 70% 이하 → 긴급
      - alert: RegistrationSuccessRateLow
        expr: storebridge_registration_success_rate < 0.7
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "등록 성공률 70% 이하"

      # Rate Limit 90% 도달 → 경고
      - alert: RateLimitAlmostExceeded
        expr: storebridge_rate_limit_remaining < 10
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Rate Limit 90% 도달"

      # 큐 대기 1시간 초과 → 경고
      - alert: QueueDepthHigh
        expr: storebridge_queue_depth > 1000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "큐에 1000개 이상 대기 중"
```

---

### 5-4. 장애 대응 (Incident Response)

#### 🆘 **Runbook (대응 매뉴얼)**

```markdown
# Incident: 네이버 API 429 Too Many Requests

## 증상
- 상품 등록 실패율 급증
- 로그에 "429" 다수
- Rate Limit Exceeded 알림

## 원인
1. 다른 워커가 동시 호출
2. Rate Limiter 버그
3. 네이버 측 제한 강화

## 즉시 조치
1. Celery 워커 일시 중지
   ```bash
   docker-compose stop worker-normal worker-batch
   ```

2. Redis Rate Limiter 키 확인
   ```bash
   redis-cli KEYS "naver:ratelimit:*"
   redis-cli GET "naver:ratelimit:1697481234"
   ```

3. 수동으로 1개 등록 테스트
   ```bash
   curl -X POST http://localhost:8000/api/products/test
   ```

## 근본 원인 분석 (RCA)
- [ ] Rate Limiter 로직 검토
- [ ] 동시성 테스트
- [ ] 네이버 측 변경 사항 확인 (GitHub Discussions)

## 재발 방지
- Rate Limiter 단위 테스트 추가
- 알림 임계값 70% → 80%로 완화
- Circuit Breaker 패턴 도입
```

---

## 실전 팁 & 안티패턴

### ✅ **Best Practices**

#### 1. **로그를 구조화하라**
```python
# ❌ 나쁜 예
print(f"상품 등록: {product_id}")

# ✅ 좋은 예
logger.info(
    "Product registered",
    extra={
        'product_id': product_id,
        'naver_product_id': naver_id,
        'duration_ms': duration,
        'retry_count': retry_count
    }
)
# → Grafana/Loki에서 구조화된 쿼리 가능
```

#### 2. **에러 메시지는 액션 가능하게**
```python
# ❌ 나쁜 예
raise ValueError("Invalid data")

# ✅ 좋은 예
raise ValueError(
    f"Category {category_id} not found in mappings. "
    f"Please add to data/category_mappings.csv"
)
```

#### 3. **설정은 환경변수로, 비밀은 Secrets Manager로**
```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 공개 설정
    max_retries: int = 3
    log_level: str = "INFO"

    # 비밀 (환경변수/AWS Secrets Manager에서 로드)
    domeggook_api_key: str
    naver_client_secret: str

    class Config:
        env_file = ".env"
        env_prefix = "STOREBRIDGE_"

settings = Settings()
```

#### 4. **Graceful Degradation (점진적 성능 저하)**
```python
# Redis 장애 시에도 서비스 유지
async def get_cached_categories():
    try:
        return await redis.get('categories')
    except RedisConnectionError:
        logger.warning("Redis unavailable, fetching from DB")
        return await db.query(Category).all()
```

---

### ❌ **안티패턴 (피해야 할 것)**

#### 1. **God Object (만능 클래스)**
```python
# ❌ 나쁜 예
class ProductManager:
    def fetch_from_domeggook(self): ...
    def transform(self): ...
    def validate(self): ...
    def upload_images(self): ...
    def register_to_naver(self): ...
    def send_email(self): ...
    # → 너무 많은 책임!

# ✅ 좋은 예: 단일 책임 원칙
class DomeggookClient: ...
class ProductTransformer: ...
class ProductValidator: ...
class ImageUploader: ...
class NaverClient: ...
```

#### 2. **Magic Numbers (마법 숫자)**
```python
# ❌ 나쁜 예
if retry_count > 3:
    await asyncio.sleep(300)

# ✅ 좋은 예
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 300

if retry_count > MAX_RETRIES:
    await asyncio.sleep(RETRY_BACKOFF_SECONDS)
```

#### 3. **Silent Failures (조용한 실패)**
```python
# ❌ 나쁜 예
try:
    await upload_image(img)
except Exception:
    pass  # 😱 에러 무시!

# ✅ 좋은 예
try:
    await upload_image(img)
except Exception as e:
    logger.error(f"Image upload failed: {e}", exc_info=True)
    await error_queue.enqueue({
        'type': 'IMAGE_UPLOAD_FAILED',
        'image_url': img.url,
        'error': str(e)
    })
    raise  # 상위로 전파
```

#### 4. **Premature Optimization (성급한 최적화)**
```python
# ❌ 나쁜 예: 아직 병목도 아닌데 복잡하게
# (병목 프로파일링도 안 해봤는데 "느릴 것 같아서" 최적화)

# ✅ 좋은 예:
# 1. 먼저 단순하게 구현
# 2. 프로파일링으로 병목 확인
# 3. 병목만 최적화
```

---

## 학습 체크리스트

### 🎓 **이 가이드를 통해 배워야 할 것**

#### Level 1: 기초
- [ ] 요구사항을 명확한 문서로 작성할 수 있다
- [ ] 외부 API 문서를 읽고 Postman으로 테스트할 수 있다
- [ ] 기술 스택을 선택할 때 근거를 댈 수 있다
- [ ] 프로토타입을 빠르게 만들 수 있다

#### Level 2: 중급
- [ ] 레이어 아키텍처를 설계할 수 있다
- [ ] ERD를 그리고 인덱스를 설계할 수 있다
- [ ] Rate Limiter 같은 핵심 컴포넌트를 직접 구현할 수 있다
- [ ] 단위/통합 테스트를 작성할 수 있다
- [ ] Docker Compose로 로컬 환경을 구성할 수 있다

#### Level 3: 고급
- [ ] 상태 기계(State Machine)를 설계하고 구현할 수 있다
- [ ] 에러를 분류하고 재시도 전략을 세울 수 있다
- [ ] Prometheus/Grafana로 모니터링을 구축할 수 있다
- [ ] 장애 대응 매뉴얼(Runbook)을 작성할 수 있다
- [ ] 단계적 배포(Staged Rollout) 전략을 수립할 수 있다

---

## 📚 더 공부할 것들

### 추천 자료

#### 아키텍처
- 📘 "Clean Architecture" - Robert C. Martin
- 📘 "Domain-Driven Design" - Eric Evans
- 🎥 [The Clean Code Talks](https://www.youtube.com/watch?v=4F72VULWFvc)

#### 테스트
- 📘 "Test Driven Development" - Kent Beck
- 🔗 [pytest 공식 문서](https://docs.pytest.org/)

#### 분산 시스템
- 📘 "Designing Data-Intensive Applications" - Martin Kleppmann
- 🎥 [AWS re:Invent - Eventual Consistency](https://www.youtube.com/watch?v=9GFhGJcqBx8)

#### 운영
- 📘 "Site Reliability Engineering" - Google
- 🔗 [The Twelve-Factor App](https://12factor.net/)

---

## 🎯 마무리: 개발 프로세스의 핵심

### 기억해야 할 3가지

1. **"빨리 가려면 천천히 가라"**
   - 요구사항 분석 → 아키텍처 설계 → 프로토타입
   - 처음에 시간 들여도 나중에 10배 절약

2. **"리스크부터 제거하라"**
   - 가장 어려운 부분을 먼저 검증
   - 프로토타입으로 실현 가능성 확인

3. **"작게 자주 배포하라"**
   - 1개 → 10개 → 100개 → 1,000개
   - 단계마다 피드백 수집 & 개선

---

**작성자**: StoreBridge Team
**최종 수정**: 2025-10-16
**버전**: 1.0

---

## 부록: StoreBridge 프로젝트 타임라인 예시

```
Week 0: 준비
  Day 1-3: 요구사항 분석, API 조사
  Day 4-5: Postman 테스트, 프로토타입

Week 1-2: 기반 구축
  - 프로젝트 셋업 (Docker, DB)
  - 도매꾹/네이버 커넥터
  - Rate Limiter
  - 1개 상품 E2E 성공

Week 3-4: 파이프라인
  - Transform 레이어
  - Celery 워커
  - 10개 배치 테스트

Week 5-6: 안정화
  - Validator, 상태 기계
  - 에러 핸들링
  - 100개 스트레스 테스트

Week 7-8: 운영 준비
  - 모니터링 (Grafana)
  - 알림 (Sentry)
  - 매뉴얼 작성
  - 파일럿 (500개)

Week 9+: 운영 & 개선
  - 실전 투입
  - 반려 사유 분석
  - 매핑 룰 보강
  - 성능 최적화
```

이제 당신도 **실무 개발 프로세스**를 마스터했습니다! 🎉
