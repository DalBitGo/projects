"""
Video Downloader Module
Based on design doc: docs/05-video-processing.md
"""
import yt_dlp
import asyncio
import logging
from pathlib import Path
from typing import Optional, Callable
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class DownloadProgressHook:
    """다운로드 진행 상황 훅"""

    def __init__(self, callback: Optional[Callable] = None):
        self.callback = callback
        self.current_percent = 0

    def __call__(self, d):
        if d["status"] == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)

            if total > 0:
                progress = (downloaded / total) * 100
                self.current_percent = int(progress)

                if self.callback:
                    self.callback(self.current_percent)

        elif d["status"] == "finished":
            logger.info(f"Download completed: {d['filename']}")
            if self.callback:
                self.callback(100)


def download_video(
    url: str, output_dir: str = "../storage/downloads", video_id: Optional[str] = None
) -> str:
    """
    TikTok 영상 다운로드

    Args:
        url: TikTok 영상 URL
        output_dir: 저장 디렉토리
        video_id: 영상 ID (파일명 지정용)

    Returns:
        str: 다운로드된 파일 경로
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 파일명 템플릿
    if video_id:
        outtmpl = str(output_path / f"{video_id}.%(ext)s")
    else:
        outtmpl = str(output_path / "%(id)s.%(ext)s")

    ydl_opts = {
        "format": "best[height<=1920]",  # 최대 1080p
        "outtmpl": outtmpl,
        "quiet": False,
        "no_warnings": False,
        "extract_flat": False,
        "progress_hooks": [DownloadProgressHook()],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        logger.info(f"Downloaded video: {filename}")
        return filename

    except Exception as e:
        logger.error(f"Failed to download video from {url}: {e}")
        raise


async def download_video_async(
    url: str,
    output_dir: str = "../storage/downloads",
    video_id: Optional[str] = None,
    progress_callback: Optional[Callable] = None,
) -> str:
    """
    비동기 영상 다운로드

    Args:
        url: TikTok 영상 URL
        output_dir: 저장 디렉토리
        video_id: 영상 ID
        progress_callback: 진행 상황 콜백

    Returns:
        str: 다운로드된 파일 경로
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if video_id:
        outtmpl = str(output_path / f"{video_id}.%(ext)s")
    else:
        outtmpl = str(output_path / "%(id)s.%(ext)s")

    ydl_opts = {
        "format": "best[height<=1920]",
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [DownloadProgressHook(callback=progress_callback)],
    }

    loop = asyncio.get_event_loop()

    def _download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)

    try:
        filename = await loop.run_in_executor(None, _download)
        logger.info(f"Downloaded video async: {filename}")
        return filename

    except Exception as e:
        logger.error(f"Failed to download video async from {url}: {e}")
        raise


async def download_videos_parallel(
    urls: list, output_dir: str = "../storage/downloads", max_workers: int = 5
) -> list:
    """
    여러 영상을 병렬로 다운로드

    Args:
        urls: 영상 URL 리스트
        output_dir: 저장 디렉토리
        max_workers: 최대 동시 다운로드 수

    Returns:
        list: 다운로드된 파일 경로 리스트
    """
    logger.info(f"Starting parallel download of {len(urls)} videos")

    loop = asyncio.get_event_loop()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        tasks = [loop.run_in_executor(executor, download_video, url, output_dir) for url in urls]

        results = await asyncio.gather(*tasks, return_exceptions=True)

    # 에러 필터링
    successful = []
    failed = []

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Failed to download video {i+1}: {result}")
            failed.append(urls[i])
        else:
            successful.append(result)

    logger.info(f"Downloaded {len(successful)}/{len(urls)} videos successfully")

    if failed:
        logger.warning(f"Failed URLs: {failed}")

    return successful


async def download_thumbnail(
    url: str, video_id: str, output_dir: str = "../storage/thumbnails"
) -> str:
    """
    썸네일 이미지 다운로드

    Args:
        url: 썸네일 URL
        video_id: 영상 ID
        output_dir: 저장 디렉토리

    Returns:
        str: 로컬 파일 경로
    """
    import httpx

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filename = f"{video_id}.jpg"
    filepath = output_path / filename

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()

            with open(filepath, "wb") as f:
                f.write(response.content)

        logger.info(f"Downloaded thumbnail: {filepath}")
        return str(filepath)

    except Exception as e:
        logger.error(f"Failed to download thumbnail from {url}: {e}")
        raise


async def download_all_thumbnails(videos: list, output_dir: str = "../storage/thumbnails") -> list:
    """병렬로 모든 썸네일 다운로드"""
    tasks = [download_thumbnail(video["cover_url"], video["tiktok_id"], output_dir) for video in videos]

    return await asyncio.gather(*tasks, return_exceptions=True)
