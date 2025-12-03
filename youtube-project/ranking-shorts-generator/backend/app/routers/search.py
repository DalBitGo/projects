"""
Search Router
Based on design doc: docs/07-backend-api.md
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from app.database import get_db
from app.models.search import Search
from app.models.video import Video
from app.schemas.search import SearchCreate, SearchResponse, SearchDetailResponse
from celery_app import celery_app
from app.core.tasks import scrape_tiktok_task

router = APIRouter()


@router.post("", response_model=SearchResponse, status_code=status.HTTP_201_CREATED)
async def create_search(search_data: SearchCreate, db: Session = Depends(get_db)):
    """
    새로운 검색 시작

    Args:
        search_data: 검색 요청 데이터 (keyword, limit)
        db: 데이터베이스 세션

    Returns:
        SearchResponse: 생성된 검색 정보 (ID, task_id 포함)
    """
    # Search 레코드 생성
    search = Search(
        id=str(uuid.uuid4()),
        keyword=search_data.keyword,
        status="pending",
        total_found=0,
    )
    db.add(search)
    db.commit()
    db.refresh(search)

    # Celery 백그라운드 작업 시작
    task = scrape_tiktok_task.apply_async(
        args=[search.id, search_data.keyword, search_data.limit],
    )

    # task_id 저장
    search.task_id = task.id
    db.commit()
    db.refresh(search)

    return SearchResponse(
        id=search.id,
        keyword=search.keyword,
        status=search.status,
        total_found=search.total_found,
        task_id=search.task_id,
        created_at=search.created_at,
    )


@router.get("", response_model=List[SearchResponse])
async def get_searches(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """
    검색 목록 조회

    Args:
        skip: 건너뛸 레코드 수 (페이지네이션)
        limit: 가져올 레코드 수
        db: 데이터베이스 세션

    Returns:
        List[SearchResponse]: 검색 목록
    """
    searches = db.query(Search).order_by(Search.created_at.desc()).offset(skip).limit(limit).all()

    return [
        SearchResponse(
            id=s.id,
            keyword=s.keyword,
            status=s.status,
            total_found=s.total_found,
            task_id=s.task_id,
            created_at=s.created_at,
        )
        for s in searches
    ]


@router.get("/{search_id}", response_model=SearchDetailResponse)
async def get_search_detail(search_id: str, db: Session = Depends(get_db)):
    """
    검색 상세 정보 조회 (검색된 영상 목록 포함)

    Args:
        search_id: 검색 ID
        db: 데이터베이스 세션

    Returns:
        SearchDetailResponse: 검색 상세 정보 + 영상 목록
    """
    search = db.query(Search).filter(Search.id == search_id).first()

    if not search:
        raise HTTPException(status_code=404, detail="Search not found")

    # 연관된 영상 조회
    videos = db.query(Video).filter(Video.search_id == search_id).order_by(Video.views.desc()).all()

    return SearchDetailResponse(
        id=search.id,
        keyword=search.keyword,
        status=search.status,
        total_found=search.total_found,
        task_id=search.task_id,
        created_at=search.created_at,
        completed_at=search.completed_at,
        error_message=search.error_message,
        videos=[
            {
                "id": v.id,
                "tiktok_id": v.tiktok_id,
                "author": v.author,
                "title": v.title,
                "description": v.description,
                "duration": v.duration,
                "views": v.views,
                "likes": v.likes,
                "comments": v.comments,
                "shares": v.shares,
                "thumbnail_url": v.thumbnail_url,
                "download_url": v.download_url,
                "local_path": v.local_path,
                "download_status": v.download_status,
                "created_at": v.created_at,
            }
            for v in videos
        ],
    )


@router.get("/{search_id}/status")
async def get_search_status(search_id: str, db: Session = Depends(get_db)):
    """
    검색 작업 진행 상황 조회

    Args:
        search_id: 검색 ID
        db: 데이터베이스 세션

    Returns:
        dict: 작업 상태 정보
    """
    search = db.query(Search).filter(Search.id == search_id).first()

    if not search:
        raise HTTPException(status_code=404, detail="Search not found")

    # Celery 작업 상태 조회
    if search.task_id:
        task = celery_app.AsyncResult(search.task_id)
        task_state = task.state
        task_info = task.info if task.info else {}

        return {
            "search_id": search.id,
            "status": search.status,
            "task_state": task_state,
            "task_info": task_info,
            "total_found": search.total_found,
            "error_message": search.error_message,
        }
    else:
        return {
            "search_id": search.id,
            "status": search.status,
            "task_state": "PENDING",
            "total_found": search.total_found,
            "error_message": search.error_message,
        }


@router.delete("/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_search(search_id: str, db: Session = Depends(get_db)):
    """
    검색 삭제 (관련 영상은 유지)

    Args:
        search_id: 검색 ID
        db: 데이터베이스 세션

    Returns:
        None (204 No Content)
    """
    search = db.query(Search).filter(Search.id == search_id).first()

    if not search:
        raise HTTPException(status_code=404, detail="Search not found")

    # Celery 작업 취소 (진행 중인 경우)
    if search.task_id and search.status == "processing":
        celery_app.control.revoke(search.task_id, terminate=True)

    # 검색 레코드 삭제
    db.delete(search)
    db.commit()

    return None
