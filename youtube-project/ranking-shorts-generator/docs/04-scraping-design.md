# 데이터 수집 및 스크래핑 설계

## 1. 개요

### 1.1 목적
TikTok 플랫폼에서 특정 해시태그/키워드 기반으로 인기 영상 메타데이터를 수집하여, 사용자가 랭킹 쇼츠 제작에 활용할 영상을 선택할 수 있도록 지원

### 1.2 수집 대상 데이터
- 영상 메타데이터 (ID, URL, 제목, 설명)
- 통계 정보 (조회수, 좋아요, 댓글, 공유 수)
- 미디어 정보 (썸네일, 영상 다운로드 URL, 길이)
- 크리에이터 정보 (사용자명, 프로필 이미지)

---

## 2. 스크래핑 전략

### 2.1 접근 방법 비교

| 방법 | 장점 | 단점 | 선택 |
|------|------|------|------|
| **TikTok 공식 API** | 안정적, 합법적 | 승인 필요, 제한적 접근, 일반 사용자 불가 | ❌ |
| **비공식 API (TikTokApi)** | Python 친화적, 해시태그 검색 가능 | 가끔 깨짐, 업데이트 필요 | ✅ 1순위 |
| **Playwright 스크래핑** | 유연함, 커스터마이징 가능 | 느림, 복잡함, 유지보수 어려움 | ⚠️ 백업 |
| **유료 API (Apify)** | 안정적, 관리 불필요 | 비용 발생 ($49/월~) | ⚠️ 대안 |
| **수동 URL 입력** | 100% 안정적, 선택의 질 보장 | 자동화 안 됨, 시간 소요 | ⚠️ 최후 수단 |

**최종 선택**:
1. **TikTokApi** (Python 라이브러리) - 주 방법
2. **Playwright 커스텀 스크래핑** - TikTokApi 실패 시
3. **수동 URL 입력** - 완전 실패 시

---

## 3. TikTokApi 사용 설계

### 3.1 라이브러리 정보
- **GitHub**: https://github.com/davidteather/TikTok-Api
- **버전**: 6.0+
- **라이선스**: MIT
- **의존성**: Playwright (브라우저 자동화)

### 3.2 설치 및 설정

#### 설치
```bash
pip install TikTokApi
playwright install chromium
```

#### 기본 설정
```python
from TikTokApi import TikTokApi
import asyncio

async def init_api():
    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=1,
            sleep_after=3,  # 요청 간 대기 시간 (초)
            headless=True,  # 헤드리스 모드
            executable_path=None  # Chromium 경로 (자동)
        )
        return api
```

### 3.3 해시태그 검색 구현

#### 기본 검색
```python
async def search_by_hashtag(keyword: str, limit: int = 30):
    """
    해시태그 기반 TikTok 영상 검색

    Args:
        keyword: 검색 키워드 (예: "football", "skills")
        limit: 검색 결과 개수 (기본 30개)

    Returns:
        List[dict]: 영상 메타데이터 리스트
    """
    async with TikTokApi() as api:
        await api.create_sessions(num_sessions=1, sleep_after=3)

        # 해시태그 객체 생성
        tag = api.hashtag(name=keyword)

        videos = []
        async for video in tag.videos(count=limit):
            video_data = {
                "tiktok_id": video.id,
                "author": video.author.username,
                "description": video.desc,
                "duration": video.video.duration,
                "views": video.stats.get("playCount", 0),
                "likes": video.stats.get("diggCount", 0),
                "comments": video.stats.get("commentCount", 0),
                "shares": video.stats.get("shareCount", 0),
                "download_url": video.video.download_addr,
                "cover_url": video.video.cover,
                "created_at": video.create_time,
            }
            videos.append(video_data)

        return videos
```

#### 고급 검색 (필터링)
```python
async def search_with_filters(
    keyword: str,
    limit: int = 50,
    min_views: int = 100000,
    min_likes: int = 5000,
    max_duration: int = 60  # 초
):
    """
    필터링 조건이 있는 검색

    Args:
        keyword: 검색 키워드
        limit: 초기 검색 개수 (필터링 전)
        min_views: 최소 조회수
        min_likes: 최소 좋아요 수
        max_duration: 최대 영상 길이 (초)

    Returns:
        List[dict]: 필터링된 영상 목록
    """
    all_videos = await search_by_hashtag(keyword, limit)

    filtered_videos = [
        v for v in all_videos
        if v["views"] >= min_views
        and v["likes"] >= min_likes
        and v["duration"] <= max_duration
    ]

    # 조회수 기준 정렬
    filtered_videos.sort(key=lambda x: x["views"], reverse=True)

    return filtered_videos[:30]  # 최종 30개 반환
```

### 3.4 에러 처리 및 재시도

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def search_with_retry(keyword: str, limit: int = 30):
    """
    재시도 로직이 포함된 검색

    - 최대 3회 재시도
    - 지수 백오프 (4초, 8초, 10초)
    """
    try:
        return await search_by_hashtag(keyword, limit)
    except Exception as e:
        print(f"Search failed: {e}")
        raise
```

### 3.5 Rate Limiting 관리

```python
import time
from collections import deque

class RateLimiter:
    """
    Rate Limiting 클래스
    - TikTok IP 차단 방지
    - 분당 최대 요청 수 제한
    """
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()

    async def wait_if_needed(self):
        """필요 시 대기"""
        now = time.time()

        # 오래된 요청 기록 제거
        while self.requests and self.requests[0] < now - self.time_window:
            self.requests.popleft()

        # 제한 초과 시 대기
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0])
            if sleep_time > 0:
                print(f"Rate limit reached. Waiting {sleep_time:.1f}s...")
                await asyncio.sleep(sleep_time)

        # 요청 기록 추가
        self.requests.append(now)

# 사용 예시
rate_limiter = RateLimiter(max_requests=10, time_window=60)

async def safe_search(keyword: str):
    await rate_limiter.wait_if_needed()
    return await search_by_hashtag(keyword)
```

---

## 4. Playwright 커스텀 스크래핑 (백업 방법)

### 4.1 사용 시나리오
- TikTokApi가 작동하지 않을 때
- 특정 데이터가 API에서 제공되지 않을 때
- 최신 TikTok UI 변경 사항 반영 시

### 4.2 구현 예시

```python
from playwright.async_api import async_playwright
import json

async def scrape_tiktok_playwright(keyword: str, limit: int = 30):
    """
    Playwright를 이용한 커스텀 스크래핑
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        # TikTok 해시태그 페이지 접속
        url = f"https://www.tiktok.com/tag/{keyword}"
        await page.goto(url, wait_until="networkidle")

        # 스크롤하여 더 많은 영상 로드
        for _ in range(5):
            await page.evaluate("window.scrollBy(0, window.innerHeight)")
            await page.wait_for_timeout(2000)

        # 영상 데이터 추출
        videos = await page.evaluate("""
            () => {
                const videoElements = document.querySelectorAll('[data-e2e="search-card-item"]');
                return Array.from(videoElements).map(el => {
                    const link = el.querySelector('a');
                    const stats = el.querySelectorAll('[data-e2e="video-views"]');
                    return {
                        url: link ? link.href : '',
                        thumbnail: el.querySelector('img')?.src || '',
                        views: stats[0]?.textContent || '0'
                    };
                });
            }
        """)

        await browser.close()
        return videos[:limit]
```

### 4.3 HTML 파싱 (BeautifulSoup 사용)

```python
from bs4 import BeautifulSoup
import httpx

async def parse_tiktok_html(html: str):
    """
    TikTok HTML 파싱
    """
    soup = BeautifulSoup(html, 'html.parser')

    # JSON 데이터 추출 (TikTok은 __UNIVERSAL_DATA_FOR_REHYDRATION__ 사용)
    script_tag = soup.find('script', id='__UNIVERSAL_DATA_FOR_REHYDRATION__')
    if script_tag:
        data = json.loads(script_tag.string)
        # 데이터 구조 분석 후 파싱
        return data

    return None
```

---

## 5. 수동 URL 입력 방식

### 5.1 UI 설계
```
┌─────────────────────────────────────────┐
│  Manual URL Input                       │
├─────────────────────────────────────────┤
│  Paste TikTok URLs (one per line):     │
│  ┌─────────────────────────────────┐   │
│  │ https://tiktok.com/@user/video/1│   │
│  │ https://tiktok.com/@user/video/2│   │
│  │ https://tiktok.com/@user/video/3│   │
│  │                                  │   │
│  └─────────────────────────────────┘   │
│                                          │
│  [Fetch Video Info]                     │
└─────────────────────────────────────────┘
```

### 5.2 구현

```python
import re

def extract_video_id(url: str) -> str:
    """
    TikTok URL에서 영상 ID 추출

    예시:
    - https://www.tiktok.com/@user/video/1234567890
    - https://vm.tiktok.com/ZMeFgHpQP/
    """
    # 일반 URL 패턴
    match = re.search(r'/video/(\d+)', url)
    if match:
        return match.group(1)

    # 축약 URL 처리 (리다이렉트 필요)
    if 'vm.tiktok.com' in url:
        # 실제 URL로 리다이렉트 필요
        return None

    return None

async def fetch_video_by_url(url: str):
    """
    URL로부터 영상 정보 가져오기
    """
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError("Invalid TikTok URL")

    async with TikTokApi() as api:
        await api.create_sessions(num_sessions=1)
        video = api.video(id=video_id)

        # 영상 정보 조회
        info = await video.info()
        return {
            "tiktok_id": video_id,
            "url": url,
            "title": info.desc,
            "views": info.stats["playCount"],
            # ... 기타 정보
        }
```

---

## 6. 데이터 저장 및 캐싱

### 6.1 데이터베이스 저장

```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.video import Video
from datetime import datetime
import uuid

async def save_videos_to_db(session: AsyncSession, videos: list, search_id: str):
    """
    스크래핑한 영상 데이터를 DB에 저장
    """
    db_videos = []

    for video in videos:
        db_video = Video(
            id=str(uuid.uuid4()),
            search_id=search_id,
            tiktok_id=video["tiktok_id"],
            thumbnail_url=video["cover_url"],
            title=video["description"],
            views=video["views"],
            likes=video["likes"],
            duration=video["duration"],
            download_url=video["download_url"],
            created_at=datetime.utcnow()
        )
        db_videos.append(db_video)

    session.add_all(db_videos)
    await session.commit()

    return db_videos
```

### 6.2 Redis 캐싱

```python
import redis.asyncio as redis
import json

class VideoCache:
    """Redis 캐싱 클래스"""

    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)

    async def get_search_results(self, keyword: str) -> list:
        """캐시에서 검색 결과 가져오기"""
        key = f"search:{keyword}"
        cached = await self.redis.get(key)

        if cached:
            return json.loads(cached)
        return None

    async def set_search_results(self, keyword: str, videos: list, ttl: int = 3600):
        """검색 결과 캐싱 (1시간)"""
        key = f"search:{keyword}"
        await self.redis.setex(key, ttl, json.dumps(videos))

    async def close(self):
        await self.redis.close()

# 사용 예시
cache = VideoCache("redis://localhost:6379/0")

async def search_with_cache(keyword: str):
    # 캐시 확인
    cached = await cache.get_search_results(keyword)
    if cached:
        print("Cache hit!")
        return cached

    # 스크래핑
    videos = await search_by_hashtag(keyword)

    # 캐싱
    await cache.set_search_results(keyword, videos)

    return videos
```

---

## 7. 썸네일 다운로드

### 7.1 구현

```python
import httpx
from pathlib import Path

async def download_thumbnail(url: str, video_id: str, output_dir: str = "storage/thumbnails"):
    """
    썸네일 이미지 다운로드

    Args:
        url: 썸네일 URL
        video_id: 영상 ID
        output_dir: 저장 디렉토리

    Returns:
        str: 로컬 파일 경로
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filename = f"{video_id}.jpg"
    filepath = output_path / filename

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

        with open(filepath, 'wb') as f:
            f.write(response.content)

    return str(filepath)

async def download_all_thumbnails(videos: list):
    """병렬로 모든 썸네일 다운로드"""
    tasks = [
        download_thumbnail(video["cover_url"], video["tiktok_id"])
        for video in videos
    ]
    return await asyncio.gather(*tasks)
```

---

## 8. Celery 작업 통합

### 8.1 비동기 작업 정의

```python
from celery import Task
from app.celery_app import celery_app

@celery_app.task(bind=True, name="scrape_tiktok")
def scrape_tiktok_task(self: Task, search_id: str, keyword: str, limit: int = 30):
    """
    Celery 작업: TikTok 스크래핑

    Args:
        search_id: 검색 ID (DB 참조용)
        keyword: 검색 키워드
        limit: 결과 개수
    """
    import asyncio

    # 진행 상황 업데이트
    self.update_state(state='PROGRESS', meta={
        'current': 0,
        'total': limit,
        'status': 'Initializing TikTok API...'
    })

    # 스크래핑 실행 (async 함수 실행)
    loop = asyncio.get_event_loop()
    videos = loop.run_until_complete(search_by_hashtag(keyword, limit))

    # 진행 상황 업데이트
    self.update_state(state='PROGRESS', meta={
        'current': len(videos),
        'total': limit,
        'status': f'Found {len(videos)} videos'
    })

    # DB 저장
    from app.db.session import SessionLocal
    session = SessionLocal()

    saved_videos = asyncio.run(save_videos_to_db(session, videos, search_id))
    session.close()

    # 썸네일 다운로드
    self.update_state(state='PROGRESS', meta={
        'current': len(videos),
        'total': limit,
        'status': 'Downloading thumbnails...'
    })

    asyncio.run(download_all_thumbnails(videos))

    return {
        'search_id': search_id,
        'videos_found': len(videos),
        'status': 'completed'
    }
```

### 8.2 작업 실행 및 모니터링

```python
from app.core.tasks import scrape_tiktok_task

# 작업 실행
task = scrape_tiktok_task.delay(
    search_id="uuid-xxx",
    keyword="football skills",
    limit=30
)

# 작업 상태 확인
result = task.get()  # 블로킹
print(result)

# 또는 비동기 확인
if task.ready():
    result = task.result
else:
    status = task.info  # 진행 상황
```

---

## 9. 에러 처리 및 로깅

### 9.1 에러 분류

| 에러 타입 | 원인 | 처리 방법 |
|----------|------|----------|
| `NetworkError` | 네트워크 연결 실패 | 재시도 (3회) |
| `RateLimitError` | 요청 과다 | 대기 후 재시도 |
| `VideoNotFoundError` | 영상 삭제됨 | 건너뛰기, 로그 기록 |
| `APIChangeError` | TikTok 구조 변경 | 알림, 수동 URL 입력 제안 |
| `ParseError` | 데이터 파싱 실패 | 건너뛰기, 로그 기록 |

### 9.2 커스텀 예외

```python
class ScrapingError(Exception):
    """기본 스크래핑 에러"""
    pass

class RateLimitError(ScrapingError):
    """Rate limit 초과"""
    pass

class VideoNotFoundError(ScrapingError):
    """영상을 찾을 수 없음"""
    pass

class APIChangeError(ScrapingError):
    """TikTok API 변경"""
    pass
```

### 9.3 로깅

```python
import logging

logger = logging.getLogger(__name__)

async def search_with_logging(keyword: str):
    logger.info(f"Starting search for keyword: {keyword}")

    try:
        videos = await search_by_hashtag(keyword)
        logger.info(f"Found {len(videos)} videos")
        return videos

    except RateLimitError as e:
        logger.warning(f"Rate limit hit: {e}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error during scraping: {e}", exc_info=True)
        raise ScrapingError(f"Failed to scrape: {e}")
```

---

## 10. 성능 최적화

### 10.1 병렬 처리

```python
import asyncio

async def search_multiple_keywords(keywords: list):
    """
    여러 키워드를 병렬로 검색
    """
    tasks = [search_by_hashtag(kw, limit=20) for kw in keywords]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 에러 필터링
    valid_results = [r for r in results if not isinstance(r, Exception)]

    return valid_results
```

### 10.2 데이터 압축

```python
import gzip
import pickle

def compress_video_data(videos: list) -> bytes:
    """영상 데이터 압축 (저장 용량 절약)"""
    data = pickle.dumps(videos)
    compressed = gzip.compress(data)
    return compressed

def decompress_video_data(compressed: bytes) -> list:
    """압축 해제"""
    data = gzip.decompress(compressed)
    videos = pickle.loads(data)
    return videos
```

---

## 11. 모니터링 및 알림

### 11.1 스크래핑 통계

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ScrapingStats:
    total_searches: int = 0
    total_videos_found: int = 0
    failed_searches: int = 0
    avg_response_time: float = 0.0
    last_updated: datetime = None

class StatsTracker:
    def __init__(self):
        self.stats = ScrapingStats()

    def record_search(self, videos_count: int, response_time: float, success: bool):
        self.stats.total_searches += 1
        if success:
            self.stats.total_videos_found += videos_count
        else:
            self.stats.failed_searches += 1

        # 평균 응답 시간 계산
        n = self.stats.total_searches
        self.stats.avg_response_time = (
            (self.stats.avg_response_time * (n-1) + response_time) / n
        )

        self.stats.last_updated = datetime.utcnow()
```

### 11.2 알림 시스템

```python
async def send_alert(message: str, severity: str = "info"):
    """
    알림 전송 (향후 이메일/Slack 연동)
    """
    logger.log(
        logging.INFO if severity == "info" else logging.ERROR,
        f"[ALERT] {message}"
    )

    # TODO: 이메일/Slack 전송
```

---

## 12. 테스트

### 12.1 단위 테스트

```python
import pytest

@pytest.mark.asyncio
async def test_search_by_hashtag():
    videos = await search_by_hashtag("test", limit=5)

    assert len(videos) <= 5
    assert all("tiktok_id" in v for v in videos)
    assert all(v["views"] >= 0 for v in videos)

@pytest.mark.asyncio
async def test_rate_limiter():
    limiter = RateLimiter(max_requests=2, time_window=5)

    start = time.time()

    for _ in range(3):
        await limiter.wait_if_needed()

    elapsed = time.time() - start
    assert elapsed >= 5  # 3번째 요청은 5초 대기해야 함
```

### 12.2 통합 테스트

```python
@pytest.mark.asyncio
async def test_full_scraping_workflow():
    # 검색
    videos = await search_by_hashtag("football", limit=10)

    # DB 저장
    search_id = str(uuid.uuid4())
    # ... DB 저장 로직

    # 썸네일 다운로드
    thumbnails = await download_all_thumbnails(videos)

    # 검증
    assert len(thumbnails) == len(videos)
```

---

## 13. 유지보수 가이드

### 13.1 TikTok 구조 변경 대응

**모니터링**:
- 주 1회 테스트 스크래핑 실행
- 에러 발생 시 알림

**업데이트 프로세스**:
1. TikTokApi 라이브러리 업데이트 확인
   ```bash
   pip install --upgrade TikTokApi
   ```
2. GitHub Issues 확인
3. 필요 시 Playwright 스크래핑으로 전환

### 13.2 API 키 관리

```python
# .env
TIKTOK_API_KEY=your_key_here  # 향후 공식 API 사용 시
APIFY_API_KEY=your_key_here   # 유료 서비스 사용 시
```

---

**문서 버전**: 1.0
**작성일**: 2025-10-19
**최종 수정일**: 2025-10-19
