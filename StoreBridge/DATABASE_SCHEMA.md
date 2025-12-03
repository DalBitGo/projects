# 데이터베이스 스키마 상세 설계

> StoreBridge PostgreSQL 데이터베이스 ERD 및 마이그레이션 스크립트

**작성일**: 2025-10-16
**DBMS**: PostgreSQL 15+
**버전**: 1.0

---

## 목차

1. [ERD (Entity Relationship Diagram)](#erd-entity-relationship-diagram)
2. [테이블 상세 스펙](#테이블-상세-스펙)
3. [인덱스 전략](#인덱스-전략)
4. [마이그레이션 스크립트](#마이그레이션-스크립트)
5. [시드 데이터](#시드-데이터)
6. [쿼리 최적화 가이드](#쿼리-최적화-가이드)

---

## ERD (Entity Relationship Diagram)

### 전체 ERD

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌──────────────────┐         ┌─────────────────────────────┐ │
│  │    products      │         │  product_registrations      │ │
│  ├──────────────────┤         ├─────────────────────────────┤ │
│  │ id (PK)          │────────<│ product_id (FK)             │ │
│  │ domeggook_item_id│  1:N    │ id (PK)                     │ │
│  │ name             │         │ state                       │ │
│  │ price            │         │ naver_product_id            │ │
│  │ category         │         │ seller_product_code         │ │
│  │ raw_data (JSONB) │         │ retry_count                 │ │
│  │ created_at       │         │ error_message               │ │
│  │ updated_at       │         │ metadata (JSONB)            │ │
│  └──────────────────┘         │ created_at                  │ │
│                                │ updated_at                  │ │
│                                └─────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────┐         ┌─────────────────────────────┐ │
│  │ category_mappings│         │  jobs                       │ │
│  ├──────────────────┤         ├─────────────────────────────┤ │
│  │ id (PK)          │         │ id (PK)                     │ │
│  │ domeggook_category│        │ type                        │ │
│  │ naver_leaf_cat_id│         │ status                      │ │
│  │ required_attrs   │         │ total_count                 │ │
│  │   (JSONB)        │         │ success_count               │ │
│  │ confidence       │         │ failed_count                │ │
│  │ is_active        │         │ error_summary               │ │
│  │ created_at       │         │ created_by                  │ │
│  │ updated_at       │         │ created_at                  │ │
│  └──────────────────┘         │ completed_at                │ │
│                                └─────────────────────────────┘ │
│                                           ↑                     │
│                                           │                     │
│                                           │ N:1                 │
│  ┌──────────────────┐         ┌─────────────────────────────┐ │
│  │  job_items       │────────>│ jobs                        │ │
│  ├──────────────────┤  N:1    │ id (PK)                     │ │
│  │ id (PK)          │         └─────────────────────────────┘ │
│  │ job_id (FK)      │                                         │
│  │ product_id (FK)  │                                         │
│  │ registration_id  │                                         │
│  │   (FK)           │                                         │
│  │ status           │                                         │
│  │ error_message    │                                         │
│  │ created_at       │                                         │
│  │ updated_at       │                                         │
│  └──────────────────┘                                         │
│                                                                 │
│  ┌──────────────────┐         ┌─────────────────────────────┐ │
│  │ forbidden_words  │         │  audit_logs                 │ │
│  ├──────────────────┤         ├─────────────────────────────┤ │
│  │ id (PK)          │         │ id (PK)                     │ │
│  │ word             │         │ entity_type                 │ │
│  │ category         │         │ entity_id                   │ │
│  │ severity         │         │ action                      │ │
│  │ is_active        │         │ user_id                     │ │
│  │ created_at       │         │ changes (JSONB)             │ │
│  └──────────────────┘         │ created_at                  │ │
│                                └─────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 테이블 상세 스펙

### 1. `products` (도매꾹 원본 상품 데이터)

**목적**: 도매꾹에서 수집한 상품 원본 데이터 저장

```sql
CREATE TABLE products (
    -- 기본키
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 도매꾹 식별자 (외부 시스템 연동 키)
    domeggook_item_id VARCHAR(100) UNIQUE NOT NULL,

    -- 상품 기본 정보
    name VARCHAR(500) NOT NULL,
    price INTEGER NOT NULL CHECK (price >= 0),
    original_price INTEGER CHECK (original_price >= 0),
    category VARCHAR(200),
    supplier VARCHAR(200),

    -- 상품 상세
    description TEXT,
    images TEXT[],  -- 이미지 URL 배열
    options JSONB,  -- 옵션 정보 (구조화되지 않은 원본)

    -- 재고/판매 정보
    stock_quantity INTEGER DEFAULT 0,
    is_available BOOLEAN DEFAULT TRUE,

    -- 원본 데이터 (도매꾹 API 응답 전체)
    raw_data JSONB NOT NULL,

    -- 메타데이터
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- 제약조건
    CONSTRAINT products_price_check CHECK (price <= original_price OR original_price IS NULL)
);

-- 인덱스
CREATE INDEX idx_products_domeggook_id ON products(domeggook_item_id);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_supplier ON products(supplier);
CREATE INDEX idx_products_updated_at ON products(updated_at DESC);
CREATE INDEX idx_products_is_available ON products(is_available) WHERE is_available = TRUE;

-- 전문 검색 인덱스 (상품명)
CREATE INDEX idx_products_name_gin ON products USING GIN (to_tsvector('korean', name));

-- 자동 업데이트 트리거
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 테이블 코멘트
COMMENT ON TABLE products IS '도매꾹에서 수집한 상품 원본 데이터';
COMMENT ON COLUMN products.raw_data IS '도매꾹 API 응답 전체 (변환 전 백업용)';
COMMENT ON COLUMN products.options IS '옵션 정보 (파싱 전 원본, 구조 불규칙)';
```

---

### 2. `product_registrations` (상품 등록 상태 추적)

**목적**: 네이버 스마트스토어 등록 프로세스 추적

```sql
CREATE TYPE registration_state AS ENUM (
    'PENDING',        -- 등록 대기
    'VALIDATED',      -- 검증 완료
    'UPLOADING',      -- 이미지 업로드 중
    'REGISTERING',    -- 상품 등록 중
    'COMPLETED',      -- 등록 완료
    'RETRYING',       -- 재시도 중
    'MANUAL_REVIEW',  -- 수동 검토 필요
    'FAILED'          -- 등록 실패 (최종)
);

CREATE TABLE product_registrations (
    -- 기본키
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 외래키
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,

    -- 등록 상태
    state registration_state NOT NULL DEFAULT 'PENDING',

    -- 네이버 연동 정보
    naver_product_id VARCHAR(100),  -- 네이버 상품 ID (등록 후)
    seller_product_code VARCHAR(100) UNIQUE,  -- 판매자 상품 코드 (SKU)

    -- 재시도 정보
    retry_count INTEGER DEFAULT 0 CHECK (retry_count >= 0),
    max_retries INTEGER DEFAULT 3,
    next_retry_at TIMESTAMP WITH TIME ZONE,

    -- 에러 정보
    error_code VARCHAR(100),
    error_message TEXT,
    error_details JSONB,

    -- 변환된 데이터 (네이버 형식)
    metadata JSONB,  -- { "transformed_options": {...}, "s3_image_urls": [...], ... }

    -- 타임스탬프
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    -- 제약조건
    CONSTRAINT reg_completed_at_check
        CHECK ((state = 'COMPLETED' AND completed_at IS NOT NULL) OR state <> 'COMPLETED'),
    CONSTRAINT reg_naver_id_check
        CHECK ((state = 'COMPLETED' AND naver_product_id IS NOT NULL) OR state <> 'COMPLETED')
);

-- 인덱스
CREATE INDEX idx_registrations_product_id ON product_registrations(product_id);
CREATE INDEX idx_registrations_state ON product_registrations(state);
CREATE INDEX idx_registrations_naver_product_id ON product_registrations(naver_product_id)
    WHERE naver_product_id IS NOT NULL;
CREATE INDEX idx_registrations_seller_code ON product_registrations(seller_product_code)
    WHERE seller_product_code IS NOT NULL;
CREATE INDEX idx_registrations_retry ON product_registrations(next_retry_at)
    WHERE state = 'RETRYING' AND next_retry_at IS NOT NULL;

-- 부분 인덱스 (상태별)
CREATE INDEX idx_registrations_pending ON product_registrations(created_at DESC)
    WHERE state = 'PENDING';
CREATE INDEX idx_registrations_manual_review ON product_registrations(created_at DESC)
    WHERE state = 'MANUAL_REVIEW';

-- 자동 업데이트 트리거
CREATE TRIGGER registrations_updated_at
    BEFORE UPDATE ON product_registrations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 상태 전이 검증 트리거
CREATE OR REPLACE FUNCTION validate_state_transition()
RETURNS TRIGGER AS $$
DECLARE
    allowed_states TEXT[];
BEGIN
    -- 허용된 상태 전이 규칙
    CASE OLD.state
        WHEN 'PENDING' THEN
            allowed_states := ARRAY['VALIDATED', 'MANUAL_REVIEW', 'FAILED'];
        WHEN 'VALIDATED' THEN
            allowed_states := ARRAY['UPLOADING', 'MANUAL_REVIEW'];
        WHEN 'UPLOADING' THEN
            allowed_states := ARRAY['REGISTERING', 'RETRYING', 'MANUAL_REVIEW'];
        WHEN 'REGISTERING' THEN
            allowed_states := ARRAY['COMPLETED', 'RETRYING', 'MANUAL_REVIEW'];
        WHEN 'RETRYING' THEN
            allowed_states := ARRAY['UPLOADING', 'REGISTERING', 'MANUAL_REVIEW', 'FAILED'];
        WHEN 'MANUAL_REVIEW' THEN
            allowed_states := ARRAY['PENDING', 'FAILED'];
        WHEN 'COMPLETED' THEN
            allowed_states := ARRAY[]::TEXT[];  -- 완료 후 변경 불가
        WHEN 'FAILED' THEN
            allowed_states := ARRAY[]::TEXT[];  -- 실패 후 변경 불가
    END CASE;

    IF NEW.state::TEXT <> OLD.state::TEXT AND NOT (NEW.state::TEXT = ANY(allowed_states)) THEN
        RAISE EXCEPTION 'Invalid state transition: % -> %', OLD.state, NEW.state;
    END IF;

    -- COMPLETED 시 completed_at 자동 설정
    IF NEW.state = 'COMPLETED' AND NEW.completed_at IS NULL THEN
        NEW.completed_at := NOW();
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER registrations_state_transition
    BEFORE UPDATE OF state ON product_registrations
    FOR EACH ROW
    EXECUTE FUNCTION validate_state_transition();

-- 코멘트
COMMENT ON TABLE product_registrations IS '네이버 스마트스토어 등록 프로세스 추적';
COMMENT ON COLUMN product_registrations.metadata IS '변환된 데이터 (네이버 형식, 이미지 URL 등)';
COMMENT ON COLUMN product_registrations.seller_product_code IS '판매자 상품 코드 (SKU), 향후 재고/주문 연동 시 사용';
```

---

### 3. `category_mappings` (카테고리 매핑 테이블)

**목적**: 도매꾹 ↔ 네이버 카테고리 매핑 및 필수 속성 정의

```sql
CREATE TABLE category_mappings (
    -- 기본키
    id SERIAL PRIMARY KEY,

    -- 도매꾹 카테고리
    domeggook_category VARCHAR(200) NOT NULL,
    domeggook_category_id VARCHAR(50),  -- 도매꾹 카테고리 ID (있다면)

    -- 네이버 카테고리
    naver_leaf_category_id VARCHAR(50) NOT NULL,
    naver_category_name VARCHAR(200),

    -- 필수 속성 정의
    required_attributes JSONB,  -- { "제조일자": {"type": "date", "required": true}, ... }
    default_attributes JSONB,   -- 기본값 자동 채우기 룰

    -- 매핑 품질
    confidence FLOAT DEFAULT 1.0 CHECK (confidence >= 0 AND confidence <= 1),
    mapping_source VARCHAR(50) DEFAULT 'manual',  -- manual/auto/ml

    -- 활성화 여부
    is_active BOOLEAN DEFAULT TRUE,

    -- 사용 통계
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,

    -- 메타데이터
    notes TEXT,
    created_by VARCHAR(100),

    -- 타임스탬프
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- 제약조건
    CONSTRAINT unique_active_mapping
        UNIQUE (domeggook_category, naver_leaf_category_id, is_active)
        DEFERRABLE INITIALLY DEFERRED
);

-- 인덱스
CREATE INDEX idx_category_dg ON category_mappings(domeggook_category) WHERE is_active = TRUE;
CREATE INDEX idx_category_naver ON category_mappings(naver_leaf_category_id);
CREATE INDEX idx_category_confidence ON category_mappings(confidence DESC) WHERE is_active = TRUE;

-- 자동 업데이트 트리거
CREATE TRIGGER category_mappings_updated_at
    BEFORE UPDATE ON category_mappings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 코멘트
COMMENT ON TABLE category_mappings IS '도매꾹 ↔ 네이버 카테고리 매핑 및 필수 속성';
COMMENT ON COLUMN category_mappings.required_attributes IS '네이버 카테고리 필수 속성 정의 (JSON)';
COMMENT ON COLUMN category_mappings.default_attributes IS '속성 기본값 자동 채우기 룰 (JSON)';
COMMENT ON COLUMN category_mappings.confidence IS '매핑 신뢰도 (0.0~1.0), ML 자동 매핑 시 사용';
```

#### 예시 데이터

```sql
INSERT INTO category_mappings (
    domeggook_category,
    naver_leaf_category_id,
    naver_category_name,
    required_attributes,
    default_attributes
) VALUES (
    '여성의류 > 티셔츠',
    '50000123',
    '여성상의',
    '{
        "제조일자": {"type": "date", "required": true, "format": "YYYY-MM-DD"},
        "소재": {"type": "string", "required": true},
        "세탁방법": {"type": "enum", "required": false, "options": ["드라이클리닝", "물세탁"]}
    }',
    '{
        "소재": "면 100%",
        "세탁방법": "드라이클리닝"
    }'
);
```

---

### 4. `jobs` (작업 추적)

**목적**: 대량 작업(import, sync 등) 추적

```sql
CREATE TYPE job_type AS ENUM (
    'IMPORT',           -- 대량 등록
    'SYNC_PRICE',       -- 가격 동기화
    'SYNC_INVENTORY',   -- 재고 동기화
    'MANUAL_REVIEW',    -- 수동 검토
    'CLEANUP'           -- 정리 작업
);

CREATE TYPE job_status AS ENUM (
    'PENDING',    -- 대기 중
    'RUNNING',    -- 실행 중
    'COMPLETED',  -- 완료
    'FAILED',     -- 실패
    'CANCELLED'   -- 취소됨
);

CREATE TABLE jobs (
    -- 기본키
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 작업 정보
    type job_type NOT NULL,
    status job_status NOT NULL DEFAULT 'PENDING',

    -- 통계
    total_count INTEGER NOT NULL DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    skipped_count INTEGER DEFAULT 0,

    -- 에러 요약
    error_summary TEXT,
    error_details JSONB,  -- 에러별 카운트 등

    -- 설정
    config JSONB,  -- 작업 설정 (필터, 옵션 등)

    -- 사용자 정보
    created_by VARCHAR(100),

    -- 타임스탬프
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- 제약조건
    CONSTRAINT jobs_counts_check CHECK (
        success_count + failed_count + skipped_count <= total_count
    ),
    CONSTRAINT jobs_completed_at_check CHECK (
        (status = 'COMPLETED' AND completed_at IS NOT NULL) OR
        (status <> 'COMPLETED')
    )
);

-- 인덱스
CREATE INDEX idx_jobs_status ON jobs(status, created_at DESC);
CREATE INDEX idx_jobs_type ON jobs(type);
CREATE INDEX idx_jobs_created_by ON jobs(created_by);

-- 진행률 계산 뷰
CREATE VIEW job_progress AS
SELECT
    id,
    type,
    status,
    total_count,
    success_count,
    failed_count,
    skipped_count,
    CASE
        WHEN total_count > 0 THEN
            ROUND((success_count + failed_count + skipped_count)::NUMERIC / total_count * 100, 2)
        ELSE 0
    END AS progress_percent,
    CASE
        WHEN status = 'RUNNING' AND started_at IS NOT NULL THEN
            EXTRACT(EPOCH FROM (NOW() - started_at))
        WHEN status = 'COMPLETED' AND started_at IS NOT NULL AND completed_at IS NOT NULL THEN
            EXTRACT(EPOCH FROM (completed_at - started_at))
        ELSE NULL
    END AS duration_seconds,
    created_at
FROM jobs;

-- 코멘트
COMMENT ON TABLE jobs IS '대량 작업 추적 (import, sync 등)';
COMMENT ON VIEW job_progress IS '작업 진행률 및 소요 시간 계산 뷰';
```

---

### 5. `job_items` (작업 항목 상세)

**목적**: 작업에 포함된 개별 상품 추적

```sql
CREATE TABLE job_items (
    -- 기본키
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 외래키
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    registration_id UUID REFERENCES product_registrations(id) ON DELETE SET NULL,

    -- 상태
    status VARCHAR(50) NOT NULL,  -- pending/processing/success/failed/skipped

    -- 에러 정보
    error_code VARCHAR(100),
    error_message TEXT,

    -- 타임스탬프
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- 인덱스
CREATE INDEX idx_job_items_job_id ON job_items(job_id);
CREATE INDEX idx_job_items_product_id ON job_items(product_id);
CREATE INDEX idx_job_items_status ON job_items(job_id, status);

-- 자동 업데이트 트리거
CREATE TRIGGER job_items_updated_at
    BEFORE UPDATE ON job_items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Job 통계 자동 업데이트 트리거
CREATE OR REPLACE FUNCTION update_job_statistics()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        UPDATE jobs
        SET
            success_count = (
                SELECT COUNT(*) FROM job_items
                WHERE job_id = NEW.job_id AND status = 'success'
            ),
            failed_count = (
                SELECT COUNT(*) FROM job_items
                WHERE job_id = NEW.job_id AND status = 'failed'
            ),
            skipped_count = (
                SELECT COUNT(*) FROM job_items
                WHERE job_id = NEW.job_id AND status = 'skipped'
            )
        WHERE id = NEW.job_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER job_items_update_statistics
    AFTER INSERT OR UPDATE OF status ON job_items
    FOR EACH ROW
    EXECUTE FUNCTION update_job_statistics();

-- 코멘트
COMMENT ON TABLE job_items IS '작업에 포함된 개별 상품 추적';
```

---

### 6. `forbidden_words` (금지어 관리)

**목적**: 네이버 반려 방지용 금지어 관리

```sql
CREATE TABLE forbidden_words (
    -- 기본키
    id SERIAL PRIMARY KEY,

    -- 금지어
    word VARCHAR(200) NOT NULL,
    pattern VARCHAR(200),  -- 정규표현식 패턴

    -- 분류
    category VARCHAR(50),  -- brand/trademark/prohibited/etc
    severity VARCHAR(20) DEFAULT 'warning',  -- error/warning/info

    -- 대체어
    replacement VARCHAR(200),

    -- 활성화
    is_active BOOLEAN DEFAULT TRUE,

    -- 메타데이터
    description TEXT,
    source VARCHAR(100),  -- 출처 (네이버 가이드, 실제 반려 사례 등)

    -- 타임스탬프
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- 제약조건
    CONSTRAINT unique_active_word UNIQUE (word, is_active)
        DEFERRABLE INITIALLY DEFERRED
);

-- 인덱스
CREATE INDEX idx_forbidden_words_word ON forbidden_words(word) WHERE is_active = TRUE;
CREATE INDEX idx_forbidden_words_category ON forbidden_words(category) WHERE is_active = TRUE;

-- 전문 검색 인덱스
CREATE INDEX idx_forbidden_words_pattern_gin ON forbidden_words
    USING GIN (to_tsvector('korean', word)) WHERE is_active = TRUE;

-- 자동 업데이트 트리거
CREATE TRIGGER forbidden_words_updated_at
    BEFORE UPDATE ON forbidden_words
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 코멘트
COMMENT ON TABLE forbidden_words IS '네이버 반려 방지용 금지어 관리';
COMMENT ON COLUMN forbidden_words.pattern IS '정규표현식 패턴 (고급 매칭용)';
COMMENT ON COLUMN forbidden_words.replacement IS '자동 대체어 (가능한 경우)';
```

---

### 7. `audit_logs` (감사 로그)

**목적**: 데이터 변경 이력 추적 (컴플라이언스, 디버깅)

```sql
CREATE TABLE audit_logs (
    -- 기본키
    id BIGSERIAL PRIMARY KEY,

    -- 대상 엔티티
    entity_type VARCHAR(50) NOT NULL,  -- products/registrations/jobs/etc
    entity_id UUID NOT NULL,

    -- 작업 정보
    action VARCHAR(50) NOT NULL,  -- INSERT/UPDATE/DELETE

    -- 사용자 정보
    user_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,

    -- 변경 내용
    old_values JSONB,
    new_values JSONB,
    changes JSONB,  -- 변경된 필드만

    -- 타임스탬프
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 (파티셔닝과 함께 사용 권장)
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);

-- 파티셔닝 (월별)
CREATE TABLE audit_logs_y2025m10 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');

-- 코멘트
COMMENT ON TABLE audit_logs IS '데이터 변경 이력 추적 (감사, 디버깅용)';
COMMENT ON COLUMN audit_logs.changes IS '변경된 필드만 추출 (효율성)';
```

---

## 인덱스 전략

### 인덱스 선택 가이드

```sql
-- 1. B-Tree 인덱스 (기본)
-- 용도: 등호(=), 범위(<, >), 정렬(ORDER BY)
CREATE INDEX idx_products_created_at ON products(created_at DESC);

-- 2. 부분 인덱스 (Partial Index)
-- 용도: 특정 조건만 자주 조회 (인덱스 크기 절감)
CREATE INDEX idx_registrations_pending ON product_registrations(created_at DESC)
    WHERE state = 'PENDING';

-- 3. 복합 인덱스 (Composite Index)
-- 용도: 여러 컬럼 동시 조회 (순서 중요!)
CREATE INDEX idx_job_items_job_status ON job_items(job_id, status);

-- 4. GIN 인덱스 (Generalized Inverted Index)
-- 용도: JSONB, 배열, 전문 검색
CREATE INDEX idx_products_raw_data_gin ON products USING GIN (raw_data);

-- 5. 고유 인덱스 (Unique Index)
-- 용도: 중복 방지 + 조회 성능
CREATE UNIQUE INDEX idx_products_domeggook_id ON products(domeggook_item_id);
```

### 인덱스 유지보수

```sql
-- 인덱스 사용률 확인
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan ASC;

-- 사용 안 하는 인덱스 제거 (idx_scan = 0)

-- 인덱스 재구축 (Fragmentation 해소)
REINDEX INDEX CONCURRENTLY idx_products_created_at;
```

---

## 마이그레이션 스크립트

### Alembic 설정

```python
# migrations/env.py

from alembic import context
from sqlalchemy import engine_from_config, pool
from app.models.database import Base
import app.models.product  # 모델 임포트

target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        context.config.get_section(context.config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()
```

### Migration Script 예시

```python
# migrations/versions/001_initial_schema.py

"""Initial schema

Revision ID: 001
Create Date: 2025-10-16
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None

def upgrade():
    # 1. ENUM 타입 생성
    op.execute("""
        CREATE TYPE registration_state AS ENUM (
            'PENDING', 'VALIDATED', 'UPLOADING', 'REGISTERING',
            'COMPLETED', 'RETRYING', 'MANUAL_REVIEW', 'FAILED'
        );
    """)

    op.execute("""
        CREATE TYPE job_type AS ENUM (
            'IMPORT', 'SYNC_PRICE', 'SYNC_INVENTORY',
            'MANUAL_REVIEW', 'CLEANUP'
        );
    """)

    op.execute("""
        CREATE TYPE job_status AS ENUM (
            'PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED'
        );
    """)

    # 2. products 테이블
    op.create_table(
        'products',
        sa.Column('id', postgresql.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('domeggook_item_id', sa.String(100), nullable=False),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('original_price', sa.Integer()),
        sa.Column('category', sa.String(200)),
        sa.Column('supplier', sa.String(200)),
        sa.Column('description', sa.Text()),
        sa.Column('images', postgresql.ARRAY(sa.Text())),
        sa.Column('options', postgresql.JSONB()),
        sa.Column('stock_quantity', sa.Integer(), server_default='0'),
        sa.Column('is_available', sa.Boolean(), server_default='TRUE'),
        sa.Column('raw_data', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('domeggook_item_id'),
        sa.CheckConstraint('price >= 0', name='products_price_check')
    )

    # ... (나머지 테이블 생성)

    # 3. 트리거 생성
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER products_updated_at
            BEFORE UPDATE ON products
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)

def downgrade():
    op.drop_table('products')
    # ... (역순 삭제)
    op.execute('DROP TYPE registration_state;')
    op.execute('DROP TYPE job_type;')
    op.execute('DROP TYPE job_status;')
```

---

## 시드 데이터

### 카테고리 매핑 시드

```sql
-- migrations/seeds/001_category_mappings.sql

INSERT INTO category_mappings (
    domeggook_category,
    naver_leaf_category_id,
    naver_category_name,
    required_attributes,
    default_attributes,
    confidence
) VALUES
('여성의류 > 티셔츠', '50000123', '여성상의',
 '{"제조일자": {"type": "date", "required": true}, "소재": {"type": "string", "required": true}}',
 '{"소재": "면 100%", "세탁방법": "드라이클리닝"}', 1.0),

('여성의류 > 바지', '50000124', '여성하의',
 '{"제조일자": {"type": "date", "required": true}, "소재": {"type": "string", "required": true}}',
 '{"소재": "면 95%, 스판 5%"}', 1.0),

('남성의류 > 셔츠', '50000125', '남성상의',
 '{"제조일자": {"type": "date", "required": true}, "소재": {"type": "string", "required": true}}',
 '{"소재": "면 100%"}', 1.0);
```

### 금지어 시드

```sql
-- migrations/seeds/002_forbidden_words.sql

INSERT INTO forbidden_words (word, category, severity, replacement, description) VALUES
('가품', 'prohibited', 'error', '제품', '가품 표현 금지'),
('짝퉁', 'prohibited', 'error', NULL, '모조품 표현 금지'),
('명품', 'trademark', 'warning', '고급', '상표권 침해 가능'),
('정품', 'trademark', 'warning', NULL, '인증 없이 사용 불가'),
('최저가', 'prohibited', 'error', '합리적 가격', '최저가 보장 표현 금지');
```

---

## 쿼리 최적화 가이드

### 자주 사용하는 쿼리 패턴

```sql
-- 1. 등록 대기 중인 상품 조회 (PENDING 상태)
SELECT p.*, pr.id AS registration_id, pr.state
FROM products p
INNER JOIN product_registrations pr ON p.id = pr.product_id
WHERE pr.state = 'PENDING'
ORDER BY pr.created_at ASC
LIMIT 100;
-- 인덱스: idx_registrations_pending

-- 2. 특정 작업의 진행률 조회
SELECT * FROM job_progress WHERE id = 'job-uuid';
-- 뷰 활용

-- 3. 최근 1시간 이내 가격 변경된 상품
SELECT * FROM products
WHERE updated_at > NOW() - INTERVAL '1 hour'
  AND is_available = TRUE;
-- 인덱스: idx_products_updated_at, idx_products_is_available

-- 4. 반려된 상품 중 특정 에러 코드
SELECT p.name, pr.error_code, pr.error_message
FROM products p
INNER JOIN product_registrations pr ON p.id = pr.product_id
WHERE pr.state = 'MANUAL_REVIEW'
  AND pr.error_code = 'CATEGORY_MISMATCH'
ORDER BY pr.created_at DESC;
-- 인덱스: idx_registrations_manual_review

-- 5. 카테고리별 등록 성공률
SELECT
    cm.domeggook_category,
    COUNT(pr.id) AS total,
    SUM(CASE WHEN pr.state = 'COMPLETED' THEN 1 ELSE 0 END) AS success,
    ROUND(SUM(CASE WHEN pr.state = 'COMPLETED' THEN 1 ELSE 0 END)::NUMERIC / COUNT(pr.id) * 100, 2) AS success_rate
FROM category_mappings cm
LEFT JOIN products p ON p.category = cm.domeggook_category
LEFT JOIN product_registrations pr ON pr.product_id = p.id
WHERE cm.is_active = TRUE
GROUP BY cm.domeggook_category
ORDER BY success_rate DESC;
```

### 쿼리 성능 분석

```sql
-- EXPLAIN ANALYZE로 실행 계획 확인
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM products
WHERE category = '여성의류 > 티셔츠'
  AND is_available = TRUE
ORDER BY created_at DESC
LIMIT 20;

-- Seq Scan이 나오면 인덱스 추가 고려
-- Index Scan이 나와야 정상
```

---

**작성자**: StoreBridge Team
**최종 수정**: 2025-10-16
**버전**: 1.0
