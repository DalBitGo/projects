# 아키텍처 개선사항 상세 설계

> ARCHITECTURE.md 리뷰 결과 발견된 문제점 해결 방안

**작성일**: 2025-10-16
**버전**: 1.1

---

## 목차

1. [P0: Race Condition in Rate Limiter](#p0-race-condition-in-rate-limiter)
2. [P1: 옵션 매핑 로직 강화](#p1-옵션-매핑-로직-강화)
3. [P1: 이미지 병렬 처리 전략](#p1-이미지-병렬-처리-전략)
4. [P2: 캐시 무효화 전략](#p2-캐시-무효화-전략)
5. [P2: 가격 동기화 Delta 감지](#p2-가격-동기화-delta-감지)
6. [P3: Prometheus 메트릭 상세화](#p3-prometheus-메트릭-상세화)

---

## P0: Race Condition in Rate Limiter

### 문제점

```python
# 현재 코드 (ARCHITECTURE.md)
current_count = await self.redis.get(key)
current_count = int(current_count) if current_count else 0

if current_count < self.max_tps:
    await self.redis.incr(key)  # 🚨 Race Condition!
    return True
```

**시나리오:**
```
시간 T:
  Worker A: GET → count=1
  Worker B: GET → count=1
  Worker A: CHECK (1 < 2) → OK
  Worker B: CHECK (1 < 2) → OK
  Worker A: INCR → count=2
  Worker B: INCR → count=3  # 🚨 초과!
```

### 해결책: Lua Script로 원자성 보장

#### 개선된 코드

```python
# app/connectors/rate_limiters.py

import time
import asyncio
from typing import Optional
import aioredis
from aioredis.client import Redis

class TokenBucketRateLimiter:
    """
    네이버 커머스 API Rate Limit 준수
    - TPS: 2
    - Burst Max: 다음 1초 선빌림 (연속 불가)
    - 원자성: Lua Script
    """

    # Lua Script: 원자적으로 체크 & 증가
    LUA_ACQUIRE = """
    local key = KEYS[1]
    local max_tps = tonumber(ARGV[1])
    local ttl = tonumber(ARGV[2])

    local current = redis.call('GET', key)

    if not current then
        current = 0
    else
        current = tonumber(current)
    end

    if current < max_tps then
        redis.call('INCR', key)
        redis.call('EXPIRE', key, ttl)
        return 1  -- 성공
    else
        return 0  -- 실패
    end
    """

    # Burst Max용 Lua Script
    LUA_ACQUIRE_BURST = """
    local current_key = KEYS[1]
    local next_key = KEYS[2]
    local burst_flag_key = KEYS[3]
    local max_tps = tonumber(ARGV[1])
    local ttl = tonumber(ARGV[2])

    -- 현재 초 체크
    local current = redis.call('GET', current_key)
    if not current then
        current = 0
    else
        current = tonumber(current)
    end

    if current < max_tps then
        redis.call('INCR', current_key)
        redis.call('EXPIRE', current_key, ttl)
        return 1  -- 일반 성공
    end

    -- Burst Max 체크
    local burst_used = redis.call('GET', burst_flag_key)
    if burst_used then
        return 0  -- Burst 이미 사용됨
    end

    local next = redis.call('GET', next_key)
    if not next then
        next = 0
    else
        next = tonumber(next)
    end

    if next == 0 then
        redis.call('INCR', next_key)
        redis.call('EXPIRE', next_key, ttl)
        redis.call('SETEX', burst_flag_key, ttl, '1')
        return 2  -- Burst 성공
    end

    return 0  -- 실패
    """

    def __init__(
        self,
        redis_url: str,
        max_tps: int = 2,
        burst_enabled: bool = True
    ):
        self.redis: Optional[Redis] = None
        self.redis_url = redis_url
        self.max_tps = max_tps
        self.burst_enabled = burst_enabled
        self.ttl = 2  # 키 TTL (초)

    async def connect(self):
        """Redis 연결 초기화"""
        if not self.redis:
            self.redis = await aioredis.from_url(self.redis_url)

    async def acquire(self, timeout: Optional[float] = None) -> bool:
        """
        토큰 획득 시도

        Args:
            timeout: 최대 대기 시간 (초). None이면 즉시 실패.

        Returns:
            True: 토큰 획득 성공
            False: timeout 내 획득 실패

        Raises:
            RateLimitExceeded: timeout 없이 즉시 실패
        """
        await self.connect()
        start_time = time.time()

        while True:
            now = time.time()
            current_second = int(now)

            # 1차 시도: 일반 획득
            result = await self._try_acquire_normal(current_second)
            if result:
                return True

            # 2차 시도: Burst Max
            if self.burst_enabled:
                result = await self._try_acquire_burst(current_second)
                if result:
                    return True

            # 실패 처리
            if timeout is None:
                raise RateLimitExceeded(
                    f"Rate limit exceeded: {self.max_tps} TPS"
                )

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                return False

            # 다음 초까지 대기
            wait_time = 1 - (now - current_second)
            await asyncio.sleep(max(wait_time, 0.1))

    async def _try_acquire_normal(self, current_second: int) -> bool:
        """일반 토큰 획득 시도"""
        key = f'naver:ratelimit:{current_second}'

        result = await self.redis.eval(
            self.LUA_ACQUIRE,
            1,  # key 개수
            key,
            self.max_tps,
            self.ttl
        )

        return result == 1

    async def _try_acquire_burst(self, current_second: int) -> bool:
        """Burst Max 토큰 획득 시도"""
        current_key = f'naver:ratelimit:{current_second}'
        next_key = f'naver:ratelimit:{current_second + 1}'
        burst_flag_key = f'naver:burst_used:{current_second}'

        result = await self.redis.eval(
            self.LUA_ACQUIRE_BURST,
            3,  # key 개수
            current_key,
            next_key,
            burst_flag_key,
            self.max_tps,
            self.ttl
        )

        return result > 0

    async def get_remaining(self) -> int:
        """현재 초의 남은 토큰 수 (디버깅용)"""
        await self.connect()
        current_second = int(time.time())
        key = f'naver:ratelimit:{current_second}'

        current = await self.redis.get(key)
        current = int(current) if current else 0

        return max(0, self.max_tps - current)

    async def close(self):
        """Redis 연결 종료"""
        if self.redis:
            await self.redis.close()


class RateLimitExceeded(Exception):
    """Rate Limit 초과 예외"""
    pass
```

#### 테스트 코드

```python
# tests/test_rate_limiter.py

import pytest
import asyncio
from app.connectors.rate_limiters import TokenBucketRateLimiter

@pytest.mark.asyncio
async def test_rate_limiter_allows_max_tps():
    """최대 TPS까지 허용"""
    limiter = TokenBucketRateLimiter(
        redis_url='redis://localhost:6379',
        max_tps=2
    )

    # 첫 2개 성공
    assert await limiter.acquire() == True
    assert await limiter.acquire() == True

    # 3번째 실패
    with pytest.raises(Exception):  # RateLimitExceeded
        await limiter.acquire(timeout=None)

    await limiter.close()


@pytest.mark.asyncio
async def test_rate_limiter_resets_per_second():
    """매 초마다 리셋"""
    limiter = TokenBucketRateLimiter(
        redis_url='redis://localhost:6379',
        max_tps=2
    )

    # 2개 소진
    await limiter.acquire()
    await limiter.acquire()

    # 1초 대기
    await asyncio.sleep(1)

    # 다시 2개 가능
    assert await limiter.acquire() == True
    assert await limiter.acquire() == True

    await limiter.close()


@pytest.mark.asyncio
async def test_rate_limiter_concurrent_workers():
    """여러 워커가 동시 호출 시 Race Condition 없음"""
    limiter = TokenBucketRateLimiter(
        redis_url='redis://localhost:6379',
        max_tps=10
    )

    success_count = 0
    fail_count = 0

    async def worker():
        nonlocal success_count, fail_count
        try:
            if await limiter.acquire(timeout=None):
                success_count += 1
        except Exception:
            fail_count += 1

    # 20개 워커 동시 실행
    await asyncio.gather(*[worker() for _ in range(20)])

    # 정확히 10개만 성공
    assert success_count == 10
    assert fail_count == 10

    await limiter.close()
```

---

## P1: 옵션 매핑 로직 강화

### 문제점

도매꾹과 네이버의 옵션 구조가 다름:

```
도매꾹:
  ["블랙-S", "블랙-M", "화이트-S", "화이트-M"]
  → 단순 문자열 배열

네이버:
  {
    "type": "COMBINATION",
    "dimensions": [
      {"name": "색상", "values": ["블랙", "화이트"]},
      {"name": "사이즈", "values": ["S", "M"]}
    ],
    "combinations": [
      {"values": ["블랙", "S"], "price": 0, "stock": 10},
      ...
    ]
  }
  → 구조화된 객체
```

### 해결책: 옵션 파서 & 매퍼

#### 옵션 타입 분류

```python
from enum import Enum

class OptionType(str, Enum):
    """네이버 옵션 타입"""
    NONE = "NONE"              # 옵션 없음
    SIMPLE = "SIMPLE"          # 단일 옵션 (색상만)
    COMBINATION = "COMBINATION"  # 조합 옵션 (색상 × 사이즈)
    INDEPENDENT = "INDEPENDENT"  # 독립 옵션 (추가 구성품)
```

#### 옵션 파서

```python
# app/transformers/option_mapper.py

import re
from typing import List, Dict, Any, Optional, Tuple
from itertools import product

class OptionMapper:
    """도매꾹 → 네이버 옵션 변환"""

    # 옵션명 정규화 매핑
    OPTION_NAME_MAP = {
        '색상': ['색상', '색깔', '컬러', 'color', 'COLOR'],
        '사이즈': ['사이즈', '크기', '치수', 'size', 'SIZE', 'Size'],
        '길이': ['길이', 'length', 'LENGTH'],
        '두께': ['두께', 'thickness'],
    }

    # 구분자 후보
    SEPARATORS = ['-', '/', '_', ' ', ':']

    def parse(self, raw_options: List[str]) -> Dict[str, Any]:
        """
        도매꾹 옵션을 네이버 옵션 구조로 변환

        Args:
            raw_options: ["블랙-S", "블랙-M", "화이트-S", "화이트-M"]

        Returns:
            {
                "type": "COMBINATION",
                "dimensions": [...],
                "combinations": [...]
            }
        """
        if not raw_options or len(raw_options) == 0:
            return {"type": "NONE"}

        # 1. 구분자 탐지
        separator = self._detect_separator(raw_options)

        if separator is None:
            # 구분자 없음 → 단일 옵션
            return self._parse_simple(raw_options)

        # 2. 값 분리
        split_options = [opt.split(separator) for opt in raw_options]

        # 3. 차원 수 확인
        dimensions_count = len(split_options[0])

        if dimensions_count == 1:
            return self._parse_simple(raw_options)
        else:
            return self._parse_combination(split_options)

    def _detect_separator(self, options: List[str]) -> Optional[str]:
        """구분자 탐지"""
        for sep in self.SEPARATORS:
            # 모든 옵션에 해당 구분자가 있고, 일관된 개수인지 확인
            split_counts = [opt.count(sep) for opt in options]

            if all(count > 0 for count in split_counts) and \
               len(set(split_counts)) == 1:
                return sep

        return None

    def _parse_simple(self, options: List[str]) -> Dict[str, Any]:
        """단일 옵션 파싱"""
        # 옵션명 추론 (대부분 "색상")
        option_name = self._infer_option_name(options)

        return {
            "type": "SIMPLE",
            "dimensions": [
                {
                    "name": option_name,
                    "values": options
                }
            ]
        }

    def _parse_combination(self, split_options: List[List[str]]) -> Dict[str, Any]:
        """조합 옵션 파싱"""
        # 1. 각 차원별 고유값 추출
        dimensions_count = len(split_options[0])
        dimension_values = [set() for _ in range(dimensions_count)]

        for option in split_options:
            for i, value in enumerate(option):
                dimension_values[i].add(value.strip())

        # 2. 차원별 이름 추론
        dimensions = []
        for i, values in enumerate(dimension_values):
            name = self._infer_dimension_name(i, values)
            dimensions.append({
                "name": name,
                "values": sorted(list(values))
            })

        # 3. 조합 생성 (카티션 프로덕트)
        combinations = []
        all_combinations = product(*[d['values'] for d in dimensions])

        for combo in all_combinations:
            combinations.append({
                "values": list(combo),
                "price": 0,  # 기본값 (추후 가격 차이 반영)
                "stock": 999  # 기본값 (추후 실제 재고 반영)
            })

        return {
            "type": "COMBINATION",
            "dimensions": dimensions,
            "combinations": combinations
        }

    def _infer_option_name(self, values: List[str]) -> str:
        """옵션명 추론 (단일 옵션)"""
        # 색상 관련 키워드 체크
        color_keywords = ['블랙', '화이트', '레드', '블루', '그레이', '네이비']
        if any(keyword in ''.join(values) for keyword in color_keywords):
            return '색상'

        # 사이즈 관련 키워드 체크
        size_keywords = ['S', 'M', 'L', 'XL', 'FREE']
        if any(keyword in ''.join(values).upper() for keyword in size_keywords):
            return '사이즈'

        # 기본값
        return '옵션'

    def _infer_dimension_name(self, index: int, values: set) -> str:
        """차원별 옵션명 추론 (조합 옵션)"""
        values_str = ''.join(values).upper()

        # 색상 체크
        color_keywords = ['블랙', '화이트', '레드', '블루', 'BLACK', 'WHITE']
        if any(keyword.upper() in values_str for keyword in color_keywords):
            return '색상'

        # 사이즈 체크
        size_keywords = ['S', 'M', 'L', 'XL', 'FREE']
        if any(keyword in values_str for keyword in size_keywords):
            return '사이즈'

        # 숫자만 있으면 "길이" or "두께"
        if all(v.isdigit() for v in values):
            return '길이' if index == 1 else '두께'

        # 기본값
        return f'옵션{index + 1}'

    def normalize_option_name(self, name: str) -> str:
        """옵션명 정규화"""
        for standard, aliases in self.OPTION_NAME_MAP.items():
            if name in aliases:
                return standard
        return name
```

#### 테스트 케이스

```python
# tests/test_option_mapper.py

import pytest
from app.transformers.option_mapper import OptionMapper

def test_parse_no_options():
    """옵션 없는 상품"""
    mapper = OptionMapper()
    result = mapper.parse([])
    assert result['type'] == 'NONE'


def test_parse_simple_option():
    """단일 옵션 (색상만)"""
    mapper = OptionMapper()
    result = mapper.parse(['블랙', '화이트', '그레이'])

    assert result['type'] == 'SIMPLE'
    assert result['dimensions'][0]['name'] == '색상'
    assert set(result['dimensions'][0]['values']) == {'블랙', '화이트', '그레이'}


def test_parse_combination_option():
    """조합 옵션 (색상 × 사이즈)"""
    mapper = OptionMapper()
    result = mapper.parse(['블랙-S', '블랙-M', '화이트-S', '화이트-M'])

    assert result['type'] == 'COMBINATION'
    assert len(result['dimensions']) == 2

    # 차원 확인
    assert result['dimensions'][0]['name'] == '색상'
    assert set(result['dimensions'][0]['values']) == {'블랙', '화이트'}

    assert result['dimensions'][1]['name'] == '사이즈'
    assert set(result['dimensions'][1]['values']) == {'S', 'M'}

    # 조합 확인 (2×2 = 4개)
    assert len(result['combinations']) == 4


def test_parse_three_dimension_combination():
    """3차원 조합 (색상 × 사이즈 × 길이)"""
    mapper = OptionMapper()
    result = mapper.parse([
        '블랙-S-90', '블랙-S-100',
        '블랙-M-90', '블랙-M-100',
        '화이트-S-90', '화이트-S-100',
        '화이트-M-90', '화이트-M-100'
    ])

    assert result['type'] == 'COMBINATION'
    assert len(result['dimensions']) == 3
    assert len(result['combinations']) == 8  # 2×2×2


def test_detect_separator():
    """다양한 구분자 탐지"""
    mapper = OptionMapper()

    # 하이픈
    assert mapper._detect_separator(['블랙-S', '화이트-M']) == '-'

    # 슬래시
    assert mapper._detect_separator(['블랙/S', '화이트/M']) == '/'

    # 언더스코어
    assert mapper._detect_separator(['블랙_S', '화이트_M']) == '_'

    # 구분자 없음
    assert mapper._detect_separator(['블랙', '화이트']) is None
```

---

## P1: 이미지 병렬 처리 전략

### 문제점

상품당 10~20장 이미지를 순차 처리 시 병목:

```python
# 순차 처리 (느림)
for img_url in product.images:
    data = await download(img_url)        # I/O
    resized = resize(data)                # CPU
    await upload_to_s3(resized)           # I/O
    await upload_to_naver(resized)        # I/O + Rate Limit
```

### 해결책: 단계별 병렬 처리

```python
# app/services/image_pipeline.py

import asyncio
import hashlib
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from PIL import Image
import httpx

class ImagePipeline:
    """이미지 다운로드, 변환, 업로드 파이프라인"""

    def __init__(
        self,
        s3_client,
        naver_client,
        max_images: int = 10,
        min_width: int = 500,
        min_height: int = 500,
        max_size_mb: int = 12
    ):
        self.s3_client = s3_client
        self.naver_client = naver_client
        self.max_images = max_images
        self.min_width = min_width
        self.min_height = min_height
        self.max_size_mb = max_size_mb
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def process(
        self,
        image_urls: List[str],
        product_id: str
    ) -> List[str]:
        """
        이미지 파이프라인 실행

        Args:
            image_urls: 원본 이미지 URL 목록
            product_id: 상품 ID (S3 경로용)

        Returns:
            네이버 이미지 URL 목록
        """
        # 1단계: 병렬 다운로드 (I/O bound)
        print(f"[Image Pipeline] 1/4 병렬 다운로드 중... ({len(image_urls[:self.max_images])}장)")
        images_data = await self._download_images(image_urls[:self.max_images])

        # 2단계: 병렬 변환 (CPU bound)
        print(f"[Image Pipeline] 2/4 병렬 변환 중... ({len(images_data)}장)")
        processed_images = await self._process_images(images_data)

        # 3단계: 중복 제거 (해시 기반)
        print(f"[Image Pipeline] 3/4 중복 제거 중...")
        unique_images = self._deduplicate_images(processed_images)
        print(f"[Image Pipeline] 중복 제거 완료: {len(processed_images)} → {len(unique_images)}장")

        # 4단계: S3 업로드 (백업용, 병렬)
        print(f"[Image Pipeline] 4/4 S3 업로드 중...")
        s3_urls = await self._upload_to_s3(unique_images, product_id)

        # 5단계: 네이버 업로드는 Rate Limiter 통과해야 하므로 순차
        # (네이버 API에서 S3 URL 직접 등록 가능하면 이 단계 생략)
        print(f"[Image Pipeline] 완료: {len(s3_urls)}장")
        return s3_urls

    async def _download_images(self, urls: List[str]) -> List[bytes]:
        """병렬 다운로드"""
        async def download_one(url: str) -> Optional[bytes]:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    return response.content
            except Exception as e:
                print(f"[Image Pipeline] 다운로드 실패: {url} - {e}")
                return None

        results = await asyncio.gather(*[download_one(url) for url in urls])
        return [data for data in results if data is not None]

    async def _process_images(self, images_data: List[bytes]) -> List[bytes]:
        """병렬 이미지 변환 (CPU bound → ThreadPoolExecutor)"""
        loop = asyncio.get_event_loop()

        tasks = [
            loop.run_in_executor(self.executor, self._process_one_image, data)
            for data in images_data
        ]

        results = await asyncio.gather(*tasks)
        return [img for img in results if img is not None]

    def _process_one_image(self, data: bytes) -> Optional[bytes]:
        """단일 이미지 변환 (동기 함수)"""
        try:
            img = Image.open(BytesIO(data))

            # 1. 규격 검증
            if img.width < self.min_width or img.height < self.min_height:
                print(f"[Image Pipeline] 규격 미달: {img.width}x{img.height}")
                return None

            # 2. 리사이즈 (최대 1200px, 비율 유지)
            max_dimension = 1200
            if img.width > max_dimension or img.height > max_dimension:
                ratio = min(max_dimension / img.width, max_dimension / img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # 3. WebP 변환 (용량 절감)
            output = BytesIO()
            img.save(output, format='WEBP', quality=85)
            output.seek(0)

            result = output.read()

            # 4. 용량 체크
            size_mb = len(result) / (1024 * 1024)
            if size_mb > self.max_size_mb:
                print(f"[Image Pipeline] 용량 초과: {size_mb:.2f}MB")
                return None

            return result

        except Exception as e:
            print(f"[Image Pipeline] 변환 실패: {e}")
            return None

    def _deduplicate_images(self, images: List[bytes]) -> List[bytes]:
        """중복 이미지 제거 (해시 기반)"""
        seen_hashes = set()
        unique_images = []

        for img_data in images:
            img_hash = hashlib.md5(img_data).hexdigest()

            if img_hash not in seen_hashes:
                seen_hashes.add(img_hash)
                unique_images.append(img_data)

        return unique_images

    async def _upload_to_s3(
        self,
        images: List[bytes],
        product_id: str
    ) -> List[str]:
        """S3 병렬 업로드"""
        async def upload_one(img_data: bytes, index: int) -> Optional[str]:
            try:
                filename = f"{product_id}_{index}.webp"
                url = await self.s3_client.upload(
                    data=img_data,
                    filename=filename,
                    content_type='image/webp'
                )
                return url
            except Exception as e:
                print(f"[Image Pipeline] S3 업로드 실패: {e}")
                return None

        results = await asyncio.gather(*[
            upload_one(img, i) for i, img in enumerate(images)
        ])

        return [url for url in results if url is not None]
```

#### 성능 비교

```python
# 벤치마크
import time

# 순차 처리
start = time.time()
for url in image_urls[:10]:
    data = await download(url)      # 평균 0.5초
    resized = resize(data)          # 평균 0.2초
    await upload_s3(resized)        # 평균 0.3초
# 총: 10초

# 병렬 처리
start = time.time()
pipeline = ImagePipeline(...)
await pipeline.process(image_urls[:10], product_id)
# 총: ~2초 (5배 빠름!)
```

---

## P2: 캐시 무효화 전략

### 문제점

TTL만 있고 명시적 무효화 없음:

```python
@cache(ttl=3600)  # 1시간
async def get_item_view(item_id: str):
    ...
```

→ 도매꾹에서 가격 변경 시 1시간 동안 구 데이터 사용

### 해결책: Cache Manager

```python
# app/utils/cache.py

from typing import Optional, Callable, Any
import functools
import hashlib
import json
import aioredis

class CacheManager:
    """Redis 캐시 관리자"""

    def __init__(self, redis_url: str, prefix: str = 'cache'):
        self.redis_url = redis_url
        self.prefix = prefix
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self):
        if not self.redis:
            self.redis = await aioredis.from_url(self.redis_url)

    def cache(self, ttl: int = 3600, key_builder: Optional[Callable] = None):
        """캐시 데코레이터"""
        def decorator(func: Callable):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                await self.connect()

                # 캐시 키 생성
                cache_key = self._build_cache_key(func, args, kwargs, key_builder)

                # 캐시 조회
                cached = await self.redis.get(cache_key)
                if cached:
                    return json.loads(cached)

                # 캐시 미스: 실제 함수 호출
                result = await func(*args, **kwargs)

                # 캐시 저장
                await self.redis.setex(
                    cache_key,
                    ttl,
                    json.dumps(result, ensure_ascii=False)
                )

                return result

            # 무효화 메서드 추가
            wrapper.invalidate = functools.partial(
                self._invalidate_pattern,
                func.__name__
            )

            return wrapper
        return decorator

    def _build_cache_key(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        key_builder: Optional[Callable]
    ) -> str:
        """캐시 키 생성"""
        if key_builder:
            key_suffix = key_builder(*args, **kwargs)
        else:
            # 기본: 함수명 + 인자 해시
            args_str = json.dumps(
                {'args': args, 'kwargs': kwargs},
                sort_keys=True,
                ensure_ascii=False
            )
            args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
            key_suffix = args_hash

        return f'{self.prefix}:{func.__name__}:{key_suffix}'

    async def invalidate(self, key: str):
        """특정 키 무효화"""
        await self.connect()
        await self.redis.delete(key)

    async def invalidate_pattern(self, pattern: str):
        """패턴 매칭 키 일괄 무효화"""
        await self.connect()
        full_pattern = f'{self.prefix}:{pattern}'

        cursor = 0
        deleted_count = 0

        while True:
            cursor, keys = await self.redis.scan(
                cursor=cursor,
                match=full_pattern,
                count=100
            )

            if keys:
                await self.redis.delete(*keys)
                deleted_count += len(keys)

            if cursor == 0:
                break

        return deleted_count

    async def invalidate_product(self, item_id: str):
        """특정 상품 관련 캐시 전체 무효화"""
        patterns = [
            f'get_item_view:*{item_id}*',
            f'get_item_list:*',  # 목록에도 포함될 수 있음
        ]

        total_deleted = 0
        for pattern in patterns:
            count = await self.invalidate_pattern(pattern)
            total_deleted += count

        return total_deleted

    async def invalidate_category(self, category_id: str):
        """카테고리 관련 캐시 무효화"""
        patterns = [
            f'get_category_list:*',
            f'get_cat:*{category_id}*',
        ]

        total_deleted = 0
        for pattern in patterns:
            count = await self.invalidate_pattern(pattern)
            total_deleted += count

        return total_deleted


# 사용 예시
cache_manager = CacheManager(redis_url='redis://localhost:6379')

@cache_manager.cache(ttl=3600)
async def get_item_view(item_id: str):
    # 실제 API 호출
    ...

# 명시적 무효화
await cache_manager.invalidate_product('12345')
```

---

## P2: 가격 동기화 Delta 감지

### 문제점

전체 상품을 주기적으로 동기화 → 비효율적

### 해결책: 변경 감지 + 이벤트 기반

```python
# app/workers/sync.py

from datetime import datetime, timedelta
from sqlalchemy import select
from app.models.product import Product, ProductRegistration

async def detect_price_changes():
    """가격 변경 감지 (Delta)"""

    # 1시간 이내 업데이트된 상품만
    cutoff_time = datetime.now() - timedelta(hours=1)

    stmt = select(Product).where(
        Product.updated_at > cutoff_time
    )

    products = await db.execute(stmt)

    changed_products = []

    for product in products.scalars():
        # 최신 데이터 조회
        fresh_data = await domeggook_client.get_item_view(
            product.domeggook_item_id
        )

        # 변경 감지
        if fresh_data['price'] != product.price:
            changed_products.append({
                'product_id': product.id,
                'old_price': product.price,
                'new_price': fresh_data['price']
            })

            # DB 업데이트
            product.price = fresh_data['price']
            await db.commit()

    # 변경된 상품만 동기화 큐에 추가
    for change in changed_products:
        await sync_queue.enqueue(change)

    return len(changed_products)
```

---

## P3: Prometheus 메트릭 상세화

```python
# app/utils/metrics.py

from prometheus_client import Counter, Histogram, Gauge, Info

# 1. 비즈니스 메트릭
products_registered_total = Counter(
    'storebridge_products_registered_total',
    'Total products registered',
    ['status', 'source']  # success/failed, batch/manual
)

registration_success_rate = Gauge(
    'storebridge_registration_success_rate',
    'Registration success rate (last 1 hour)'
)

rejection_reason_count = Counter(
    'storebridge_rejection_reason_total',
    'Total rejections by reason',
    ['reason']  # CATEGORY_MISMATCH, FORBIDDEN_WORD, etc.
)

# 2. 성능 메트릭
api_call_duration_seconds = Histogram(
    'storebridge_api_call_duration_seconds',
    'API call duration',
    ['api_name', 'method'],  # domeggook/naver, GET/POST
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30]
)

image_processing_duration_seconds = Histogram(
    'storebridge_image_processing_duration_seconds',
    'Image processing duration',
    buckets=[0.5, 1, 2, 5, 10]
)

# 3. 인프라 메트릭
queue_depth = Gauge(
    'storebridge_queue_depth',
    'Current queue depth',
    ['queue_name']  # normal/batch/sync/review
)

rate_limit_remaining = Gauge(
    'storebridge_rate_limit_remaining',
    'Remaining rate limit',
    ['api_name']  # domeggook/naver
)

cache_hit_rate = Gauge(
    'storebridge_cache_hit_rate',
    'Cache hit rate (last 5 minutes)'
)

# 4. 애플리케이션 정보
app_info = Info(
    'storebridge_app',
    'Application information'
)
app_info.info({
    'version': '1.0.0',
    'python_version': '3.11',
    'environment': 'production'
})
```

---

이상으로 P0~P3 개선사항 상세 설계 완료! 다음은 DB 스키마 상세 설계 진행하겠습니다.
