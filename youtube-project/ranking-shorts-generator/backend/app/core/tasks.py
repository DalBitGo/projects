"""
Celery Tasks for Background Processing
Based on design doc: docs/02-system-architecture.md
"""
import asyncio
import logging
import shutil
import time
from pathlib import Path
from typing import List, Dict, Optional
from celery import Task
from celery_app import celery_app
from app.database import SessionLocal
from app.models.search import Search
from app.models.video import Video
from app.models.project import Project, ProjectVideo, FinalVideo
from app.core.scraper import tiktok_scraper
from app.core.downloader import download_video, download_videos_parallel
from app.core.video_processor import generate_ranking_video

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """데이터베이스 세션을 자동으로 관리하는 Task 클래스"""

    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(bind=True, base=DatabaseTask, name="app.core.tasks.scrape_tiktok_task")
def scrape_tiktok_task(self, search_id: str, keyword: str, limit: int = 30):
    """
    TikTok 스크래핑 비동기 작업

    Args:
        search_id: Search 레코드 ID
        keyword: 검색 키워드
        limit: 검색 결과 개수

    Returns:
        dict: 결과 정보
    """
    logger.info(f"Starting TikTok scraping task for keyword: {keyword}")

    # 진행 상황 업데이트
    self.update_state(state="PROGRESS", meta={"current": 0, "total": 100, "status": "Initializing..."})

    try:
        # Search 레코드 가져오기
        search = self.db.query(Search).filter(Search.id == search_id).first()
        if not search:
            raise ValueError(f"Search not found: {search_id}")

        search.status = "processing"
        self.db.commit()

        # 비동기 스크래핑 실행
        loop = asyncio.get_event_loop()
        videos = loop.run_until_complete(
            tiktok_scraper.search_with_filters(
                keyword=keyword,
                limit=limit,
                min_views=100000,
                min_likes=5000,
                max_duration=60,
            )
        )

        logger.info(f"Found {len(videos)} videos")

        # 진행 상황 업데이트
        self.update_state(
            state="PROGRESS", meta={"current": 50, "total": 100, "status": f"Found {len(videos)} videos"}
        )

        # 데이터베이스에 저장
        saved_count = 0
        for video_data in videos:
            # 중복 체크
            existing = self.db.query(Video).filter(Video.tiktok_id == video_data["tiktok_id"]).first()

            if existing:
                # 이미 존재하면 search_id만 연결
                existing.search_id = search_id
            else:
                # 새로운 비디오 생성
                import uuid
                video = Video(
                    id=str(uuid.uuid4()),
                    search_id=search_id,
                    tiktok_id=video_data["tiktok_id"],
                    author_username=video_data["author"],
                    title=video_data.get("description", "")[:200],
                    description=video_data.get("description", ""),
                    duration=video_data["duration"],
                    views=video_data["views"],
                    likes=video_data["likes"],
                    comments=video_data["comments"],
                    shares=video_data["shares"],
                    download_url=video_data["download_url"],
                    thumbnail_url=video_data["cover_url"],
                )
                self.db.add(video)
                saved_count += 1

            self.db.commit()

        # Search 레코드 업데이트
        search.status = "completed"
        search.total_found = len(videos)
        self.db.commit()

        logger.info(f"Saved {saved_count} new videos to database")

        return {
            "status": "success",
            "search_id": search_id,
            "keyword": keyword,
            "total_found": len(videos),
            "new_videos": saved_count,
        }

    except Exception as e:
        logger.error(f"Scraping task failed: {e}")

        # Search 레코드 에러 상태로 업데이트
        search = self.db.query(Search).filter(Search.id == search_id).first()
        if search:
            search.status = "failed"
            search.error_message = str(e)
            self.db.commit()

        raise


@celery_app.task(bind=True, base=DatabaseTask, name="app.core.tasks.download_video_task")
def download_video_task(self, video_id: str):
    """
    개별 영상 다운로드 작업

    Args:
        video_id: Video 레코드 ID

    Returns:
        dict: 다운로드 결과
    """
    logger.info(f"Starting video download task: {video_id}")

    try:
        # Video 레코드 가져오기
        video = self.db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise ValueError(f"Video not found: {video_id}")

        # 다운로드 디렉토리
        download_dir = Path("../storage/downloads")
        download_dir.mkdir(parents=True, exist_ok=True)

        # 다운로드 실행
        local_path = download_video(
            url=video.download_url, output_dir=str(download_dir), video_id=video.tiktok_id
        )

        # 데이터베이스 업데이트
        video.local_path = local_path
        video.download_status = "completed"
        self.db.commit()

        logger.info(f"Video downloaded successfully: {local_path}")

        return {"status": "success", "video_id": video_id, "local_path": local_path}

    except Exception as e:
        logger.error(f"Download task failed for video {video_id}: {e}")

        # 에러 상태 업데이트
        video = self.db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.download_status = "failed"
            self.db.commit()

        raise


@celery_app.task(
    bind=True, base=DatabaseTask, name="app.core.tasks.generate_ranking_video_task"
)
def generate_ranking_video_task(
    self, project_id: str, selected_video_ids: List[str], music_path: Optional[str] = None
):
    """
    랭킹 쇼츠 영상 생성 작업

    Args:
        project_id: Project 레코드 ID
        selected_video_ids: 선택된 Video ID 리스트 (순서대로)
        music_path: 배경음악 파일 경로

    Returns:
        dict: 생성 결과
    """
    logger.info(f"Starting ranking video generation: project={project_id}")

    try:
        # Project 레코드 가져오기
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project not found: {project_id}")

        project.status = "processing"
        project.render_progress = 0
        self.db.commit()

        # 진행 상황 콜백
        def progress_callback(current: int, total: int, message: str):
            progress_percent = int((current / total) * 100)
            logger.info(f"Progress: {progress_percent}% - {message}")

            # 상태 업데이트
            self.update_state(
                state="PROGRESS",
                meta={"current": current, "total": total, "percent": progress_percent, "status": message},
            )

            # 데이터베이스 업데이트
            project.render_progress = progress_percent
            self.db.commit()

        # 선택된 비디오 정보 가져오기
        videos = []
        for video_id in selected_video_ids:
            video = self.db.query(Video).filter(Video.id == video_id).first()
            if not video:
                raise ValueError(f"Video not found: {video_id}")
            if not video.local_path or not Path(video.local_path).exists():
                raise ValueError(f"Video file not found: {video_id}")
            videos.append(video)

        logger.info(f"Processing {len(videos)} videos")

        # 출력 경로 설정
        output_dir = Path("../storage/outputs")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f"{project_id}_ranking_video.mp4")

        # 영상 URL 리스트 (로컬 경로 사용)
        video_paths = [v.local_path for v in videos]

        # 배경음악 경로 설정
        if not music_path:
            # 기본 배경음악 사용
            music_path = "../storage/music/energetic_1.mp3"

        # 랭킹 비디오 생성
        final_path = generate_ranking_video(
            video_urls=video_paths,
            output_path=output_path,
            music_path=music_path if Path(music_path).exists() else None,
            progress_callback=progress_callback,
        )

        # FinalVideo 레코드 생성
        final_video = FinalVideo(
            project_id=project_id,
            file_path=final_path,
            file_size=Path(final_path).stat().st_size,
            duration=len(videos) * 7,  # 각 영상 7초
            status="completed",
        )
        self.db.add(final_video)

        # Project 상태 업데이트
        project.status = "completed"
        project.render_progress = 100
        project.final_video_id = final_video.id
        self.db.commit()

        logger.info(f"Ranking video generated successfully: {final_path}")

        return {
            "status": "success",
            "project_id": project_id,
            "final_video_id": final_video.id,
            "output_path": final_path,
            "file_size": final_video.file_size,
        }

    except Exception as e:
        logger.error(f"Video generation task failed: {e}")

        # 에러 상태 업데이트
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.status = "failed"
            project.error_message = str(e)
            self.db.commit()

        raise


@celery_app.task(name="app.core.tasks.cleanup_temp_files")
def cleanup_temp_files():
    """
    임시 파일 정리 작업 (주기적 실행)

    - 24시간 이상 된 temp 파일 삭제
    - 완료된 프로젝트의 중간 파일 삭제
    """
    logger.info("Starting temp files cleanup")

    try:
        temp_dir = Path("../storage/temp")
        if not temp_dir.exists():
            return {"status": "success", "deleted_count": 0}

        deleted_count = 0
        current_time = time.time()

        # 24시간 = 86400초
        max_age = 86400

        for item in temp_dir.iterdir():
            if item.is_dir():
                # 폴더 수정 시간 확인
                mod_time = item.stat().st_mtime
                age = current_time - mod_time

                if age > max_age:
                    logger.info(f"Deleting old temp folder: {item}")
                    shutil.rmtree(item, ignore_errors=True)
                    deleted_count += 1

        logger.info(f"Cleanup completed. Deleted {deleted_count} temp folders")

        return {"status": "success", "deleted_count": deleted_count}

    except Exception as e:
        logger.error(f"Cleanup task failed: {e}")
        raise


@celery_app.task(
    bind=True, base=DatabaseTask, name="app.core.tasks.download_videos_batch_task"
)
def download_videos_batch_task(self, video_ids: List[str]):
    """
    여러 영상을 병렬로 다운로드하는 작업

    Args:
        video_ids: Video ID 리스트

    Returns:
        dict: 다운로드 결과
    """
    logger.info(f"Starting batch download for {len(video_ids)} videos")

    try:
        # Video 레코드 가져오기
        videos = self.db.query(Video).filter(Video.id.in_(video_ids)).all()

        if len(videos) != len(video_ids):
            logger.warning(f"Some videos not found. Expected {len(video_ids)}, got {len(videos)}")

        # 다운로드 URL 추출
        download_urls = [v.download_url for v in videos]

        # 비동기 병렬 다운로드
        loop = asyncio.get_event_loop()
        local_paths = loop.run_until_complete(
            download_videos_parallel(download_urls, output_dir="../storage/downloads", max_workers=5)
        )

        # 데이터베이스 업데이트
        success_count = 0
        for i, video in enumerate(videos):
            if i < len(local_paths) and local_paths[i]:
                video.local_path = local_paths[i]
                video.download_status = "completed"
                success_count += 1
            else:
                video.download_status = "failed"

        self.db.commit()

        logger.info(f"Batch download completed: {success_count}/{len(videos)} successful")

        return {
            "status": "success",
            "total": len(videos),
            "successful": success_count,
            "failed": len(videos) - success_count,
        }

    except Exception as e:
        logger.error(f"Batch download task failed: {e}")
        raise
