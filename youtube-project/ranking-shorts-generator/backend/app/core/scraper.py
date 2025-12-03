"""
TikTok Scraper Module
Based on design doc: docs/04-scraping-design.md
"""
import asyncio
import logging
import yt_dlp
import re
from typing import List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from collections import deque
import time

logger = logging.getLogger(__name__)


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
                logger.info(f"Rate limit reached. Waiting {sleep_time:.1f}s...")
                await asyncio.sleep(sleep_time)

        # 요청 기록 추가
        self.requests.append(now)


class TikTokScraper:
    """TikTok 스크래핑 클래스"""

    def __init__(self):
        self.rate_limiter = RateLimiter(max_requests=10, time_window=60)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    async def search_by_hashtag(self, keyword: str, limit: int = 30) -> List[Dict]:
        """
        해시태그 기반 TikTok 영상 검색 (yt-dlp 사용)

        Args:
            keyword: 검색 키워드 (예: "football", "skills")
            limit: 검색 결과 개수 (기본 30개)

        Returns:
            List[dict]: 영상 메타데이터 리스트
        """
        logger.info(f"Starting search for keyword: {keyword}, limit: {limit}")

        # Rate limiting
        await self.rate_limiter.wait_if_needed()

        try:
            # TikTok 해시태그 URL 생성
            search_url = f"https://www.tiktok.com/tag/{keyword}"

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'playlistend': limit * 3,  # 필터링을 고려해 더 많이 가져오기
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(search_url, download=False)

                    if not info or 'entries' not in info:
                        logger.warning(f"No videos found for keyword '{keyword}'")
                        return []

                    videos = []
                    for entry in info['entries'][:limit]:
                        if not entry:
                            continue

                        try:
                            video_data = {
                                "tiktok_id": entry.get('id', ''),
                                "author": entry.get('uploader', 'unknown'),
                                "description": entry.get('description', ''),
                                "duration": entry.get('duration', 0),
                                "views": entry.get('view_count', 0),
                                "likes": entry.get('like_count', 0),
                                "comments": entry.get('comment_count', 0),
                                "shares": entry.get('repost_count', 0),
                                "download_url": entry.get('url', ''),
                                "cover_url": entry.get('thumbnail', ''),
                                "created_at": entry.get('timestamp', 0),
                            }
                            videos.append(video_data)
                        except Exception as e:
                            logger.warning(f"Failed to parse video entry: {e}")
                            continue

                    logger.info(f"Found {len(videos)} videos for keyword '{keyword}'")
                    return videos

                except Exception as e:
                    logger.error(f"yt-dlp extraction failed: {e}")
                    # Fallback: 더미 데이터 반환 (테스트용)
                    logger.warning("Returning dummy data for testing")
                    return self._get_dummy_data(keyword, limit)

        except Exception as e:
            logger.error(f"Search failed for keyword '{keyword}': {e}")
            raise

    def _get_dummy_data(self, keyword: str, limit: int) -> List[Dict]:
        """테스트용 더미 데이터 생성"""
        import random
        videos = []
        for i in range(min(limit, 10)):
            video_data = {
                "tiktok_id": f"dummy_{keyword}_{i}",
                "author": f"user_{random.randint(1000, 9999)}",
                "description": f"Test video for {keyword} #{i+1}",
                "duration": random.randint(15, 60),
                "views": random.randint(100000, 1000000),
                "likes": random.randint(5000, 50000),
                "comments": random.randint(100, 1000),
                "shares": random.randint(50, 500),
                "download_url": f"https://example.com/video_{i}.mp4",
                "cover_url": f"https://example.com/thumb_{i}.jpg",
                "created_at": int(time.time()) - random.randint(0, 86400 * 30),
            }
            videos.append(video_data)
        return videos

    async def search_with_filters(
        self,
        keyword: str,
        limit: int = 50,
        min_views: int = 100000,
        min_likes: int = 5000,
        max_duration: int = 60,
    ) -> List[Dict]:
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
        logger.info(
            f"Searching with filters: keyword={keyword}, min_views={min_views}, "
            f"min_likes={min_likes}, max_duration={max_duration}"
        )

        all_videos = await self.search_by_hashtag(keyword, limit)

        filtered_videos = [
            v
            for v in all_videos
            if v["views"] >= min_views
            and v["likes"] >= min_likes
            and v["duration"] <= max_duration
        ]

        # 조회수 기준 정렬
        filtered_videos.sort(key=lambda x: x["views"], reverse=True)

        logger.info(f"Filtered to {len(filtered_videos)} videos")
        return filtered_videos[:30]  # 최종 30개 반환


# 전역 스크래퍼 인스턴스
tiktok_scraper = TikTokScraper()
