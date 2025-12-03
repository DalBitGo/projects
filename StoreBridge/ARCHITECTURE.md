# StoreBridge 아키텍처 명세서

> 도매꾹 상품을 네이버 스마트스토어에 자동 등록하는 ETL 파이프라인

**작성일**: 2025-10-16
**버전**: 1.0

---

## 📋 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [시스템 아키텍처](#시스템-아키텍처)
3. [기술 스택](#기술-스택)
4. [API 분석](#api-분석)
5. [데이터 플로우](#데이터-플로우)
6. [모듈 설계](#모듈-설계)
7. [핵심 컴포넌트](#핵심-컴포넌트)
8. [성능 & 제약사항](#성능--제약사항)
9. [에러 핸들링](#에러-핸들링)
10. [배포 전략](#배포-전략)
11. [개발 로드맵](#개발-로드맵)

---

## 프로젝트 개요

### 목표
도매꾹에서 상품 정보(이름, 설명, 이미지, 옵션)를 추출하여 네이버 스마트스토어에 자동으로 대량 등록

### 핵심 요구사항
- ✅ 공식 API 연동 (크롤링 회피)
- ✅ 대량 등록 지원 (하루 5,000~10,000개)
- ✅ 옵션/이미지 자동 변환
- ✅ 반려 처리 자동화
- ✅ 재고/가격 동기화

### 주요 과제
1. **Rate Limit 관리** (네이버 2 TPS 제약)
2. **카테고리/속성 매핑** (복잡한 필수 속성)
3. **옵션 구조 변환** (도매꾹 ↔ 네이버 스키마 차이)
4. **반려 처리** (금지어, 이미지 규격, 속성 불일치)

---

## 시스템 아키텍처

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Client Layer                           │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │  Admin UI   │  │  REST API    │  │  CLI Tools       │    │
│  └─────────────┘  └──────────────┘  └──────────────────┘    │
└──────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│                     Application Layer                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              FastAPI Web Server                       │   │
│  │  - Job Management API                                 │   │
│  │  - Status Monitoring API                              │   │
│  │  - Manual Review Queue API                            │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│                      Job Queue Layer                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                  Celery Workers                         │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │ │
│  │  │  Urgent  │  │  Normal  │  │  Batch   │  │  Sync  │ │ │
│  │  │  Queue   │  │  Queue   │  │  Queue   │  │  Queue │ │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│              Redis (Message Broker + Cache)                  │
└──────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│                      Service Layer                            │
│  ┌───────────────────┐  ┌────────────────────────────────┐  │
│  │  ETL Pipeline     │  │  Business Services             │  │
│  │  - Extract        │  │  - Validation                  │  │
│  │  - Transform      │  │  - Mapping                     │  │
│  │  - Load           │  │  - Rate Limiting               │  │
│  └───────────────────┘  └────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│                    Integration Layer                          │
│  ┌──────────────────┐              ┌────────────────────┐   │
│  │ Domeggook API    │              │ Naver Commerce API │   │
│  │ - Product List   │              │ - Product Register │   │
│  │ - Product Detail │              │ - Category Query   │   │
│  │ - Images         │              │ - Image Upload     │   │
│  └──────────────────┘              └────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│                      Data Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  PostgreSQL  │  │    Redis     │  │   S3/Storage     │  │
│  │  - Products  │  │  - Cache     │  │  - Images        │  │
│  │  - Mappings  │  │  - Sessions  │  │  - Backups       │  │
│  │  - Jobs      │  │  - Locks     │  │                  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## 기술 스택

### Backend
| 항목 | 기술 | 버전 | 선택 이유 |
|------|------|------|-----------|
| **언어** | Python | 3.11+ | 타입힌트, 비동기 I/O, 한글 처리 우수 |
| **웹 프레임워크** | FastAPI | 0.104+ | 비동기, 자동 문서화, Pydantic 통합 |
| **태스크 큐** | Celery | 5.3+ | 복잡한 워크플로우, 우선순위 큐 지원 |
| **메시지 브로커** | Redis | 7.0+ | 빠른 속도, 캐시 겸용 |
| **데이터베이스** | PostgreSQL | 15+ | 트랜잭션, JSON 타입, 안정성 |
| **ORM** | SQLAlchemy | 2.0+ | 비동기 지원, 타입 안전성 |
| **HTTP 클라이언트** | httpx | 0.25+ | 비동기, HTTP/2 지원 |
| **스키마 검증** | Pydantic | 2.0+ | 타입 안전성, 자동 검증 |

### Infrastructure
| 항목 | 기술 | 용도 |
|------|------|------|
| **컨테이너** | Docker | 격리된 환경 |
| **오케스트레이션** | Docker Compose | 로컬/개발 환경 |
| **프록시** | Nginx | 리버스 프록시, 로드 밸런싱 |
| **스토리지** | MinIO / S3 | 이미지 저장 |

### Monitoring & Observability
| 항목 | 기술 | 용도 |
|------|------|------|
| **메트릭** | Prometheus | 시계열 데이터 수집 |
| **시각화** | Grafana | 대시보드 |
| **로그 수집** | Loki | 중앙 로그 관리 |
| **에러 추적** | Sentry | 예외 모니터링 |
| **APM** | OpenTelemetry | 분산 추적 |

### Development
| 항목 | 기술 | 용도 |
|------|------|------|
| **테스트** | Pytest | 단위/통합 테스트 |
| **API 모킹** | VCR.py | 외부 API 테스트 |
| **린터** | Ruff | 빠른 린팅 |
| **포매터** | Black | 코드 스타일 통일 |
| **타입 체크** | Mypy | 정적 타입 검사 |

---

## API 분석

### 도매꾹 OpenAPI

#### 기본 정보
```yaml
Base URL: https://domeggook.com/ssl/api/
인증 방식: API Key (쿼리 파라미터)
응답 형식: JSON / XML
인코딩: EUC-KR ⚠️
```

#### Rate Limits
```
분당: 180회 (3 TPS)
일일: 15,000회
→ 실제 하루 수집량: ~7,500 상품 (상품당 2 API 호출)
```

#### 주요 엔드포인트
| API | 메서드 | 버전 | 용도 | 파라미터 |
|-----|--------|------|------|----------|
| `getItemList` | GET | 4.1 | 상품 목록 조회 | keyword, category, page |
| `getItemView` | GET | 4.5 | 상품 상세 조회 | item_id |
| `getImageAllowItems` | POST | 1.1 | 이미지 허용 상품 | - |
| `getCategoryList` | GET | 1.0 | 카테고리 목록 | - |
| `getCat` | GET | 2.0 | 카테고리 상세 | category_id |

#### 요청 예시
```python
import requests

params = {
    'ver': '4.1',
    'mode': 'getItemList',
    'aid': 'YOUR_API_KEY',
    'market': 'dome',
    'om': 'json',
    'keyword': '여성의류'.encode('euc-kr'),
    'page': 1
}

response = requests.get('https://domeggook.com/ssl/api/', params=params)
data = response.json()
```

#### 응답 구조 (추정)
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "item_id": "12345",
        "name": "상품명",
        "price": 10000,
        "images": ["url1", "url2"],
        "category": "카테고리",
        "options": [...]
      }
    ],
    "total": 1000,
    "page": 1
  }
}
```

#### 주의사항
- ⚠️ **EUC-KR 인코딩** 필수 (한글 파라미터)
- ⚠️ 상세 스펙 불명확 → 실제 테스트 필요
- ⚠️ API 버전별 응답 차이 확인 필요

---

### 네이버 커머스 API

#### 기본 정보
```yaml
Base URL: https://api.commerce.naver.com
인증 방식: OAuth 2.0 (App ID + Secret)
응답 형식: JSON
인코딩: UTF-8
```

#### Rate Limits ⚠️ (치명적!)
```
TPS: 2회/초 (매우 낮음!)
알고리즘: Token Bucket
Burst Max: 다음 1초 선빌림 가능 (단, 연속 불가)
초과 시: HTTP 429

→ 이론적 최대: 172,800 호출/일
→ 현실적 가용: ~96,000 호출/일 (재시도/오버헤드)
→ 상품당 5 호출 가정: ~19,000 상품/일
→ 안전 마진 50%: 9,000~10,000 상품/일
```

#### 인증 플로우
```
1. 커머스API센터에서 앱 등록
   - 통합매니저 계정만 가능
   - IP 화이트리스트 등록 (최대 3개)
   - API 그룹 선택 (상품, 주문, 정산 등)

2. 애플리케이션 ID & Secret 발급

3. 판매자센터에서 "API 사용" ON 설정

4. OAuth 2.0 토큰 발급
   POST /oauth2/token
   {
     "client_id": "...",
     "client_secret": "...",
     "grant_type": "client_credentials"
   }

5. API 호출 시 Bearer Token 사용
```

#### 주요 엔드포인트 (추정)
| API | 메서드 | 용도 | 필수 파라미터 |
|-----|--------|------|---------------|
| `/v2/categories` | GET | 카테고리 목록 | - |
| `/v2/categories/{id}/attributes` | GET | 카테고리 필수 속성 | category_id |
| `/v2/products` | POST | 상품 등록 | leafCategoryId, name, statusType |
| `/v2/products/{id}` | PUT | 상품 수정 | product_id |
| `/v2/products/{id}/images` | POST | 이미지 업로드 | product_id, image_file |
| `/v2/products/{id}/options` | POST | 옵션 등록 | product_id, options |

#### 상품 등록 요청 구조 (추정)
```json
{
  "leafCategoryId": "50000123",
  "statusType": "SALE",
  "name": "상품명",
  "salePrice": 10000,
  "stockQuantity": 100,
  "images": [
    {"url": "https://..."},
    {"url": "https://..."}
  ],
  "detailContent": "<div>상세 설명 HTML</div>",
  "options": [
    {
      "type": "COMBINATION",
      "name": "색상",
      "values": [
        {"name": "블랙", "price": 0, "stock": 50},
        {"name": "화이트", "price": 0, "stock": 50}
      ]
    }
  ],
  "attributes": {
    "제조일자": "2025-01-01",
    "소재": "면 100%",
    "세탁방법": "드라이클리닝"
  },
  "sellerProductCode": "SKU-12345"
}
```

#### 알려진 제약사항
1. **카테고리 속성**
   - 카테고리마다 필수 속성이 다름
   - 속성값 불일치 시 반려
   - 사전에 `/v2/categories/{id}/attributes` 호출 필수

2. **옵션 구조**
   - 단일옵션 / 조합옵션 / 독립옵션 구분
   - 그룹 상품 수정이 복잡함
   - 옵션 삭제 제한적 (재등록 필요할 수도)

3. **이미지 규격**
   - 최소: 500x500px
   - 최대: 12MB
   - 형식: JPG, PNG, GIF
   - 외부 URL 허용 여부 불명확

4. **금지어 / 정책**
   - 자동 검출 (블랙박스)
   - 사전 체크 불가
   - 반려 후 수동 수정 필요

#### 기술 지원
- GitHub: `commerce-api-naver/commerce-api`
- 카테고리: 공지사항, 릴리즈 노트, 묻고답하기, FAQ
- ⚠️ 토큰/시크릿 공유 금지

---

## 데이터 플로우

### ETL 파이프라인

```
┌─────────────────────────────────────────────────────────────┐
│                      EXTRACT (도매꾹)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. 검색/카테고리/공급처 기반 상품 목록 조회          │  │
│  │  2. 상품 상세 정보 조회 (페이징)                      │  │
│  │  3. 이미지 URL 수집                                   │  │
│  │  4. 옵션/가격/재고 정보 추출                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓                                 │
│              Redis Cache (중복 방지, 1시간)                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    TRANSFORM (정규화)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. HTML 클린업                                       │  │
│  │     - 금지 태그 제거 (script, style, iframe)         │  │
│  │     - 인라인 스타일 정리                              │  │
│  │     - 금지어 필터링                                   │  │
│  │                                                        │  │
│  │  2. 이미지 파이프라인                                 │  │
│  │     - 원본 다운로드                                   │  │
│  │     - 규격 검증 (500x500 이상)                        │  │
│  │     - 리사이즈 / WebP 변환                            │  │
│  │     - S3 업로드                                       │  │
│  │                                                        │  │
│  │  3. 카테고리 매핑                                     │  │
│  │     - 도매꾹 카테고리 → 네이버 리프 카테고리         │  │
│  │     - 필수 속성 조회 (캐시 우선)                      │  │
│  │     - 속성값 자동 채우기 (룰 기반)                    │  │
│  │                                                        │  │
│  │  4. 옵션 정규화                                       │  │
│  │     - 옵션명 표준화 (색상/색깔/컬러 → 색상)          │  │
│  │     - 네이버 옵션 스키마로 변환                       │  │
│  │     - 가격 차이 / 재고 매핑                           │  │
│  │                                                        │  │
│  │  5. 가격 규칙 적용                                    │  │
│  │     - 마진율 / 쿠폰 / 수수료 반영                     │  │
│  │     - 최소/최대 가격 검증                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓                                 │
│         Validation (카테고리/속성/이미지/금지어)             │
└─────────────────────────────────────────────────────────────┘
                              ↓
                   검증 실패 → Manual Review Queue
                              ↓
                         검증 성공
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  LOAD (네이버 스마트스토어)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Rate Limiter 획득 (2 TPS)                         │  │
│  │  2. 이미지 업로드 (필요시)                            │  │
│  │  3. 상품 등록 API 호출                                │  │
│  │  4. 옵션 등록 (별도 API일 경우)                       │  │
│  │  5. sellerProductCode 매핑 저장                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓                                 │
│                   등록 성공 → COMPLETED                      │
│                   등록 실패 ↓                                │
│            ┌──────────────────────────────┐                 │
│            │   에러 분석                   │                 │
│            ├──────────────────────────────┤                 │
│            │ 429 Rate Limit → 지수 백오프  │                 │
│            │ 속성 불일치 → Review Queue    │                 │
│            │ 금지어 → 자동 치환 재시도     │                 │
│            │ 이미지 오류 → 재업로드        │                 │
│            │ 기타 → 3회 재시도             │                 │
│            └──────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

### 상태 기계 (State Machine)

```
                    ┌─────────────┐
                    │   PENDING   │ ← 초기 상태
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  VALIDATED  │ ← 검증 완료
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  UPLOADING  │ ← 이미지 업로드 중
                    └──────┬──────┘
                           │
                    ┌──────▼───────┐
                    │ REGISTERING  │ ← 상품 등록 중
                    └──────┬───┬───┘
                           │   │
                  성공 ─────┘   └───── 실패
                           │           │
                    ┌──────▼──────┐   │
                    │  COMPLETED  │   │
                    └─────────────┘   │
                                      │
            ┌─────────────────────────┴────────────────┐
            │                                          │
      ┌─────▼─────┐                          ┌────────▼────────┐
      │ RETRYING  │ ← 재시도 가능            │ MANUAL_REVIEW  │
      └─────┬─────┘                          └────────┬────────┘
            │                                          │
            └──────────► (3회 실패) ──────────────────┘
                                                       │
                                              사람 수정 후 재등록
```

---

## 모듈 설계

### 디렉토리 구조

```
StoreBridge/
├── README.md
├── ARCHITECTURE.md              # 본 문서
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── pyproject.toml
├── .env.example
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI 엔트리포인트
│   ├── config.py                # 설정 관리 (Pydantic Settings)
│   │
│   ├── api/                     # REST API 엔드포인트
│   │   ├── __init__.py
│   │   ├── jobs.py              # 잡 생성/조회/취소
│   │   ├── products.py          # 상품 조회/매핑
│   │   ├── review.py            # 수동 검토 큐
│   │   └── health.py            # 헬스체크
│   │
│   ├── connectors/              # 외부 API 클라이언트
│   │   ├── __init__.py
│   │   ├── domeggook.py         # 도매꾹 API
│   │   ├── naver.py             # 네이버 커머스 API
│   │   └── rate_limiters.py    # Rate Limiter
│   │
│   ├── workers/                 # Celery 워커
│   │   ├── __init__.py
│   │   ├── extract.py           # 도매꾹 데이터 수집
│   │   ├── transform.py         # 정규화
│   │   ├── load.py              # 네이버 등록
│   │   └── sync.py              # 가격/재고 동기화
│   │
│   ├── services/                # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── validation.py        # 검증 서비스
│   │   ├── mapping.py           # 카테고리/속성 매핑
│   │   ├── image_pipeline.py   # 이미지 처리
│   │   └── deduplication.py    # 중복 제거
│   │
│   ├── validators/              # 검증 로직
│   │   ├── __init__.py
│   │   ├── category.py          # 카테고리 검증
│   │   ├── image.py             # 이미지 규격 검증
│   │   └── forbidden_words.py  # 금지어 필터
│   │
│   ├── transformers/            # 데이터 변환
│   │   ├── __init__.py
│   │   ├── html_sanitizer.py   # HTML 클린업
│   │   ├── option_mapper.py    # 옵션 변환
│   │   └── price_calculator.py # 가격 계산
│   │
│   ├── models/                  # 데이터 모델
│   │   ├── __init__.py
│   │   ├── database.py          # SQLAlchemy Base
│   │   ├── product.py           # 상품 모델
│   │   ├── mapping.py           # 매핑 모델
│   │   ├── job.py               # 잡 모델
│   │   └── schemas.py           # Pydantic 스키마
│   │
│   ├── workflows/               # 워크플로우
│   │   ├── __init__.py
│   │   ├── state_machine.py    # 상태 기계
│   │   └── retry_handler.py    # 재시도 로직
│   │
│   └── utils/                   # 유틸리티
│       ├── __init__.py
│       ├── cache.py             # Redis 캐시
│       ├── encoding.py          # EUC-KR 처리
│       └── logger.py            # 로깅 설정
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest 설정
│   ├── test_connectors/
│   ├── test_workers/
│   └── fixtures/                # VCR.py 녹화 파일
│
├── migrations/                  # Alembic 마이그레이션
│   └── versions/
│
├── scripts/                     # 유틸리티 스크립트
│   ├── init_db.py
│   ├── seed_mappings.py         # 카테고리 매핑 시드
│   └── test_api.py              # API 테스트 스크립트
│
├── data/                        # 정적 데이터
│   ├── category_mappings.csv    # 카테고리 매핑 테이블
│   ├── forbidden_words.txt      # 금지어 목록
│   └── attribute_rules.yaml     # 속성 자동 채우기 룰
│
└── monitoring/                  # 모니터링 설정
    ├── prometheus.yml
    ├── grafana/
    │   └── dashboards/
    └── alerting_rules.yml
```

---

## 핵심 컴포넌트

### 1. Rate Limiter (Redis Token Bucket)

```python
# app/connectors/rate_limiters.py

import time
import asyncio
from typing import Optional
import aioredis

class TokenBucketRateLimiter:
    """
    네이버 커머스 API Rate Limit 준수
    - TPS: 2
    - Burst Max: 다음 1초 선빌림 (연속 불가)
    """

    def __init__(
        self,
        redis_url: str,
        max_tps: int = 2,
        burst_enabled: bool = True
    ):
        self.redis = aioredis.from_url(redis_url)
        self.max_tps = max_tps
        self.burst_enabled = burst_enabled

    async def acquire(self, timeout: Optional[float] = None) -> bool:
        """
        토큰 획득 시도

        Returns:
            True: 토큰 획득 성공
            False: timeout 내 획득 실패

        Raises:
            RateLimitExceeded: timeout 없이 즉시 실패
        """
        start_time = time.time()

        while True:
            now = time.time()
            current_second = int(now)
            key = f'naver:ratelimit:{current_second}'

            # 현재 초의 사용량 확인
            current_count = await self.redis.get(key)
            current_count = int(current_count) if current_count else 0

            if current_count < self.max_tps:
                # 토큰 사용
                await self.redis.incr(key)
                await self.redis.expire(key, 2)  # 2초 TTL
                return True

            # Burst Max 시도
            if self.burst_enabled:
                next_key = f'naver:ratelimit:{current_second + 1}'
                next_count = await self.redis.get(next_key)
                next_count = int(next_count) if next_count else 0

                if next_count == 0:  # 다음 초가 아직 사용 안됨
                    await self.redis.incr(next_key)
                    await self.redis.expire(next_key, 2)
                    await self.redis.setex(
                        f'naver:burst_used:{current_second}',
                        2,
                        '1'
                    )
                    return True

            # 대기
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    return False

            # 다음 초까지 대기
            wait_time = 1 - (now - current_second)
            await asyncio.sleep(max(wait_time, 0.1))
```

### 2. 도매꾹 API 클라이언트

```python
# app/connectors/domeggook.py

import httpx
from typing import List, Optional, Dict, Any
from urllib.parse import urlencode
from app.utils.encoding import encode_euckr, decode_euckr
from app.utils.cache import cache

class DomeggookClient:
    """도매꾹 OpenAPI 클라이언트"""

    BASE_URL = 'https://domeggook.com/ssl/api/'

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
        self.rate_limiter = TokenBucketRateLimiter(
            redis_url='redis://localhost',
            max_tps=3,  # 180/분 = 3/초
        )

    async def _request(
        self,
        mode: str,
        version: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """API 요청"""
        await self.rate_limiter.acquire()

        request_params = {
            'ver': version,
            'mode': mode,
            'aid': self.api_key,
            'market': 'dome',
            'om': 'json',
        }

        if params:
            # EUC-KR 인코딩
            for key, value in params.items():
                if isinstance(value, str):
                    request_params[key] = encode_euckr(value)
                else:
                    request_params[key] = value

        response = await self.client.get(self.BASE_URL, params=request_params)
        response.raise_for_status()

        return response.json()

    @cache(ttl=3600)  # 1시간 캐시
    async def get_item_list(
        self,
        keyword: Optional[str] = None,
        category_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """상품 목록 조회"""
        params = {
            'page': page,
            'page_size': page_size,
        }

        if keyword:
            params['keyword'] = keyword
        if category_id:
            params['category_id'] = category_id

        result = await self._request('getItemList', '4.1', params)
        return result.get('data', {}).get('items', [])

    @cache(ttl=21600)  # 6시간 캐시
    async def get_item_view(
        self,
        item_id: str,
        version: str = '4.5'
    ) -> Dict[str, Any]:
        """상품 상세 조회"""
        params = {'item_id': item_id}
        result = await self._request('getItemView', version, params)
        return result.get('data', {})

    @cache(ttl=86400)  # 1일 캐시
    async def get_category_list(self) -> List[Dict[str, Any]]:
        """카테고리 목록 조회"""
        result = await self._request('getCategoryList', '1.0')
        return result.get('data', {}).get('categories', [])
```

### 3. 네이버 API 클라이언트

```python
# app/connectors/naver.py

import httpx
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

class NaverCommerceClient:
    """네이버 커머스 API 클라이언트"""

    BASE_URL = 'https://api.commerce.naver.com'

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redis_url: str
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.client = httpx.AsyncClient(timeout=30.0)
        self.rate_limiter = TokenBucketRateLimiter(
            redis_url=redis_url,
            max_tps=2,
        )
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None

    async def _get_access_token(self) -> str:
        """OAuth 2.0 토큰 발급"""
        if (
            self.access_token
            and self.token_expires_at
            and datetime.now() < self.token_expires_at
        ):
            return self.access_token

        response = await self.client.post(
            f'{self.BASE_URL}/oauth2/token',
            data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials'
            }
        )
        response.raise_for_status()

        data = response.json()
        self.access_token = data['access_token']
        expires_in = data.get('expires_in', 3600)
        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)

        return self.access_token

    async def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """API 요청"""
        await self.rate_limiter.acquire(timeout=60.0)

        token = await self._get_access_token()
        headers = {'Authorization': f'Bearer {token}'}

        response = await self.client.request(
            method,
            f'{self.BASE_URL}{endpoint}',
            headers=headers,
            json=json,
            params=params
        )

        if response.status_code == 429:
            raise RateLimitExceeded('Naver API rate limit exceeded')

        response.raise_for_status()
        return response.json()

    @cache(ttl=86400 * 7)  # 1주일 캐시
    async def get_category_attributes(
        self,
        category_id: str
    ) -> Dict[str, Any]:
        """카테고리 필수 속성 조회"""
        return await self._request(
            'GET',
            f'/v2/categories/{category_id}/attributes'
        )

    async def create_product(
        self,
        product_data: Dict[str, Any]
    ) -> str:
        """상품 등록"""
        result = await self._request('POST', '/v2/products', json=product_data)
        return result['productId']

    async def upload_image(
        self,
        image_data: bytes,
        filename: str
    ) -> str:
        """이미지 업로드"""
        await self.rate_limiter.acquire(timeout=60.0)

        token = await self._get_access_token()
        files = {'image': (filename, image_data, 'image/jpeg')}

        response = await self.client.post(
            f'{self.BASE_URL}/v2/images',
            headers={'Authorization': f'Bearer {token}'},
            files=files
        )
        response.raise_for_status()

        return response.json()['imageUrl']
```

### 4. 상태 기계 (State Machine)

```python
# app/workflows/state_machine.py

from enum import Enum
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.product import ProductRegistration

class RegistrationState(str, Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    UPLOADING = "uploading"
    REGISTERING = "registering"
    COMPLETED = "completed"
    RETRYING = "retrying"
    MANUAL_REVIEW = "manual_review"
    FAILED = "failed"

class StateTransition:
    """상태 전이 규칙"""

    ALLOWED_TRANSITIONS = {
        RegistrationState.PENDING: [
            RegistrationState.VALIDATED,
            RegistrationState.MANUAL_REVIEW,
            RegistrationState.FAILED
        ],
        RegistrationState.VALIDATED: [
            RegistrationState.UPLOADING,
            RegistrationState.MANUAL_REVIEW
        ],
        RegistrationState.UPLOADING: [
            RegistrationState.REGISTERING,
            RegistrationState.RETRYING,
            RegistrationState.MANUAL_REVIEW
        ],
        RegistrationState.REGISTERING: [
            RegistrationState.COMPLETED,
            RegistrationState.RETRYING,
            RegistrationState.MANUAL_REVIEW
        ],
        RegistrationState.RETRYING: [
            RegistrationState.UPLOADING,
            RegistrationState.REGISTERING,
            RegistrationState.MANUAL_REVIEW,
            RegistrationState.FAILED
        ],
        RegistrationState.MANUAL_REVIEW: [
            RegistrationState.PENDING,  # 수정 후 재시작
            RegistrationState.FAILED
        ],
        RegistrationState.COMPLETED: [],
        RegistrationState.FAILED: []
    }

    @classmethod
    def can_transition(
        cls,
        from_state: RegistrationState,
        to_state: RegistrationState
    ) -> bool:
        """상태 전이 가능 여부"""
        return to_state in cls.ALLOWED_TRANSITIONS.get(from_state, [])

    @classmethod
    def transition(
        cls,
        db: Session,
        registration: ProductRegistration,
        to_state: RegistrationState,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProductRegistration:
        """상태 전이 수행"""
        if not cls.can_transition(registration.state, to_state):
            raise ValueError(
                f"Invalid transition: {registration.state} -> {to_state}"
            )

        registration.state = to_state

        if error_message:
            registration.error_message = error_message

        if metadata:
            registration.metadata = {
                **(registration.metadata or {}),
                **metadata
            }

        if to_state == RegistrationState.RETRYING:
            registration.retry_count += 1

        db.commit()
        db.refresh(registration)

        return registration
```

---

## 성능 & 제약사항

### Rate Limit 분석

| API | 제한 | 실제 가용량 | 병목 여부 |
|-----|------|-------------|-----------|
| **도매꾹** | 180/분, 15K/일 | ~7,500 상품/일 | ⚠️ 병목 |
| **네이버** | 2 TPS | ~10,000 상품/일 | ⚠️ 심각한 병목 |

**결론: 도매꾹이 실제 병목**
- 도매꾹: 상품당 2 API (목록+상세) = 7,500개/일
- 네이버: 상품당 5 API (속성+이미지+등록) = 10,000개/일
- **실제 처리량: ~5,000 상품/일** (안전 마진 포함)

### 대응 전략

#### 1. 캐싱
```yaml
도매꾹:
  - 상품 목록: 1시간 TTL
  - 상품 상세: 6시간 TTL
  - 카테고리: 1일 TTL

네이버:
  - 카테고리 속성: 1주일 TTL
  - OAuth 토큰: 자동 갱신
```

#### 2. 선별적 수집
```python
# 우선순위 기반 수집
priorities = {
    'new_arrivals': 10,      # 신상품 우선
    'high_margin': 8,        # 고마진 상품
    'low_competition': 6,    # 경쟁 낮은 상품
    'seasonal': 4,           # 시즌 상품
    'regular': 1             # 일반 상품
}
```

#### 3. 배치 최적화
```python
# 밤 시간대 대량 처리
schedule = {
    '00:00-06:00': 'batch_import',      # 대량 등록
    '06:00-09:00': 'sync_inventory',    # 재고 동기화
    '09:00-18:00': 'realtime_orders',   # 실시간 주문
    '18:00-24:00': 'price_updates'      # 가격 업데이트
}
```

### 성능 목표

| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| **일일 등록량** | 5,000 상품 | Grafana 카운터 |
| **등록 성공률** | > 85% | (성공 / 전체) × 100 |
| **평균 처리 시간** | < 30초/상품 | Prometheus histogram |
| **반려율** | < 15% | (반려 / 등록 시도) × 100 |
| **API 오류율** | < 1% | (5xx / 전체) × 100 |
| **큐 대기 시간** | < 5분 | Redis queue depth |

---

## 에러 핸들링

### 에러 분류 & 처리 전략

```python
# app/workflows/retry_handler.py

from typing import Optional, Callable
import asyncio

class ErrorHandler:
    """에러 분류 및 재시도 전략"""

    # 재시도 가능한 에러
    RETRYABLE_ERRORS = {
        'RATE_LIMIT_EXCEEDED': {
            'max_retries': 5,
            'backoff': 'exponential',  # 5분 → 15분 → 45분
            'base_delay': 300
        },
        'NETWORK_ERROR': {
            'max_retries': 3,
            'backoff': 'linear',
            'base_delay': 60
        },
        'IMAGE_UPLOAD_FAILED': {
            'max_retries': 3,
            'backoff': 'linear',
            'base_delay': 30
        }
    }

    # 수동 검토 필요
    MANUAL_REVIEW_ERRORS = {
        'CATEGORY_MISMATCH',
        'ATTRIBUTE_MISSING',
        'ATTRIBUTE_INVALID',
        'FORBIDDEN_WORD_DETECTED',
        'DUPLICATE_PRODUCT'
    }

    # 자동 수정 가능
    AUTO_FIX_ERRORS = {
        'IMAGE_INVALID_SIZE': 'resize_image',
        'HTML_FORBIDDEN_TAG': 'sanitize_html',
        'PRICE_OUT_OF_RANGE': 'adjust_price'
    }

    @classmethod
    async def handle_error(
        cls,
        error_code: str,
        registration: ProductRegistration,
        db: Session
    ) -> RegistrationState:
        """에러 처리 라우팅"""

        # 1. 자동 수정 시도
        if error_code in cls.AUTO_FIX_ERRORS:
            fix_func = cls.AUTO_FIX_ERRORS[error_code]
            await cls._auto_fix(registration, fix_func)
            return RegistrationState.RETRYING

        # 2. 재시도 판단
        if error_code in cls.RETRYABLE_ERRORS:
            config = cls.RETRYABLE_ERRORS[error_code]
            if registration.retry_count < config['max_retries']:
                delay = cls._calculate_backoff(
                    registration.retry_count,
                    config['backoff'],
                    config['base_delay']
                )
                await asyncio.sleep(delay)
                return RegistrationState.RETRYING

        # 3. 수동 검토 큐
        if error_code in cls.MANUAL_REVIEW_ERRORS:
            return RegistrationState.MANUAL_REVIEW

        # 4. 치명적 에러
        return RegistrationState.FAILED

    @staticmethod
    def _calculate_backoff(
        retry_count: int,
        backoff_type: str,
        base_delay: int
    ) -> int:
        """백오프 시간 계산"""
        if backoff_type == 'exponential':
            return base_delay * (3 ** retry_count)
        elif backoff_type == 'linear':
            return base_delay * (retry_count + 1)
        else:
            return base_delay
```

### 에러 코드 정의

```yaml
# 네이버 API 에러
NAVER_RATE_LIMIT: 429 Too Many Requests
NAVER_UNAUTHORIZED: 401 Invalid Token
NAVER_CATEGORY_INVALID: 400 Invalid Category
NAVER_ATTRIBUTE_MISSING: 400 Required Attribute Missing
NAVER_FORBIDDEN_WORD: 400 Forbidden Word Detected
NAVER_IMAGE_INVALID: 400 Image Validation Failed
NAVER_DUPLICATE: 409 Duplicate Product

# 도매꾹 API 에러
DOMEGGOOK_RATE_LIMIT: 429 Too Many Requests
DOMEGGOOK_INVALID_KEY: 401 Invalid API Key
DOMEGGOOK_NOT_FOUND: 404 Product Not Found

# 내부 에러
VALIDATION_FAILED: Validation Error
IMAGE_DOWNLOAD_FAILED: Image Download Error
TRANSFORM_FAILED: Data Transform Error
DB_ERROR: Database Error
```

---

## 배포 전략

### Docker Compose 구성

```yaml
# docker-compose.yml

version: '3.9'

services:
  # Web API
  web:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/storebridge
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./app:/app

  # Celery Worker (Normal Queue)
  worker-normal:
    build: .
    command: celery -A app.workers worker -Q normal -c 4
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/storebridge
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  # Celery Worker (Batch Queue)
  worker-batch:
    build: .
    command: celery -A app.workers worker -Q batch -c 2
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/storebridge
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  # Celery Beat (Scheduler)
  beat:
    build: .
    command: celery -A app.workers beat
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/storebridge
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=storebridge
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # MinIO (S3 호환)
  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=admin
      - MINIO_ROOT_PASSWORD=password
    volumes:
      - minio_data:/data

  # Prometheus
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  # Grafana
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
    depends_on:
      - prometheus

volumes:
  postgres_data:
  redis_data:
  minio_data:
  prometheus_data:
  grafana_data:
```

### 환경 변수

```bash
# .env.example

# 도매꾹 API
DOMEGGOOK_API_KEY=your_api_key_here

# 네이버 커머스 API
NAVER_CLIENT_ID=your_client_id
NAVER_CLIENT_SECRET=your_client_secret

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/storebridge

# Redis
REDIS_URL=redis://localhost:6379

# S3 / MinIO
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=admin
S3_SECRET_KEY=password
S3_BUCKET=storebridge-images

# Sentry
SENTRY_DSN=https://...

# 로그 레벨
LOG_LEVEL=INFO

# Rate Limit 설정
DOMEGGOOK_MAX_TPS=3
NAVER_MAX_TPS=2

# 재시도 설정
MAX_RETRIES=3
RETRY_BACKOFF_BASE=300
```

---

## 개발 로드맵

### Phase 0: API 스펙 확정 (3일)
- [ ] 도매꾹 API 키 발급
- [ ] 네이버 커머스 API 앱 등록
- [ ] Postman으로 각 API 테스트
  - [ ] 도매꾹: getItemList, getItemView (ver 4.0~4.5 비교)
  - [ ] 네이버: 카테고리 조회, 속성 조회, 상품 등록
- [ ] 응답 JSON 구조 문서화
- [ ] 누락 필드 확인 시 techsupport@ggook.com 문의

### Phase 1: 1개 상품 E2E (5일)
- [ ] 프로젝트 셋업
  - [ ] Git 저장소 초기화
  - [ ] Docker Compose 작성
  - [ ] 디렉토리 구조 생성
- [ ] 도매꾹 커넥터 구현
  - [ ] API 클라이언트 기본 구조
  - [ ] EUC-KR 인코딩 처리
  - [ ] Rate Limiter (Redis Token Bucket)
  - [ ] 단위 테스트 (VCR.py)
- [ ] 네이버 커넥터 구현
  - [ ] OAuth 2.0 인증
  - [ ] Rate Limiter (2 TPS)
  - [ ] 상품 등록 API
- [ ] 수동으로 1개 상품 등록 성공
  - [ ] 도매꾹에서 상품 1개 조회
  - [ ] JSON 수동 변환
  - [ ] 네이버에 등록
  - [ ] 에러 케이스 문서화

### Phase 2: 기본 파이프라인 (5일)
- [ ] 데이터베이스 모델
  - [ ] Product, Mapping, Job 테이블
  - [ ] Alembic 마이그레이션
- [ ] Transform 레이어
  - [ ] HTML Sanitizer
  - [ ] 이미지 다운로드/리사이즈
  - [ ] 옵션 매핑 (기본)
- [ ] Celery 워커
  - [ ] Extract 태스크
  - [ ] Transform 태스크
  - [ ] Load 태스크
- [ ] FastAPI 엔드포인트
  - [ ] POST /jobs (잡 생성)
  - [ ] GET /jobs/{id} (상태 조회)
- [ ] 10개 상품 배치 테스트

### Phase 3: 검증 & 에러 핸들링 (7일)
- [ ] Validator 구현
  - [ ] 카테고리 검증
  - [ ] 이미지 규격 검증
  - [ ] 금지어 필터
- [ ] 카테고리 매핑 시스템
  - [ ] CSV 기반 매핑 테이블
  - [ ] 네이버 카테고리 속성 조회/캐싱
  - [ ] 속성 자동 채우기 룰
- [ ] 상태 기계 구현
  - [ ] State Transition 로직
  - [ ] 재시도 핸들러
  - [ ] 에러 분류
- [ ] 수동 검토 큐
  - [ ] Manual Review API
  - [ ] 반려 사유 분석

### Phase 4: 이미지 파이프라인 (5일)
- [ ] S3 / MinIO 연동
- [ ] 이미지 처리
  - [ ] 병렬 다운로드
  - [ ] WebP 변환
  - [ ] 워터마크 검출 (간단한 룰)
- [ ] 중복 이미지 해시 체크
- [ ] 네이버 이미지 업로드 API

### Phase 5: 관리 콘솔 & 모니터링 (7일)
- [ ] Admin UI (간단한 대시보드)
  - [ ] 잡 목록/상세
  - [ ] 진행률 표시
  - [ ] 에러 로그 뷰어
  - [ ] 수동 검토 큐
- [ ] Grafana 대시보드
  - [ ] TPS 모니터링
  - [ ] 반려율 차트
  - [ ] 큐 깊이 게이지
  - [ ] 성공률 그래프
- [ ] Prometheus 메트릭
  - [ ] API 호출 카운터
  - [ ] 처리 시간 히스토그램
  - [ ] 에러율
- [ ] 알림 규칙
  - [ ] Rate Limit 90% 도달
  - [ ] 반려율 30% 초과
  - [ ] 큐 대기 1시간 초과

### Phase 6: 파일럿 & 튜닝 (10일)
- [ ] 100개 상품 스트레스 테스트
  - [ ] 메모리/CPU 프로파일링
  - [ ] DB 쿼리 최적화
  - [ ] Redis 캐시 히트율 측정
- [ ] 실전 500개 등록
  - [ ] 반려 사유 수집
  - [ ] 매핑 룰 보강
  - [ ] 금지어 목록 업데이트
- [ ] 성능 최적화
  - [ ] 병목 구간 식별
  - [ ] 배치 크기 튜닝
  - [ ] 동시성 조정
- [ ] 문서화
  - [ ] API 문서 (Swagger)
  - [ ] 운영 가이드
  - [ ] 트러블슈팅 가이드

### Phase 7: 동기화 & 확장 (선택)
- [ ] 가격/재고 동기화 스케줄러
- [ ] 주문 연동 (양방향)
- [ ] 다중 공급처 지원
- [ ] ML 기반 카테고리 자동 분류

---

## 부록

### A. 참고 자료

#### 도매꾹 OpenAPI
- 공식 사이트: https://openapi.domeggook.com/main/
- 시작 가이드: https://openapi.domeggook.com/main/guide/start
- API 목록: https://openapi.domeggook.com/main/reference/lst_open
- 기술 지원: techsupport@ggook.com

#### 네이버 커머스 API
- API 센터: https://apicenter.commerce.naver.com
- GitHub: https://github.com/commerce-api-naver/commerce-api
- Discussions: https://github.com/commerce-api-naver/commerce-api/discussions

### B. 용어집

| 용어 | 설명 |
|------|------|
| **ETL** | Extract, Transform, Load - 데이터 추출/변환/적재 파이프라인 |
| **TPS** | Transactions Per Second - 초당 트랜잭션 수 |
| **Rate Limit** | API 호출 빈도 제한 |
| **Token Bucket** | Rate Limiting 알고리즘의 일종 |
| **Burst Max** | 순간적으로 허용되는 최대 요청 수 |
| **리프 카테고리** | 최하위 카테고리 (더 이상 하위 카테고리가 없음) |
| **sellerProductCode** | 판매자 상품 코드 (SKU) |
| **반려** | 상품 등록 거부 |

### C. 체크리스트

#### 개발 전 확인
- [ ] 도매꾹 API 키 발급 완료
- [ ] 네이버 커머스 API 앱 등록 완료
- [ ] 네이버 판매자센터 "API 사용" ON 설정
- [ ] IP 화이트리스트 등록 (필요시)
- [ ] PostgreSQL/Redis 설치
- [ ] Docker/Docker Compose 설치

#### 배포 전 확인
- [ ] 환경 변수 설정 (.env)
- [ ] 데이터베이스 마이그레이션
- [ ] 카테고리 매핑 테이블 시드
- [ ] 금지어 목록 업데이트
- [ ] Sentry DSN 설정
- [ ] Grafana 대시보드 구성
- [ ] 알림 규칙 설정
- [ ] 백업 전략 수립

#### 운영 체크리스트
- [ ] 일일 처리량 모니터링
- [ ] 반려율 추이 확인
- [ ] API 쿼터 사용량 확인
- [ ] 에러 로그 주간 리뷰
- [ ] 디스크 용량 확인 (이미지 스토리지)
- [ ] 데이터베이스 백업 확인

---

**작성자**: StoreBridge Team
**최종 수정**: 2025-10-16
**버전**: 1.0
