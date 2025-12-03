# API 명세서 (API Specification)

> StoreBridge REST API 상세 문서

**작성일**: 2025-10-16
**Base URL**: `https://api.storebridge.com/v1`
**Protocol**: HTTPS
**Auth**: Bearer Token (JWT)
**버전**: v1.0

---

## 목차

1. [인증 (Authentication)](#인증-authentication)
2. [공통 사항](#공통-사항)
3. [작업 관리 (Jobs)](#작업-관리-jobs)
4. [상품 관리 (Products)](#상품-관리-products)
5. [수동 검토 (Manual Review)](#수동-검토-manual-review)
6. [카테고리 매핑 (Category Mappings)](#카테고리-매핑-category-mappings)
7. [설정 (Settings)](#설정-settings)
8. [에러 코드](#에러-코드)

---

## 인증 (Authentication)

### POST /auth/login

사용자 로그인 (JWT 토큰 발급)

**Request:**
```http
POST /v1/auth/login
Content-Type: application/json

{
  "username": "admin@example.com",
  "password": "SecurePassword123!"
}
```

**Response: 200 OK**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user-uuid",
    "username": "admin@example.com",
    "role": "admin"
  }
}
```

**사용 예시:**
```bash
# 이후 모든 요청에 Authorization 헤더 포함
curl -H "Authorization: Bearer {access_token}" \
  https://api.storebridge.com/v1/jobs
```

---

## 공통 사항

### 요청 헤더

```http
Authorization: Bearer {access_token}
Content-Type: application/json
Accept: application/json
X-Request-ID: {optional-uuid}  # 요청 추적용
```

### 응답 형식

#### 성공 응답
```json
{
  "success": true,
  "data": { ... },
  "metadata": {
    "timestamp": "2025-10-16T10:30:00Z",
    "request_id": "req-uuid"
  }
}
```

#### 에러 응답
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "keyword",
        "message": "keyword is required"
      }
    ]
  },
  "metadata": {
    "timestamp": "2025-10-16T10:30:00Z",
    "request_id": "req-uuid"
  }
}
```

### 페이지네이션

```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## 작업 관리 (Jobs)

### POST /jobs

새로운 작업 생성 (대량 상품 등록)

**Request:**
```http
POST /v1/jobs
Content-Type: application/json
Authorization: Bearer {token}

{
  "type": "IMPORT",
  "config": {
    "source": "domeggook",
    "filter": {
      "keyword": "여성의류",
      "category": "티셔츠",
      "price_min": 10000,
      "price_max": 50000
    },
    "limit": 100,
    "auto_register": true
  }
}
```

**Request Body Schema:**
```typescript
{
  type: "IMPORT" | "SYNC_PRICE" | "SYNC_INVENTORY",
  config: {
    source: "domeggook",
    filter?: {
      keyword?: string,
      category?: string,
      supplier?: string,
      price_min?: number,
      price_max?: number,
      new_arrivals_only?: boolean
    },
    limit?: number,           // 최대 상품 수 (기본: 100)
    auto_register?: boolean,  // 자동 등록 여부 (기본: false)
    priority?: "normal" | "high" | "urgent"
  }
}
```

**Response: 201 Created**
```json
{
  "success": true,
  "data": {
    "job_id": "job-uuid-12345",
    "type": "IMPORT",
    "status": "PENDING",
    "total_count": 0,
    "success_count": 0,
    "failed_count": 0,
    "progress_percent": 0,
    "created_at": "2025-10-16T10:30:00Z",
    "estimated_duration_minutes": 15
  }
}
```

**Errors:**
- `400 Bad Request`: 잘못된 요청 파라미터
- `401 Unauthorized`: 인증 토큰 없음/만료
- `429 Too Many Requests`: Rate Limit 초과

---

### GET /jobs

작업 목록 조회

**Request:**
```http
GET /v1/jobs?status=RUNNING&type=IMPORT&page=1&page_size=20
Authorization: Bearer {token}
```

**Query Parameters:**
- `status` (optional): PENDING | RUNNING | COMPLETED | FAILED | CANCELLED
- `type` (optional): IMPORT | SYNC_PRICE | SYNC_INVENTORY
- `created_by` (optional): 사용자 ID
- `page` (default: 1)
- `page_size` (default: 20, max: 100)
- `sort` (default: -created_at): 정렬 (created_at, -created_at, status)

**Response: 200 OK**
```json
{
  "success": true,
  "data": [
    {
      "job_id": "job-uuid-1",
      "type": "IMPORT",
      "status": "RUNNING",
      "total_count": 100,
      "success_count": 45,
      "failed_count": 3,
      "skipped_count": 0,
      "progress_percent": 48.0,
      "created_at": "2025-10-16T10:00:00Z",
      "started_at": "2025-10-16T10:01:00Z",
      "duration_seconds": 600,
      "estimated_remaining_seconds": 650
    },
    {
      "job_id": "job-uuid-2",
      "type": "SYNC_PRICE",
      "status": "COMPLETED",
      "total_count": 500,
      "success_count": 495,
      "failed_count": 5,
      "progress_percent": 100.0,
      "created_at": "2025-10-16T09:00:00Z",
      "completed_at": "2025-10-16T09:45:00Z",
      "duration_seconds": 2700
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 45,
    "total_pages": 3,
    "has_next": true
  }
}
```

---

### GET /jobs/{job_id}

특정 작업 상세 조회

**Request:**
```http
GET /v1/jobs/job-uuid-12345
Authorization: Bearer {token}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "job_id": "job-uuid-12345",
    "type": "IMPORT",
    "status": "RUNNING",
    "config": {
      "source": "domeggook",
      "filter": {
        "keyword": "여성의류",
        "category": "티셔츠"
      },
      "limit": 100
    },
    "statistics": {
      "total_count": 100,
      "success_count": 45,
      "failed_count": 3,
      "skipped_count": 0,
      "progress_percent": 48.0
    },
    "error_summary": {
      "CATEGORY_MISMATCH": 2,
      "FORBIDDEN_WORD": 1
    },
    "timeline": {
      "created_at": "2025-10-16T10:00:00Z",
      "started_at": "2025-10-16T10:01:00Z",
      "duration_seconds": 600,
      "estimated_remaining_seconds": 650
    },
    "items_sample": [
      {
        "product_name": "여성 반팔 티셔츠",
        "status": "success",
        "naver_product_id": "NP123456"
      },
      {
        "product_name": "여성 긴팔 티셔츠",
        "status": "failed",
        "error_code": "CATEGORY_MISMATCH"
      }
    ]
  }
}
```

**Errors:**
- `404 Not Found`: 작업이 존재하지 않음

---

### DELETE /jobs/{job_id}

작업 취소

**Request:**
```http
DELETE /v1/jobs/job-uuid-12345
Authorization: Bearer {token}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "job_id": "job-uuid-12345",
    "status": "CANCELLED",
    "cancelled_at": "2025-10-16T10:35:00Z",
    "items_processed": 48
  }
}
```

**Errors:**
- `400 Bad Request`: 이미 완료/실패한 작업은 취소 불가
- `404 Not Found`: 작업이 존재하지 않음

---

### GET /jobs/{job_id}/items

작업에 포함된 개별 상품 목록

**Request:**
```http
GET /v1/jobs/job-uuid-12345/items?status=failed&page=1
Authorization: Bearer {token}
```

**Query Parameters:**
- `status` (optional): pending | processing | success | failed | skipped
- `error_code` (optional): 특정 에러 코드 필터
- `page`, `page_size`

**Response: 200 OK**
```json
{
  "success": true,
  "data": [
    {
      "item_id": "item-uuid-1",
      "product_id": "product-uuid-1",
      "product_name": "여성 반팔 티셔츠",
      "domeggook_item_id": "DG123456",
      "status": "failed",
      "error_code": "CATEGORY_MISMATCH",
      "error_message": "카테고리 매핑을 찾을 수 없습니다: 여성의류 > 티셔츠",
      "created_at": "2025-10-16T10:05:00Z",
      "processed_at": "2025-10-16T10:07:00Z"
    }
  ],
  "pagination": { ... }
}
```

---

## 상품 관리 (Products)

### POST /products/validate

상품 사전 검증 (등록 전 확인)

**Request:**
```http
POST /v1/products/validate
Content-Type: application/json
Authorization: Bearer {token}

{
  "domeggook_item_id": "DG123456"
}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "is_valid": false,
    "product": {
      "name": "여성 반팔 티셔츠",
      "price": 25000,
      "category": "여성의류 > 티셔츠",
      "images_count": 5,
      "options_count": 4
    },
    "validation_results": [
      {
        "rule": "category_mapping",
        "passed": false,
        "message": "카테고리 매핑을 찾을 수 없습니다",
        "suggestion": "카테고리 매핑 테이블에 추가 필요"
      },
      {
        "rule": "forbidden_words",
        "passed": true,
        "message": "금지어 없음"
      },
      {
        "rule": "image_requirements",
        "passed": true,
        "message": "모든 이미지가 규격 충족"
      },
      {
        "rule": "required_attributes",
        "passed": false,
        "message": "필수 속성 누락: 제조일자",
        "missing_attributes": ["제조일자"]
      }
    ],
    "can_auto_fix": false,
    "estimated_registration_time_seconds": 25
  }
}
```

---

### GET /products

상품 목록 조회

**Request:**
```http
GET /v1/products?category=여성의류&page=1&page_size=20
Authorization: Bearer {token}
```

**Query Parameters:**
- `category` (optional)
- `supplier` (optional)
- `keyword` (optional): 상품명 검색
- `is_available` (optional): true | false
- `has_registration` (optional): 등록 여부 (true | false)
- `registration_state` (optional): PENDING | COMPLETED | FAILED 등
- `page`, `page_size`
- `sort`: name | price | created_at | -created_at

**Response: 200 OK**
```json
{
  "success": true,
  "data": [
    {
      "product_id": "product-uuid-1",
      "domeggook_item_id": "DG123456",
      "name": "여성 반팔 티셔츠",
      "price": 25000,
      "original_price": 30000,
      "category": "여성의류 > 티셔츠",
      "supplier": "도매업체A",
      "images_count": 5,
      "stock_quantity": 100,
      "is_available": true,
      "registration": {
        "state": "COMPLETED",
        "naver_product_id": "NP123456",
        "registered_at": "2025-10-15T14:00:00Z"
      },
      "created_at": "2025-10-15T10:00:00Z",
      "updated_at": "2025-10-15T10:00:00Z"
    }
  ],
  "pagination": { ... }
}
```

---

### GET /products/{product_id}

상품 상세 조회

**Request:**
```http
GET /v1/products/product-uuid-123
Authorization: Bearer {token}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "product_id": "product-uuid-123",
    "domeggook_item_id": "DG123456",
    "name": "여성 반팔 티셔츠",
    "price": 25000,
    "original_price": 30000,
    "category": "여성의류 > 티셔츠",
    "supplier": "도매업체A",
    "description": "시원한 여름 반팔 티셔츠입니다...",
    "images": [
      "https://cdn.domeggook.com/image1.jpg",
      "https://cdn.domeggook.com/image2.jpg"
    ],
    "options": [
      {
        "name": "블랙-S",
        "price": 25000,
        "stock": 10
      },
      {
        "name": "블랙-M",
        "price": 25000,
        "stock": 15
      }
    ],
    "stock_quantity": 100,
    "is_available": true,
    "registration": {
      "state": "COMPLETED",
      "naver_product_id": "NP123456",
      "seller_product_code": "SKU-DG123456",
      "registered_at": "2025-10-15T14:00:00Z",
      "metadata": {
        "transformed_options": { ... },
        "s3_image_urls": [ ... ]
      }
    },
    "raw_data": { ... },  # 도매꾹 원본 데이터
    "created_at": "2025-10-15T10:00:00Z",
    "updated_at": "2025-10-16T09:00:00Z"
  }
}
```

---

### POST /products/{product_id}/retry

상품 등록 재시도

**Request:**
```http
POST /v1/products/product-uuid-123/retry
Authorization: Bearer {token}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "product_id": "product-uuid-123",
    "registration_id": "reg-uuid-456",
    "state": "PENDING",
    "retry_count": 1,
    "message": "재시도 큐에 추가되었습니다"
  }
}
```

---

## 수동 검토 (Manual Review)

### GET /manual-review

수동 검토 필요 상품 목록

**Request:**
```http
GET /v1/manual-review?error_code=CATEGORY_MISMATCH&page=1
Authorization: Bearer {token}
```

**Query Parameters:**
- `error_code` (optional): 특정 에러 코드 필터
- `category` (optional): 카테고리 필터
- `priority` (optional): high | normal
- `assigned_to` (optional): 담당자 필터
- `page`, `page_size`

**Response: 200 OK**
```json
{
  "success": true,
  "data": [
    {
      "review_id": "review-uuid-1",
      "product_id": "product-uuid-123",
      "product_name": "여성 반팔 티셔츠",
      "domeggook_item_id": "DG123456",
      "error_code": "CATEGORY_MISMATCH",
      "error_message": "카테고리 매핑을 찾을 수 없습니다",
      "suggestion": "카테고리 매핑 테이블에 추가 또는 수동 선택",
      "priority": "normal",
      "assigned_to": null,
      "created_at": "2025-10-16T10:00:00Z",
      "actions": [
        {
          "action": "add_category_mapping",
          "label": "카테고리 매핑 추가",
          "endpoint": "POST /category-mappings"
        },
        {
          "action": "manual_select",
          "label": "수동 선택",
          "endpoint": "PUT /manual-review/{review_id}"
        },
        {
          "action": "skip",
          "label": "건너뛰기",
          "endpoint": "DELETE /manual-review/{review_id}"
        }
      ]
    }
  ],
  "pagination": { ... },
  "summary": {
    "total": 45,
    "by_error_code": {
      "CATEGORY_MISMATCH": 20,
      "FORBIDDEN_WORD": 15,
      "ATTRIBUTE_MISSING": 10
    }
  }
}
```

---

### PUT /manual-review/{review_id}

수동 검토 처리 (수정 후 재등록)

**Request:**
```http
PUT /v1/manual-review/review-uuid-1
Content-Type: application/json
Authorization: Bearer {token}

{
  "action": "fix_and_retry",
  "fixes": {
    "category_mapping": {
      "domeggook_category": "여성의류 > 티셔츠",
      "naver_leaf_category_id": "50000123"
    },
    "attributes": {
      "제조일자": "2025-01-01"
    }
  },
  "note": "카테고리 매핑 추가 후 재시도"
}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "review_id": "review-uuid-1",
    "status": "resolved",
    "registration_id": "reg-uuid-789",
    "registration_state": "PENDING",
    "resolved_at": "2025-10-16T11:00:00Z",
    "resolved_by": "admin@example.com"
  }
}
```

---

### DELETE /manual-review/{review_id}

수동 검토 항목 건너뛰기

**Request:**
```http
DELETE /v1/manual-review/review-uuid-1?reason=duplicate
Authorization: Bearer {token}
```

**Query Parameters:**
- `reason` (optional): duplicate | unsupported | manual_decision

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "review_id": "review-uuid-1",
    "status": "skipped",
    "reason": "duplicate",
    "skipped_at": "2025-10-16T11:00:00Z"
  }
}
```

---

## 카테고리 매핑 (Category Mappings)

### GET /category-mappings

카테고리 매핑 목록 조회

**Request:**
```http
GET /v1/category-mappings?is_active=true&page=1
Authorization: Bearer {token}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": [
    {
      "mapping_id": 1,
      "domeggook_category": "여성의류 > 티셔츠",
      "naver_leaf_category_id": "50000123",
      "naver_category_name": "여성상의",
      "required_attributes": {
        "제조일자": {"type": "date", "required": true},
        "소재": {"type": "string", "required": true}
      },
      "default_attributes": {
        "소재": "면 100%",
        "세탁방법": "드라이클리닝"
      },
      "confidence": 1.0,
      "mapping_source": "manual",
      "is_active": true,
      "usage_count": 150,
      "success_count": 142,
      "success_rate": 94.67,
      "created_at": "2025-10-01T00:00:00Z"
    }
  ],
  "pagination": { ... }
}
```

---

### POST /category-mappings

새 카테고리 매핑 추가

**Request:**
```http
POST /v1/category-mappings
Content-Type: application/json
Authorization: Bearer {token}

{
  "domeggook_category": "여성의류 > 바지",
  "naver_leaf_category_id": "50000124",
  "naver_category_name": "여성하의",
  "required_attributes": {
    "제조일자": {"type": "date", "required": true},
    "소재": {"type": "string", "required": true}
  },
  "default_attributes": {
    "소재": "면 95%, 스판 5%"
  },
  "confidence": 1.0,
  "notes": "수동 추가"
}
```

**Response: 201 Created**
```json
{
  "success": true,
  "data": {
    "mapping_id": 42,
    "domeggook_category": "여성의류 > 바지",
    "naver_leaf_category_id": "50000124",
    "is_active": true,
    "created_at": "2025-10-16T11:30:00Z"
  }
}
```

---

## 설정 (Settings)

### GET /settings

시스템 설정 조회

**Request:**
```http
GET /v1/settings
Authorization: Bearer {token}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "rate_limits": {
      "domeggook_tps": 3,
      "naver_tps": 2,
      "domeggook_daily_limit": 15000
    },
    "job_defaults": {
      "max_retries": 3,
      "retry_backoff_base_seconds": 300,
      "default_priority": "normal"
    },
    "image_processing": {
      "max_images_per_product": 10,
      "min_width": 500,
      "min_height": 500,
      "max_size_mb": 12,
      "target_format": "webp"
    },
    "notification": {
      "slack_webhook_enabled": true,
      "email_alerts_enabled": true,
      "alert_on_rejection_rate_threshold": 30
    }
  }
}
```

---

### PUT /settings

시스템 설정 업데이트

**Request:**
```http
PUT /v1/settings
Content-Type: application/json
Authorization: Bearer {token}

{
  "job_defaults": {
    "max_retries": 5
  },
  "notification": {
    "alert_on_rejection_rate_threshold": 25
  }
}
```

**Response: 200 OK**
```json
{
  "success": true,
  "data": {
    "updated_fields": ["job_defaults.max_retries", "notification.alert_on_rejection_rate_threshold"],
    "updated_at": "2025-10-16T12:00:00Z"
  }
}
```

---

## 에러 코드

### HTTP 상태 코드

| 코드 | 설명 |
|------|------|
| 200 | OK - 요청 성공 |
| 201 | Created - 리소스 생성 성공 |
| 204 | No Content - 요청 성공 (응답 본문 없음) |
| 400 | Bad Request - 잘못된 요청 |
| 401 | Unauthorized - 인증 실패 |
| 403 | Forbidden - 권한 없음 |
| 404 | Not Found - 리소스 없음 |
| 409 | Conflict - 리소스 충돌 (중복 등) |
| 422 | Unprocessable Entity - 검증 실패 |
| 429 | Too Many Requests - Rate Limit 초과 |
| 500 | Internal Server Error - 서버 오류 |
| 503 | Service Unavailable - 서비스 일시 중단 |

### 애플리케이션 에러 코드

| 코드 | 설명 | HTTP 상태 |
|------|------|-----------|
| `VALIDATION_ERROR` | 요청 데이터 검증 실패 | 400 |
| `AUTHENTICATION_FAILED` | 인증 실패 | 401 |
| `AUTHORIZATION_FAILED` | 권한 없음 | 403 |
| `RESOURCE_NOT_FOUND` | 리소스 없음 | 404 |
| `DUPLICATE_RESOURCE` | 리소스 중복 | 409 |
| `RATE_LIMIT_EXCEEDED` | Rate Limit 초과 | 429 |
| `DOMEGGOOK_API_ERROR` | 도매꾹 API 오류 | 502 |
| `NAVER_API_ERROR` | 네이버 API 오류 | 502 |
| `CATEGORY_NOT_MAPPED` | 카테고리 매핑 없음 | 422 |
| `FORBIDDEN_WORD_DETECTED` | 금지어 검출 | 422 |
| `IMAGE_VALIDATION_FAILED` | 이미지 규격 미달 | 422 |
| `INTERNAL_ERROR` | 내부 서버 오류 | 500 |

---

## WebSocket API (실시간 진행률)

### WS /jobs/{job_id}/stream

작업 진행률 실시간 스트리밍

**Connection:**
```javascript
const ws = new WebSocket('wss://api.storebridge.com/v1/jobs/job-uuid-123/stream');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Progress:', data.progress_percent);
};
```

**Message Format:**
```json
{
  "type": "progress",
  "data": {
    "job_id": "job-uuid-123",
    "progress_percent": 48.5,
    "success_count": 45,
    "failed_count": 3,
    "current_item": "여성 반팔 티셔츠",
    "timestamp": "2025-10-16T10:30:15Z"
  }
}
```

**Event Types:**
- `progress`: 진행률 업데이트
- `item_completed`: 개별 상품 완료
- `item_failed`: 개별 상품 실패
- `job_completed`: 작업 완료
- `job_failed`: 작업 실패

---

## Rate Limiting

### 제한 사항

| 엔드포인트 | 제한 |
|-----------|------|
| `/auth/login` | 10 요청/분 |
| `/jobs` (POST) | 60 요청/시간 |
| `/products/validate` | 100 요청/분 |
| 기타 모든 엔드포인트 | 1000 요청/시간 |

### Rate Limit 헤더

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 850
X-RateLimit-Reset: 1697481600
```

### Rate Limit 초과 시

**Response: 429 Too Many Requests**
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "API rate limit exceeded",
    "retry_after": 300
  }
}
```

---

**작성자**: StoreBridge Team
**최종 수정**: 2025-10-16
**버전**: v1.0
