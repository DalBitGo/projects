"""
Videos Router
Based on design doc: docs/07-backend-api.md
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path

from app.database import get_db
from app.models.video import Video
from app.schemas.video import VideoResponse, VideoDetailResponse
from celery_app import celery_app
from app.core.tasks import download_video_task, download_videos_batch_task

router = APIRouter()


@router.get("", response_model=List[VideoResponse])
async def get_videos(
    skip: int = 0,
    limit: int = 50,
    search_id: Optional[str] = None,
    min_views: Optional[int] = None,
    min_likes: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    영상 목록 조회 (필터링 가능)

    Args:
        skip: 건너뛸 레코드 수
        limit: 가져올 레코드 수
        search_id: 특정 검색 결과만 조회
        min_views: 최소 조회수 필터
        min_likes: 최소 좋아요 수 필터
        db: 데이터베이스 세션

    Returns:
        List[VideoResponse]: 영상 목록
    """
    query = db.query(Video)

    # 필터 적용
    if search_id:
        query = query.filter(Video.search_id == search_id)
    if min_views:
        query = query.filter(Video.views >= min_views)
    if min_likes:
        query = query.filter(Video.likes >= min_likes)

    # 정렬 및 페이지네이션
    videos = query.order_by(Video.views.desc()).offset(skip).limit(limit).all()

    return [
        VideoResponse(
            id=v.id,
            tiktok_id=v.tiktok_id,
            author=v.author,
            title=v.title,
            duration=v.duration,
            views=v.views,
            likes=v.likes,
            comments=v.comments,
            shares=v.shares,
            thumbnail_url=v.thumbnail_url,
            download_status=v.download_status,
            created_at=v.created_at,
        )
        for v in videos
    ]


@router.get("/{video_id}", response_model=VideoDetailResponse)
async def get_video_detail(video_id: str, db: Session = Depends(get_db)):
    """
    영상 상세 정보 조회

    Args:
        video_id: 영상 ID
        db: 데이터베이스 세션

    Returns:
        VideoDetailResponse: 영상 상세 정보
    """
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    return VideoDetailResponse(
        id=video.id,
        search_id=video.search_id,
        tiktok_id=video.tiktok_id,
        author=video.author,
        title=video.title,
        description=video.description,
        duration=video.duration,
        views=video.views,
        likes=video.likes,
        comments=video.comments,
        shares=video.shares,
        thumbnail_url=video.thumbnail_url,
        download_url=video.download_url,
        local_path=video.local_path,
        download_status=video.download_status,
        created_at=video.created_at,
        created_at_tiktok=video.created_at_tiktok,
    )


@router.post("/{video_id}/download")
async def download_video(video_id: str, db: Session = Depends(get_db)):
    """
    영상 다운로드 시작

    Args:
        video_id: 영상 ID
        db: 데이터베이스 세션

    Returns:
        dict: 다운로드 작업 정보
    """
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # 이미 다운로드 완료된 경우
    if video.local_path and Path(video.local_path).exists():
        return {
            "video_id": video_id,
            "status": "already_downloaded",
            "local_path": video.local_path,
            "message": "Video already downloaded",
        }

    # 이미 다운로드 진행 중인 경우
    if video.download_status == "processing":
        return {
            "video_id": video_id,
            "status": "processing",
            "message": "Download already in progress",
        }

    # Celery 백그라운드 작업 시작
    task = download_video_task.apply_async(args=[video_id], queue="download")

    # 상태 업데이트
    video.download_status = "processing"
    db.commit()

    return {
        "video_id": video_id,
        "task_id": task.id,
        "status": "queued",
        "message": "Download started",
    }


@router.post("/download-batch")
async def download_videos_batch(video_ids: List[str], db: Session = Depends(get_db)):
    """
    여러 영상을 일괄 다운로드

    Args:
        video_ids: 영상 ID 리스트
        db: 데이터베이스 세션

    Returns:
        dict: 일괄 다운로드 작업 정보
    """
    # 영상 존재 확인
    videos = db.query(Video).filter(Video.id.in_(video_ids)).all()

    if len(videos) != len(video_ids):
        raise HTTPException(status_code=400, detail="Some videos not found")

    # 다운로드 필요한 영상만 필터링
    videos_to_download = []
    for video in videos:
        if not video.local_path or not Path(video.local_path).exists():
            videos_to_download.append(video.id)
            video.download_status = "processing"

    db.commit()

    if not videos_to_download:
        return {
            "status": "already_downloaded",
            "total": len(video_ids),
            "message": "All videos already downloaded",
        }

    # Celery 백그라운드 작업 시작
    task = download_videos_batch_task.apply_async(args=[videos_to_download], queue="download")

    return {
        "task_id": task.id,
        "status": "queued",
        "total": len(video_ids),
        "to_download": len(videos_to_download),
        "message": "Batch download started",
    }


@router.get("/{video_id}/download-status")
async def get_download_status(video_id: str, db: Session = Depends(get_db)):
    """
    영상 다운로드 상태 조회

    Args:
        video_id: 영상 ID
        db: 데이터베이스 세션

    Returns:
        dict: 다운로드 상태 정보
    """
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # 로컬 파일 존재 확인
    file_exists = False
    if video.local_path:
        file_exists = Path(video.local_path).exists()

    return {
        "video_id": video_id,
        "download_status": video.download_status,
        "local_path": video.local_path,
        "file_exists": file_exists,
    }


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(video_id: str, delete_file: bool = False, db: Session = Depends(get_db)):
    """
    영상 레코드 삭제 (선택적으로 파일도 삭제)

    Args:
        video_id: 영상 ID
        delete_file: 로컬 파일도 삭제할지 여부
        db: 데이터베이스 세션

    Returns:
        None (204 No Content)
    """
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # 파일 삭제 (요청 시)
    if delete_file and video.local_path:
        file_path = Path(video.local_path)
        if file_path.exists():
            file_path.unlink()

    # 레코드 삭제
    db.delete(video)
    db.commit()

    return None


@router.get("/stats/summary")
async def get_videos_stats(db: Session = Depends(get_db)):
    """
    영상 통계 요약

    Returns:
        dict: 통계 정보
    """
    total_videos = db.query(Video).count()
    downloaded_videos = db.query(Video).filter(Video.download_status == "completed").count()
    total_views = db.query(Video).with_entities(db.func.sum(Video.views)).scalar() or 0
    total_likes = db.query(Video).with_entities(db.func.sum(Video.likes)).scalar() or 0

    return {
        "total_videos": total_videos,
        "downloaded_videos": downloaded_videos,
        "download_rate": (
            round((downloaded_videos / total_videos) * 100, 2) if total_videos > 0 else 0
        ),
        "total_views": total_views,
        "total_likes": total_likes,
        "avg_views": round(total_views / total_videos, 2) if total_videos > 0 else 0,
        "avg_likes": round(total_likes / total_videos, 2) if total_videos > 0 else 0,
    }
