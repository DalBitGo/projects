# StoreBridge Test Plan
**테스트 계획서**

---

## 📋 Table of Contents

1. [Test Strategy Overview](#test-strategy-overview)
2. [Test Pyramid & Coverage Targets](#test-pyramid--coverage-targets)
3. [Test Environments](#test-environments)
4. [Unit Testing Plan](#unit-testing-plan)
5. [Integration Testing Plan](#integration-testing-plan)
6. [End-to-End Testing Plan](#end-to-end-testing-plan)
7. [Performance & Load Testing Plan](#performance--load-testing-plan)
8. [Test Data Management](#test-data-management)
9. [Mocking Strategy](#mocking-strategy)
10. [CI/CD Integration](#cicd-integration)
11. [Test Execution Guide](#test-execution-guide)
12. [Appendix: Sample Test Cases](#appendix-sample-test-cases)

---

## 1. Test Strategy Overview

### 1.1 Testing Philosophy

StoreBridge의 테스트 전략은 다음 원칙을 따릅니다:

| 원칙 | 설명 |
|------|------|
| **Fast Feedback** | 단위 테스트는 1초 이내, 통합 테스트는 10초 이내 실행 |
| **Deterministic** | 동일한 입력은 항상 동일한 결과 (시간/네트워크 독립적) |
| **Isolated** | 각 테스트는 독립적이며 순서에 무관 |
| **Maintainable** | 테스트 코드도 프로덕션 코드와 동일한 품질 기준 적용 |

### 1.2 Test Scope

```
┌─────────────────────────────────────────────────────────────┐
│                     Test Scope                              │
├─────────────────────────────────────────────────────────────┤
│ ✅ Included:                                                │
│   - Rate Limiter atomic operations                          │
│   - Option Mapper parsing logic (1D/2D/3D)                  │
│   - Validators (category, image, forbidden words)           │
│   - State machine transitions                               │
│   - API integration (Domeggook, Naver)                      │
│   - Image processing pipeline                               │
│   - Database queries & triggers                             │
│   - Error handling & retry logic                            │
│                                                              │
│ ❌ Excluded:                                                │
│   - Third-party library internals (httpx, SQLAlchemy)       │
│   - Infrastructure (Kubernetes, Redis, PostgreSQL)          │
│   - UI/Frontend (out of scope - backend only)               │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Test Pyramid & Coverage Targets

### 2.1 Test Pyramid

```
              /\
             /  \        E2E Tests (10%)
            /    \       - 전체 등록 플로우
           /______\      - 실패 시나리오
          /        \
         /          \    Integration Tests (30%)
        /            \   - API 통합
       /______________\  - DB 통합
      /                \
     /                  \ Unit Tests (60%)
    /                    \ - 비즈니스 로직
   /______________________\ - Validators, Transformers
```

### 2.2 Coverage Targets

| Test Type | Target Coverage | Execution Time | Frequency |
|-----------|----------------|----------------|-----------|
| **Unit Tests** | 85% (line), 80% (branch) | < 1 min | Every commit |
| **Integration Tests** | 70% (critical paths) | < 5 min | Every PR |
| **E2E Tests** | 100% (happy paths) | < 15 min | Before merge |
| **Load Tests** | N/A (performance metrics) | 30 min | Weekly + before release |

### 2.3 Critical Paths (100% Coverage Required)

1. **Rate Limiter** - 네이버 API 2 TPS 제약 위반 방지 (P0)
2. **State Machine** - 잘못된 상태 전환 방지 (P0)
3. **Image Upload** - 네이버 업로드 실패 처리 (P0)
4. **Option Mapper** - 잘못된 옵션 구조로 인한 등록 실패 방지 (P1)

---

## 3. Test Environments

### 3.1 Environment Matrix

| Environment | Purpose | Database | Redis | External APIs |
|-------------|---------|----------|-------|---------------|
| **local** | 개발자 로컬 개발 | PostgreSQL (Docker) | Redis (Docker) | VCR.py (mocked) |
| **ci** | GitHub Actions | PostgreSQL (service) | Redis (service) | VCR.py (mocked) |
| **staging** | 통합 테스트 | RDS (isolated) | ElastiCache | **Real APIs** (sandbox) |
| **production** | N/A (no tests) | - | - | - |

### 3.2 Environment Configuration

**local / ci** (.env.test):
```bash
DATABASE_URL=postgresql://test:test@localhost:5432/storebridge_test
REDIS_URL=redis://localhost:6379/1
DOMEGGOOK_API_KEY=test_key_12345
NAVER_CLIENT_ID=test_client
NAVER_CLIENT_SECRET=test_secret
ENVIRONMENT=test
VCR_MODE=once  # once: 첫 실행 시 녹화, 이후 재생
```

**staging** (.env.staging):
```bash
DATABASE_URL=postgresql://user:pass@staging-db.rds.amazonaws.com/storebridge_staging
REDIS_URL=redis://staging-redis.elasticache.amazonaws.com:6379
DOMEGGOOK_API_KEY=${DOMEGGOOK_SANDBOX_KEY}  # Sandbox API key
NAVER_CLIENT_ID=${NAVER_STAGING_CLIENT_ID}
NAVER_CLIENT_SECRET=${NAVER_STAGING_SECRET}
ENVIRONMENT=staging
VCR_MODE=none  # 실제 API 호출
```

---

## 4. Unit Testing Plan

### 4.1 Test Structure

```
tests/
├── unit/
│   ├── services/
│   │   ├── test_rate_limiter.py          # Rate Limiter (P0)
│   │   ├── test_option_mapper.py         # Option parsing (P1)
│   │   └── test_image_processor.py       # Image pipeline (P1)
│   ├── validators/
│   │   ├── test_product_validator.py     # 상품 검증
│   │   ├── test_category_validator.py    # 카테고리 매핑
│   │   └── test_forbidden_word_validator.py  # 금칙어
│   ├── transformers/
│   │   ├── test_product_transformer.py   # 데이터 변환
│   │   └── test_image_transformer.py     # 이미지 변환
│   ├── workflows/
│   │   └── test_registration_workflow.py # State machine
│   └── connectors/
│       ├── test_domeggook_client.py      # 도매꾹 클라이언트
│       └── test_naver_client.py          # 네이버 클라이언트
```

### 4.2 Rate Limiter Tests (P0 - Critical)

**테스트 목표:**
- Lua 스크립트의 atomic operation 검증
- Race condition 방지 확인
- Burst Max 기능 동작 확인

**tests/unit/services/test_rate_limiter.py:**

```python
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.services.rate_limiter import NaverRateLimiter

class TestNaverRateLimiter:
    """네이버 API Rate Limiter 테스트 (2 TPS 제약)"""

    @pytest.fixture
    def redis_mock(self):
        """Redis mock with eval support"""
        redis = AsyncMock()
        redis.eval = AsyncMock()
        return redis

    @pytest.fixture
    def limiter(self, redis_mock):
        return NaverRateLimiter(redis=redis_mock, max_tps=2)

    # ===== Happy Path =====

    @pytest.mark.asyncio
    async def test_acquire_success_within_limit(self, limiter, redis_mock):
        """2 TPS 이내 요청은 성공"""
        redis_mock.eval.return_value = 1  # Lua script returns 1 (success)

        result = await limiter.acquire()

        assert result is True
        redis_mock.eval.assert_called_once()

    @pytest.mark.asyncio
    async def test_acquire_blocked_over_limit(self, limiter, redis_mock):
        """2 TPS 초과 요청은 차단"""
        redis_mock.eval.return_value = 0  # Lua script returns 0 (blocked)

        result = await limiter.acquire()

        assert result is False

    # ===== Race Condition Test =====

    @pytest.mark.asyncio
    async def test_concurrent_acquire_no_race_condition(self, limiter, redis_mock):
        """동시 요청 시 Race Condition 없음 (Lua atomic)"""
        call_count = 0

        async def mock_eval(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                return 1  # First 2 succeed
            else:
                return 0  # Rest blocked

        redis_mock.eval.side_effect = mock_eval

        # 10개 동시 요청 (max_tps=2이므로 2개만 성공해야 함)
        tasks = [limiter.acquire() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        success_count = sum(results)
        assert success_count == 2, "Only 2 requests should succeed"
        assert redis_mock.eval.call_count == 10

    # ===== Burst Max Test =====

    @pytest.mark.asyncio
    async def test_burst_max_allows_temporary_spike(self, redis_mock):
        """Burst Max는 일시적 스파이크 허용 (3 TPS)"""
        limiter = NaverRateLimiter(
            redis=redis_mock,
            max_tps=2,
            burst_max=3  # 일시적으로 3 TPS 허용
        )

        call_count = 0

        async def mock_eval(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 3:  # Burst allows 3
                return 1
            else:
                return 0

        redis_mock.eval.side_effect = mock_eval

        tasks = [limiter.acquire() for _ in range(5)]
        results = await asyncio.gather(*tasks)

        assert sum(results) == 3, "Burst allows 3 requests temporarily"

    # ===== TTL Test =====

    @pytest.mark.asyncio
    async def test_redis_key_expires_after_ttl(self, limiter, redis_mock):
        """Redis key는 TTL 후 자동 만료"""
        redis_mock.eval.return_value = 1

        await limiter.acquire()

        # Lua 스크립트에 TTL이 전달되는지 확인
        call_args = redis_mock.eval.call_args
        assert call_args[0][2] == limiter.ttl  # ARGV[2] = ttl

    # ===== Error Handling =====

    @pytest.mark.asyncio
    async def test_redis_connection_error_raises_exception(self, limiter, redis_mock):
        """Redis 연결 오류 시 예외 발생"""
        redis_mock.eval.side_effect = ConnectionError("Redis unavailable")

        with pytest.raises(ConnectionError):
            await limiter.acquire()

    @pytest.mark.asyncio
    async def test_lua_script_error_raises_exception(self, limiter, redis_mock):
        """Lua 스크립트 오류 시 예외 발생"""
        redis_mock.eval.side_effect = Exception("Lua script error")

        with pytest.raises(Exception):
            await limiter.acquire()
```

**실행 시간 목표:** < 1초 (모든 Rate Limiter 테스트)

---

### 4.3 Option Mapper Tests (P1 - High)

**테스트 목표:**
- 1D/2D/3D 옵션 파싱 정확도
- Separator 자동 감지
- Edge cases (공백, 특수문자, 빈 값)

**tests/unit/services/test_option_mapper.py:**

```python
import pytest
from app.services.option_mapper import OptionMapper

class TestOptionMapper:
    """옵션 매핑 테스트 (도매꾹 → 네이버)"""

    @pytest.fixture
    def mapper(self):
        return OptionMapper()

    # ===== 1D Options (Simple) =====

    def test_parse_1d_simple_options(self, mapper):
        """단일 차원 옵션 (색상만)"""
        raw_options = ["블랙", "화이트", "네이비"]

        result = mapper.parse(raw_options)

        assert result["type"] == "SIMPLE"
        assert result["dimension_name"] == "색상"
        assert result["values"] == ["블랙", "화이트", "네이비"]

    # ===== 2D Options (Combination) =====

    def test_parse_2d_combination_with_dash(self, mapper):
        """2차원 조합 옵션 (색상-사이즈, separator='-')"""
        raw_options = ["블랙-S", "블랙-M", "화이트-S", "화이트-M"]

        result = mapper.parse(raw_options)

        assert result["type"] == "COMBINATION"
        assert result["separator"] == "-"
        assert len(result["dimensions"]) == 2

        # Dimension 1: 색상
        assert result["dimensions"][0]["name"] == "색상"
        assert set(result["dimensions"][0]["values"]) == {"블랙", "화이트"}

        # Dimension 2: 사이즈
        assert result["dimensions"][1]["name"] == "사이즈"
        assert set(result["dimensions"][1]["values"]) == {"S", "M"}

        # Combinations
        assert len(result["combinations"]) == 4
        assert {"색상": "블랙", "사이즈": "S"} in result["combinations"]

    def test_parse_2d_combination_with_slash(self, mapper):
        """2차원 조합 옵션 (separator='/')"""
        raw_options = ["레드/L", "블루/XL"]

        result = mapper.parse(raw_options)

        assert result["type"] == "COMBINATION"
        assert result["separator"] == "/"
        assert len(result["dimensions"]) == 2

    # ===== 3D Options (Combination) =====

    def test_parse_3d_combination(self, mapper):
        """3차원 조합 옵션 (색상-사이즈-재질)"""
        raw_options = [
            "블랙-S-면",
            "블랙-M-면",
            "블랙-M-폴리",
            "화이트-S-면"
        ]

        result = mapper.parse(raw_options)

        assert result["type"] == "COMBINATION"
        assert len(result["dimensions"]) == 3
        assert result["dimensions"][0]["name"] == "색상"
        assert result["dimensions"][1]["name"] == "사이즈"
        assert result["dimensions"][2]["name"] == "재질"

    # ===== Edge Cases =====

    def test_empty_options_returns_empty_result(self, mapper):
        """빈 옵션 리스트"""
        result = mapper.parse([])

        assert result["type"] == "EMPTY"
        assert result["dimensions"] == []

    def test_options_with_whitespace(self, mapper):
        """공백 포함 옵션"""
        raw_options = [" 블랙 - S ", " 화이트 - M "]

        result = mapper.parse(raw_options)

        # 공백 제거 후 파싱
        assert result["type"] == "COMBINATION"
        assert result["dimensions"][0]["values"] == ["블랙", "화이트"]
        assert result["dimensions"][1]["values"] == ["S", "M"]

    def test_options_with_special_characters(self, mapper):
        """특수문자 포함 옵션"""
        raw_options = ["블랙(무광)-S", "화이트(광택)-M"]

        result = mapper.parse(raw_options)

        assert result["type"] == "COMBINATION"
        assert "블랙(무광)" in result["dimensions"][0]["values"]

    def test_inconsistent_separator_raises_error(self, mapper):
        """일관성 없는 separator"""
        raw_options = ["블랙-S", "화이트/M"]  # Mixed separators

        with pytest.raises(ValueError, match="Inconsistent separator"):
            mapper.parse(raw_options)

    # ===== Naver Format Conversion =====

    def test_to_naver_format_2d(self, mapper):
        """네이버 API 형식 변환"""
        raw_options = ["블랙-S", "화이트-M"]
        parsed = mapper.parse(raw_options)

        naver_format = mapper.to_naver_format(parsed)

        assert naver_format["optionType"] == "COMBINATION"
        assert len(naver_format["optionCombinations"]) == 2
        assert naver_format["optionCombinations"][0] == {
            "optionName1": "색상",
            "optionValue1": "블랙",
            "optionName2": "사이즈",
            "optionValue2": "S",
            "stockQuantity": 0,  # Default
            "price": 0  # To be filled by transformer
        }
```

**실행 시간 목표:** < 500ms

---

### 4.4 Validator Tests

**tests/unit/validators/test_forbidden_word_validator.py:**

```python
import pytest
from app.validators.forbidden_word_validator import ForbiddenWordValidator

class TestForbiddenWordValidator:
    """금칙어 검증 테스트"""

    @pytest.fixture
    def validator(self):
        return ForbiddenWordValidator(
            forbidden_words=["병 치료", "의약품", "100% 효과", "무조건"]
        )

    def test_clean_text_passes(self, validator):
        """금칙어 없는 텍스트 통과"""
        result = validator.validate("고품질 면 티셔츠입니다")

        assert result.is_valid is True
        assert result.errors == []

    def test_forbidden_word_detected(self, validator):
        """금칙어 감지"""
        result = validator.validate("이 제품은 병 치료에 효과적입니다")

        assert result.is_valid is False
        assert "병 치료" in result.errors[0]

    def test_multiple_forbidden_words(self, validator):
        """여러 금칙어 감지"""
        text = "100% 효과를 무조건 보장합니다"
        result = validator.validate(text)

        assert result.is_valid is False
        assert len(result.errors) == 2

    def test_case_insensitive_matching(self, validator):
        """대소문자 무관 매칭"""
        result = validator.validate("이 제품은 의약품이 아닙니다")

        assert result.is_valid is False  # "의약품" detected
```

---

### 4.5 State Machine Tests

**tests/unit/workflows/test_registration_workflow.py:**

```python
import pytest
from app.workflows.registration_workflow import RegistrationStateMachine, State

class TestRegistrationStateMachine:
    """등록 플로우 State Machine 테스트"""

    @pytest.fixture
    def state_machine(self):
        return RegistrationStateMachine()

    # ===== Valid Transitions =====

    def test_pending_to_validated(self, state_machine):
        """PENDING → VALIDATED (valid)"""
        state_machine.current_state = State.PENDING

        state_machine.transition_to(State.VALIDATED)

        assert state_machine.current_state == State.VALIDATED

    def test_validated_to_uploading(self, state_machine):
        """VALIDATED → UPLOADING (valid)"""
        state_machine.current_state = State.VALIDATED

        state_machine.transition_to(State.UPLOADING)

        assert state_machine.current_state == State.UPLOADING

    def test_uploading_to_registering(self, state_machine):
        """UPLOADING → REGISTERING (valid)"""
        state_machine.current_state = State.UPLOADING

        state_machine.transition_to(State.REGISTERING)

        assert state_machine.current_state == State.REGISTERING

    def test_registering_to_completed(self, state_machine):
        """REGISTERING → COMPLETED (valid)"""
        state_machine.current_state = State.REGISTERING

        state_machine.transition_to(State.COMPLETED)

        assert state_machine.current_state == State.COMPLETED

    # ===== Invalid Transitions =====

    def test_pending_to_uploading_invalid(self, state_machine):
        """PENDING → UPLOADING (invalid - must validate first)"""
        state_machine.current_state = State.PENDING

        with pytest.raises(ValueError, match="Invalid state transition"):
            state_machine.transition_to(State.UPLOADING)

    def test_completed_to_any_invalid(self, state_machine):
        """COMPLETED → * (invalid - terminal state)"""
        state_machine.current_state = State.COMPLETED

        with pytest.raises(ValueError, match="Cannot transition from terminal state"):
            state_machine.transition_to(State.PENDING)

    # ===== Retry Logic =====

    def test_retrying_to_validated_on_retry(self, state_machine):
        """RETRYING → VALIDATED (재시도 시 검증 단계로)"""
        state_machine.current_state = State.RETRYING

        state_machine.transition_to(State.VALIDATED)

        assert state_machine.current_state == State.VALIDATED

    # ===== Manual Review =====

    def test_any_state_to_manual_review_allowed(self, state_machine):
        """모든 상태 → MANUAL_REVIEW (allowed)"""
        for state in [State.PENDING, State.VALIDATED, State.UPLOADING]:
            state_machine.current_state = state
            state_machine.transition_to(State.MANUAL_REVIEW)
            assert state_machine.current_state == State.MANUAL_REVIEW
            state_machine.reset()  # Reset for next iteration
```

---

## 5. Integration Testing Plan

### 5.1 Test Structure

```
tests/
├── integration/
│   ├── api/
│   │   ├── test_domeggook_integration.py    # 도매꾹 API 실제 호출
│   │   └── test_naver_integration.py        # 네이버 API 실제 호출
│   ├── database/
│   │   ├── test_product_repository.py       # DB CRUD
│   │   ├── test_state_machine_triggers.py   # DB triggers
│   │   └── test_query_performance.py        # Query optimization
│   ├── cache/
│   │   └── test_redis_integration.py        # Redis cache
│   └── workflows/
│       └── test_full_registration_flow.py   # 전체 플로우
```

### 5.2 Domeggook API Integration Tests

**tests/integration/api/test_domeggook_integration.py:**

```python
import pytest
import vcr
from app.connectors.domeggook_client import DomeggookClient

# VCR.py로 HTTP 요청/응답 녹화/재생
my_vcr = vcr.VCR(
    cassette_library_dir='tests/fixtures/vcr_cassettes',
    record_mode='once',  # 첫 실행 시 녹화, 이후 재생
    match_on=['uri', 'method'],
    filter_headers=['Authorization']  # API key 제거
)

class TestDomeggookIntegration:
    """도매꾹 API 통합 테스트"""

    @pytest.fixture
    def client(self):
        return DomeggookClient(api_key="test_key")

    @my_vcr.use_cassette('domeggook_get_item_list.yaml')
    @pytest.mark.asyncio
    async def test_get_item_list_returns_products(self, client):
        """상품 목록 조회 (실제 API 호출)"""
        result = await client.get_item_list(
            page=1,
            page_size=10,
            category="패션의류"
        )

        assert result["success"] is True
        assert len(result["items"]) > 0
        assert "item_id" in result["items"][0]
        assert "item_name" in result["items"][0]

    @my_vcr.use_cassette('domeggook_get_item_view.yaml')
    @pytest.mark.asyncio
    async def test_get_item_view_returns_detail(self, client):
        """상품 상세 조회"""
        result = await client.get_item_view(item_id="12345")

        assert result["success"] is True
        assert result["item"]["item_id"] == "12345"
        assert "images" in result["item"]
        assert "options" in result["item"]

    @my_vcr.use_cassette('domeggook_rate_limit_429.yaml')
    @pytest.mark.asyncio
    async def test_rate_limit_error_raises_exception(self, client):
        """Rate limit 초과 시 예외 발생 (429)"""
        with pytest.raises(Exception, match="Rate limit exceeded"):
            # 180회 연속 호출 (rate limit 도달)
            for _ in range(181):
                await client.get_item_list(page=1, page_size=1)

    @my_vcr.use_cassette('domeggook_encoding_euc_kr.yaml')
    @pytest.mark.asyncio
    async def test_euc_kr_encoding_handled_correctly(self, client):
        """EUC-KR 인코딩 처리"""
        result = await client.get_item_list(keyword="한글상품명")

        # 한글이 깨지지 않고 정상 파싱되었는지 확인
        assert "한글" in str(result["items"])
```

**VCR Cassette 예시** (tests/fixtures/vcr_cassettes/domeggook_get_item_list.yaml):

```yaml
version: 1
interactions:
- request:
    uri: https://openapi.domeggook.com/getItemList
    method: GET
    body: null
    headers:
      User-Agent: [StoreBridge/1.0]
  response:
    status: {code: 200, message: OK}
    body:
      string: '{"success":true,"items":[{"item_id":"12345","item_name":"면 티셔츠"}]}'
    headers:
      Content-Type: [application/json; charset=utf-8]
```

---

### 5.3 Naver API Integration Tests

**tests/integration/api/test_naver_integration.py:**

```python
import pytest
import vcr
from app.connectors.naver_client import NaverClient

my_vcr = vcr.VCR(
    cassette_library_dir='tests/fixtures/vcr_cassettes',
    record_mode='once',
    filter_headers=['Authorization']
)

class TestNaverIntegration:
    """네이버 Commerce API 통합 테스트"""

    @pytest.fixture
    def client(self):
        return NaverClient(
            client_id="test_client",
            client_secret="test_secret"
        )

    @my_vcr.use_cassette('naver_upload_image.yaml')
    @pytest.mark.asyncio
    async def test_upload_image_returns_url(self, client):
        """이미지 업로드 (네이버 CDN)"""
        image_data = b"fake_image_data"

        result = await client.upload_image(image_data)

        assert result["success"] is True
        assert result["image_url"].startswith("https://shopping-phinf.pstatic.net")

    @my_vcr.use_cassette('naver_register_product.yaml')
    @pytest.mark.asyncio
    async def test_register_product_returns_product_id(self, client):
        """상품 등록"""
        product_data = {
            "originProduct": {
                "name": "테스트 상품",
                "salePrice": 10000,
                "categoryId": "50000000",
                "images": [{"url": "https://example.com/image.jpg"}],
                "detailContent": "상품 상세 설명"
            }
        }

        result = await client.register_product(product_data)

        assert result["success"] is True
        assert "originProductNo" in result

    @my_vcr.use_cassette('naver_rate_limit_429.yaml')
    @pytest.mark.asyncio
    async def test_rate_limit_2_tps_enforced(self, client):
        """2 TPS Rate limit 확인"""
        import time

        # 1초에 3번 호출 시도 (2 TPS 초과)
        start = time.time()
        results = []
        for i in range(3):
            try:
                result = await client.get_product("test_id")
                results.append("success")
            except Exception as e:
                if "429" in str(e):
                    results.append("rate_limited")

        elapsed = time.time() - start
        assert elapsed < 1.5  # 1초 내 실행
        assert results.count("rate_limited") > 0  # 적어도 1개는 차단됨
```

---

### 5.4 Database Integration Tests

**tests/integration/database/test_state_machine_triggers.py:**

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import ProductRegistration, State

class TestStateMachineTriggers:
    """DB 트리거를 통한 State Machine 검증"""

    @pytest.mark.asyncio
    async def test_valid_transition_updates_state(self, db: AsyncSession):
        """Valid transition: DB update 성공"""
        registration = ProductRegistration(
            product_id="uuid-123",
            state=State.PENDING
        )
        db.add(registration)
        await db.commit()

        # PENDING → VALIDATED (valid)
        registration.state = State.VALIDATED
        await db.commit()  # Should succeed

        await db.refresh(registration)
        assert registration.state == State.VALIDATED

    @pytest.mark.asyncio
    async def test_invalid_transition_raises_db_error(self, db: AsyncSession):
        """Invalid transition: DB 트리거가 예외 발생"""
        registration = ProductRegistration(
            product_id="uuid-123",
            state=State.PENDING
        )
        db.add(registration)
        await db.commit()

        # PENDING → UPLOADING (invalid - must validate first)
        registration.state = State.UPLOADING

        with pytest.raises(Exception, match="Invalid state transition"):
            await db.commit()

    @pytest.mark.asyncio
    async def test_updated_at_auto_updated_on_change(self, db: AsyncSession):
        """updated_at 자동 갱신"""
        import asyncio
        from datetime import datetime

        registration = ProductRegistration(
            product_id="uuid-123",
            state=State.PENDING
        )
        db.add(registration)
        await db.commit()

        original_updated_at = registration.updated_at
        await asyncio.sleep(0.1)  # 0.1초 대기

        registration.state = State.VALIDATED
        await db.commit()
        await db.refresh(registration)

        assert registration.updated_at > original_updated_at
```

**tests/integration/database/test_query_performance.py:**

```python
import pytest
from sqlalchemy import select
from app.models import ProductRegistration, State

class TestQueryPerformance:
    """쿼리 성능 테스트 (인덱스 효율성)"""

    @pytest.mark.asyncio
    async def test_pending_state_query_uses_partial_index(self, db):
        """PENDING 상태 조회는 Partial Index 사용"""
        # 1000개 레코드 생성 (500 PENDING, 500 COMPLETED)
        registrations = []
        for i in range(500):
            registrations.append(ProductRegistration(
                product_id=f"uuid-{i}",
                state=State.PENDING
            ))
            registrations.append(ProductRegistration(
                product_id=f"uuid-{i+500}",
                state=State.COMPLETED
            ))
        db.add_all(registrations)
        await db.commit()

        # EXPLAIN ANALYZE로 실행 계획 확인
        stmt = select(ProductRegistration).where(
            ProductRegistration.state == State.PENDING
        )

        import time
        start = time.time()
        result = await db.execute(stmt)
        pending_items = result.scalars().all()
        elapsed = time.time() - start

        assert len(pending_items) == 500
        assert elapsed < 0.1  # 100ms 이내 (Partial Index 사용 시)

    @pytest.mark.asyncio
    async def test_composite_index_on_job_id_status(self, db):
        """(job_id, status) Composite Index 효율성"""
        # Test data setup...

        stmt = select(ProductRegistration).where(
            ProductRegistration.job_id == "job-123",
            ProductRegistration.state == State.COMPLETED
        )

        import time
        start = time.time()
        result = await db.execute(stmt)
        elapsed = time.time() - start

        assert elapsed < 0.05  # 50ms 이내
```

---

## 6. End-to-End Testing Plan

### 6.1 Test Structure

```
tests/
├── e2e/
│   ├── test_single_product_registration.py   # 단일 상품 등록
│   ├── test_batch_registration.py            # 대량 등록 (10개)
│   ├── test_failure_scenarios.py             # 실패 시나리오
│   └── test_manual_review_flow.py            # 수동 검토 플로우
```

### 6.2 Single Product Registration (Happy Path)

**tests/e2e/test_single_product_registration.py:**

```python
import pytest
from httpx import AsyncClient
from app.main import app

class TestSingleProductRegistration:
    """단일 상품 등록 E2E 테스트 (전체 플로우)"""

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_complete_registration_flow(self):
        """
        전체 플로우:
        1. Job 생성 (POST /jobs)
        2. 도매꾹에서 상품 추출
        3. 데이터 변환
        4. 네이버에 등록
        5. Job 완료 확인
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Step 1: Create job
            response = await client.post(
                "/v1/jobs",
                json={
                    "type": "IMPORT",
                    "config": {
                        "source": "domeggook",
                        "filter": {"keyword": "테스트상품"},
                        "limit": 1,
                        "auto_register": True
                    }
                }
            )
            assert response.status_code == 201
            job_id = response.json()["data"]["job_id"]

            # Step 2: Wait for job completion (polling)
            import asyncio
            for _ in range(30):  # Max 30초 대기
                await asyncio.sleep(1)

                status_response = await client.get(f"/v1/jobs/{job_id}")
                status = status_response.json()["data"]["status"]

                if status in ["COMPLETED", "FAILED"]:
                    break

            # Step 3: Verify job completed successfully
            assert status == "COMPLETED"
            stats = status_response.json()["data"]["statistics"]
            assert stats["success_count"] == 1
            assert stats["failed_count"] == 0

            # Step 4: Verify product in database
            products_response = await client.get(
                f"/v1/jobs/{job_id}/products"
            )
            products = products_response.json()["data"]["items"]
            assert len(products) == 1
            assert products[0]["state"] == "COMPLETED"
            assert products[0]["naver_product_id"] is not None
```

---

### 6.3 Batch Registration Test

**tests/e2e/test_batch_registration.py:**

```python
import pytest
from httpx import AsyncClient
from app.main import app

class TestBatchRegistration:
    """대량 등록 테스트 (10개)"""

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_batch_10_products_registration(self):
        """10개 상품 대량 등록"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/v1/jobs",
                json={
                    "type": "IMPORT",
                    "config": {
                        "source": "domeggook",
                        "filter": {"category": "패션의류"},
                        "limit": 10,
                        "auto_register": True
                    }
                }
            )

            job_id = response.json()["data"]["job_id"]

            # Wait for completion (max 5분)
            import asyncio
            for _ in range(300):
                await asyncio.sleep(1)

                status_response = await client.get(f"/v1/jobs/{job_id}")
                status = status_response.json()["data"]["status"]

                if status in ["COMPLETED", "FAILED"]:
                    break

            # Verify at least 80% success rate
            stats = status_response.json()["data"]["statistics"]
            success_rate = stats["success_count"] / stats["total_count"]
            assert success_rate >= 0.8, f"Success rate too low: {success_rate}"
```

---

### 6.4 Failure Scenarios Test

**tests/e2e/test_failure_scenarios.py:**

```python
import pytest
from httpx import AsyncClient
from app.main import app

class TestFailureScenarios:
    """실패 시나리오 테스트"""

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_invalid_category_mapping(self):
        """잘못된 카테고리 매핑 처리"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create product with unmapped category
            response = await client.post(
                "/v1/products",
                json={
                    "domeggook_item_id": "12345",
                    "category": "존재하지않는카테고리"
                }
            )

            assert response.status_code == 400
            assert "CATEGORY_NOT_MAPPED" in response.json()["error"]["code"]

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_forbidden_word_detection(self):
        """금칙어 감지 처리"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/v1/products",
                json={
                    "name": "병 치료에 효과적인 제품",
                    "price": 10000
                }
            )

            assert response.status_code == 400
            assert "FORBIDDEN_WORD" in response.json()["error"]["code"]

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_naver_api_429_retry_logic(self, monkeypatch):
        """네이버 API 429 에러 시 재시도"""
        # Mock Naver API to return 429 on first 2 calls, then 200
        call_count = 0

        async def mock_register_product(self, data):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("429 Too Many Requests")
            return {"success": True, "originProductNo": "12345"}

        monkeypatch.setattr(
            "app.connectors.naver_client.NaverClient.register_product",
            mock_register_product
        )

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/v1/jobs", json={...})
            job_id = response.json()["data"]["job_id"]

            # Wait for retry and completion
            import asyncio
            await asyncio.sleep(10)  # Retry backoff time

            status_response = await client.get(f"/v1/jobs/{job_id}")

            # Should eventually succeed after 2 retries
            assert status_response.json()["data"]["status"] == "COMPLETED"
```

---

## 7. Performance & Load Testing Plan

### 7.1 Test Objectives

| Metric | Target | Test Tool |
|--------|--------|-----------|
| **Throughput** | 5,000 products/day | Locust |
| **Response Time** | P95 < 500ms | Locust |
| **Concurrent Workers** | 5 workers without rate limit violation | Custom script |
| **Rate Limiter Accuracy** | 0% violation (2 TPS exactly) | Redis monitoring |

### 7.2 Load Test Scenarios

**tests/performance/locustfile.py:**

```python
from locust import HttpUser, task, between
import random

class StoreBridgeUser(HttpUser):
    """Performance test user"""
    wait_time = between(1, 3)  # 1-3초 대기

    @task(3)
    def create_import_job(self):
        """상품 가져오기 Job 생성 (가중치 3)"""
        self.client.post("/v1/jobs", json={
            "type": "IMPORT",
            "config": {
                "source": "domeggook",
                "filter": {"category": random.choice(["패션의류", "생활용품"])},
                "limit": 10,
                "auto_register": True
            }
        })

    @task(2)
    def get_job_status(self):
        """Job 상태 조회 (가중치 2)"""
        job_id = "test-job-123"  # Assume exists
        self.client.get(f"/v1/jobs/{job_id}")

    @task(1)
    def get_manual_review_queue(self):
        """수동 검토 큐 조회 (가중치 1)"""
        self.client.get("/v1/manual-review?page_size=20")
```

**실행 명령:**
```bash
# 100명 동시 사용자, 초당 10명씩 증가, 5분간 테스트
locust -f tests/performance/locustfile.py \
  --host https://staging.storebridge.com \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --html reports/load_test_report.html
```

---

### 7.3 Rate Limiter Stress Test

**tests/performance/test_rate_limiter_accuracy.py:**

```python
import pytest
import asyncio
import time
from app.services.rate_limiter import NaverRateLimiter

@pytest.mark.performance
@pytest.mark.asyncio
async def test_rate_limiter_accuracy_under_load():
    """5개 워커가 동시에 요청 시 2 TPS 정확도"""
    limiter = NaverRateLimiter(max_tps=2)

    success_count = 0
    blocked_count = 0

    async def worker():
        """각 워커가 1초에 10번 요청 시도"""
        nonlocal success_count, blocked_count
        for _ in range(10):
            result = await limiter.acquire()
            if result:
                success_count += 1
            else:
                blocked_count += 1
            await asyncio.sleep(0.1)  # 0.1초 간격

    # 5개 워커 동시 실행
    start = time.time()
    await asyncio.gather(*[worker() for _ in range(5)])
    elapsed = time.time() - start

    # 검증: 1초당 정확히 2개만 성공해야 함
    expected_success = int(elapsed) * 2
    tolerance = 1  # ±1 허용

    assert abs(success_count - expected_success) <= tolerance, \
        f"Expected ~{expected_success}, got {success_count}"

    # Rate limit violation 없음
    assert success_count <= int(elapsed) * 2
```

**실행 시간:** 10초

---

### 7.4 Database Query Performance Test

**tests/performance/test_db_query_performance.py:**

```python
import pytest
import time
from sqlalchemy import select
from app.models import ProductRegistration, State

@pytest.mark.performance
@pytest.mark.asyncio
async def test_pending_queue_query_performance(db):
    """PENDING 큐 조회 성능 (10,000개 중 100개 PENDING)"""
    # Create 10,000 records (100 PENDING, 9,900 COMPLETED)
    registrations = []
    for i in range(100):
        registrations.append(ProductRegistration(
            product_id=f"uuid-{i}",
            state=State.PENDING
        ))
    for i in range(100, 10000):
        registrations.append(ProductRegistration(
            product_id=f"uuid-{i}",
            state=State.COMPLETED
        ))
    db.add_all(registrations)
    await db.commit()

    # Query PENDING items
    stmt = select(ProductRegistration).where(
        ProductRegistration.state == State.PENDING
    ).limit(20)

    start = time.time()
    result = await db.execute(stmt)
    pending_items = result.scalars().all()
    elapsed = time.time() - start

    assert len(pending_items) == 20
    assert elapsed < 0.05, f"Query too slow: {elapsed}s (expected < 50ms)"
```

---

## 8. Test Data Management

### 8.1 Fixtures & Seed Data

**tests/fixtures/seed_data.py:**

```python
from app.models import Product, CategoryMapping

# Sample products from Domeggook
SAMPLE_PRODUCTS = [
    {
        "domeggook_item_id": "DG-001",
        "name": "면 반팔 티셔츠",
        "price": 15000,
        "category": "패션의류",
        "images": [
            "https://domeggook.com/images/001_1.jpg",
            "https://domeggook.com/images/001_2.jpg"
        ],
        "options": ["블랙-S", "블랙-M", "화이트-S", "화이트-M"]
    },
    {
        "domeggook_item_id": "DG-002",
        "name": "청바지",
        "price": 35000,
        "category": "패션의류",
        "images": ["https://domeggook.com/images/002.jpg"],
        "options": ["28", "29", "30", "31", "32"]
    }
]

# Category mappings
CATEGORY_MAPPINGS = [
    {
        "domeggook_category": "패션의류",
        "naver_leaf_category_id": "50000156",
        "required_attributes": {
            "제조일자": {"type": "date", "required": True},
            "세탁방법": {"type": "string", "required": True}
        },
        "default_attributes": {
            "세탁방법": "일반세탁"
        }
    },
    {
        "domeggook_category": "생활용품",
        "naver_leaf_category_id": "50000789",
        "required_attributes": {
            "제조국": {"type": "string", "required": True}
        }
    }
]

async def seed_test_data(db):
    """테스트 DB에 seed data 삽입"""
    for product_data in SAMPLE_PRODUCTS:
        product = Product(**product_data)
        db.add(product)

    for mapping_data in CATEGORY_MAPPINGS:
        mapping = CategoryMapping(**mapping_data)
        db.add(mapping)

    await db.commit()
```

---

### 8.2 VCR.py Cassette Management

**VCR Cassette 디렉토리 구조:**

```
tests/fixtures/vcr_cassettes/
├── domeggook/
│   ├── get_item_list.yaml
│   ├── get_item_view.yaml
│   ├── rate_limit_429.yaml
│   └── encoding_euc_kr.yaml
├── naver/
│   ├── upload_image.yaml
│   ├── register_product.yaml
│   ├── rate_limit_429.yaml
│   └── oauth_token.yaml
└── README.md
```

**Cassette 재생성 (API 변경 시):**

```bash
# 기존 cassette 삭제 후 재녹화
rm -rf tests/fixtures/vcr_cassettes/domeggook/get_item_list.yaml
VCR_RECORD_MODE=all pytest tests/integration/api/test_domeggook_integration.py::test_get_item_list
```

---

## 9. Mocking Strategy

### 9.1 Mocking Hierarchy

```
Real (Production)
    ↓
VCR.py (Integration Tests)
    ↓
AsyncMock (Unit Tests)
    ↓
Fake (In-memory, for E2E)
```

### 9.2 Fake Implementations

**tests/fakes/fake_naver_client.py:**

```python
from typing import Dict, Any

class FakeNaverClient:
    """네이버 API Fake 구현 (테스트용)"""

    def __init__(self):
        self.uploaded_images = []
        self.registered_products = []
        self.call_count = 0

    async def upload_image(self, image_data: bytes) -> Dict[str, Any]:
        """이미지 업로드 (fake)"""
        self.call_count += 1
        fake_url = f"https://fake-cdn.naver.com/image_{self.call_count}.jpg"
        self.uploaded_images.append(fake_url)
        return {"success": True, "image_url": fake_url}

    async def register_product(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """상품 등록 (fake)"""
        self.call_count += 1
        fake_product_id = f"NAVER-{self.call_count:05d}"
        self.registered_products.append({
            "product_id": fake_product_id,
            "data": data
        })
        return {"success": True, "originProductNo": fake_product_id}

    def reset(self):
        """테스트 간 상태 초기화"""
        self.uploaded_images.clear()
        self.registered_products.clear()
        self.call_count = 0
```

**사용 예시:**

```python
@pytest.fixture
def fake_naver_client():
    client = FakeNaverClient()
    yield client
    client.reset()

def test_registration_uses_fake_client(fake_naver_client):
    """Fake client 사용 테스트"""
    result = await fake_naver_client.register_product({"name": "테스트"})

    assert result["success"] is True
    assert len(fake_naver_client.registered_products) == 1
```

---

## 10. CI/CD Integration

### 10.1 GitHub Actions Test Workflow

**기존 .github/workflows/ci-cd.yml에 통합:**

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # ===== Unit & Integration Tests =====
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: storebridge_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run Unit Tests
        run: |
          pytest tests/unit/ \
            --cov=app \
            --cov-report=xml \
            --cov-report=term \
            --junitxml=reports/unit-tests.xml

      - name: Run Integration Tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/storebridge_test
          REDIS_URL: redis://localhost:6379/1
          VCR_RECORD_MODE: none  # Use existing cassettes
        run: |
          pytest tests/integration/ \
            --junitxml=reports/integration-tests.xml

      - name: Upload Coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          fail_ci_if_error: true

      - name: Check Coverage Threshold
        run: |
          coverage report --fail-under=85

  # ===== E2E Tests (only on staging) =====
  e2e-test:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    needs: [test]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Run E2E Tests against Staging
        env:
          API_BASE_URL: https://staging.storebridge.com
          DOMEGGOOK_API_KEY: ${{ secrets.DOMEGGOOK_SANDBOX_KEY }}
          NAVER_CLIENT_ID: ${{ secrets.NAVER_STAGING_CLIENT_ID }}
          NAVER_CLIENT_SECRET: ${{ secrets.NAVER_STAGING_SECRET }}
        run: |
          pytest tests/e2e/ \
            --junitxml=reports/e2e-tests.xml \
            -v

  # ===== Performance Tests (weekly schedule) =====
  performance-test:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'  # Cron trigger

    steps:
      - uses: actions/checkout@v4

      - name: Install Locust
        run: pip install locust

      - name: Run Load Test
        run: |
          locust -f tests/performance/locustfile.py \
            --host https://staging.storebridge.com \
            --users 100 \
            --spawn-rate 10 \
            --run-time 5m \
            --html reports/load_test_report.html \
            --headless

      - name: Upload Load Test Report
        uses: actions/upload-artifact@v3
        with:
          name: load-test-report
          path: reports/load_test_report.html
```

---

### 10.2 Pre-commit Hooks

**설치:**

```bash
pip install pre-commit
pre-commit install
```

**.pre-commit-config.yaml:**

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: local
    hooks:
      - id: pytest-unit
        name: Run Unit Tests
        entry: pytest tests/unit/ --maxfail=1
        language: system
        pass_filenames: false
        always_run: true
```

---

### 10.3 Test Reporting

**Pytest 설정** (pytest.ini):

```ini
[pytest]
minversion = 7.0
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (DB, Redis, APIs with VCR)
    e2e: End-to-end tests (full flow, slow)
    performance: Performance and load tests

# Coverage
addopts =
    --strict-markers
    --tb=short
    --cov=app
    --cov-report=html:reports/coverage
    --cov-report=term-missing
    --junitxml=reports/junit.xml

# Asyncio
asyncio_mode = auto

# Logging
log_cli = true
log_cli_level = INFO
```

**실행 명령:**

```bash
# 모든 테스트 실행
pytest

# Unit tests only (빠른 피드백)
pytest -m unit

# Integration tests only
pytest -m integration

# E2E tests only
pytest -m e2e

# Coverage report 생성
pytest --cov=app --cov-report=html
open reports/coverage/index.html
```

---

## 11. Test Execution Guide

### 11.1 로컬 개발 환경

**Step 1: 환경 설정**

```bash
# 1. Docker Compose로 PostgreSQL, Redis 시작
docker-compose up -d postgres redis

# 2. 테스트 DB 생성 및 마이그레이션
export DATABASE_URL=postgresql://test:test@localhost:5432/storebridge_test
alembic upgrade head

# 3. Seed data 삽입
python -m tests.fixtures.seed_data
```

**Step 2: 테스트 실행**

```bash
# Unit tests (가장 빠름 - 1초 이내)
pytest -m unit -v

# Integration tests (VCR.py 사용 - 10초 이내)
pytest -m integration -v

# 특정 테스트 파일만
pytest tests/unit/services/test_rate_limiter.py -v

# 특정 테스트 함수만
pytest tests/unit/services/test_rate_limiter.py::TestNaverRateLimiter::test_acquire_success -v

# 실패 시 즉시 중단 (--maxfail=1)
pytest -m unit --maxfail=1

# 병렬 실행 (pytest-xdist)
pytest -m unit -n auto  # CPU 코어 수만큼 병렬
```

---

### 11.2 CI 환경 (GitHub Actions)

**트리거:**

1. **Push to main/develop**: Unit + Integration tests
2. **Pull Request**: Unit + Integration tests + Coverage check
3. **Push to develop**: E2E tests (staging 환경)
4. **Weekly schedule**: Performance tests (Locust)

**테스트 결과 확인:**

```bash
# GitHub Actions 탭에서 확인
# - ✅ test job: Unit + Integration
# - ✅ e2e-test job: E2E (staging only)
# - 📊 Coverage report: Codecov badge
```

---

### 11.3 Staging 환경

**Real API 테스트 (VCR 없이):**

```bash
# Staging에서 실제 API 호출 테스트
export ENVIRONMENT=staging
export VCR_RECORD_MODE=none  # VCR 비활성화
export DOMEGGOOK_API_KEY=$DOMEGGOOK_SANDBOX_KEY
export NAVER_CLIENT_ID=$NAVER_STAGING_CLIENT_ID
export NAVER_CLIENT_SECRET=$NAVER_STAGING_SECRET

pytest tests/integration/api/ -v
```

---

## 12. Appendix: Sample Test Cases

### 12.1 Test Case Template

| ID | Test Name | Priority | Type | Precondition | Steps | Expected Result |
|----|-----------|----------|------|--------------|-------|-----------------|
| TC-001 | Rate Limiter blocks 3rd request | P0 | Unit | Rate limit = 2 TPS | 1. Call acquire() 3 times in 1 sec | 1st=True, 2nd=True, 3rd=False |
| TC-002 | Option Mapper parses 2D combo | P1 | Unit | Raw options = ["블랙-S", "화이트-M"] | 1. Call parse() | type=COMBINATION, dimensions=[색상, 사이즈] |
| TC-003 | Naver API upload image | P0 | Integration | Valid image data | 1. Call upload_image() | Returns CDN URL |
| TC-004 | Complete registration flow | P0 | E2E | Job created | 1. Create job<br>2. Wait for completion | Job status=COMPLETED |
| TC-005 | Rate limiter under load | P0 | Performance | 5 workers, 10 req/sec each | 1. Run 5 workers concurrently | Max 2 TPS enforced |

---

### 12.2 Test Coverage Report 예시

**목표 Coverage (단위별):**

```
app/
├── services/
│   ├── rate_limiter.py          ✅ 95% (P0 - critical)
│   ├── option_mapper.py         ✅ 90% (P1 - high)
│   └── image_processor.py       ✅ 85% (P1 - high)
├── validators/
│   ├── product_validator.py     ✅ 85%
│   ├── category_validator.py    ✅ 80%
│   └── forbidden_word_validator.py ✅ 90%
├── workflows/
│   └── registration_workflow.py ✅ 90% (State machine critical)
├── connectors/
│   ├── domeggook_client.py      ⚠️  70% (외부 API 의존)
│   └── naver_client.py          ⚠️  70% (외부 API 의존)
└── transformers/
    └── product_transformer.py   ✅ 85%

Overall Coverage: 85.3% ✅ (Target: 85%)
```

---

## 13. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-16 | Initial test plan (Unit, Integration, E2E, Performance) |

---

**문서 끝 - StoreBridge Test Plan v1.0.0**
