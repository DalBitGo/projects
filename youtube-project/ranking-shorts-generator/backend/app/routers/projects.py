"""
Projects Router
Based on design doc: docs/07-backend-api.md
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from app.database import get_db
from app.models.project import Project, ProjectVideo, FinalVideo
from app.models.video import Video
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectDetailResponse,
    ProjectUpdate,
)
from celery_app import celery_app
from app.core.tasks import generate_ranking_video_task

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project_data: ProjectCreate, db: Session = Depends(get_db)):
    """
    새로운 프로젝트 생성

    Args:
        project_data: 프로젝트 생성 데이터 (title, description)
        db: 데이터베이스 세션

    Returns:
        ProjectResponse: 생성된 프로젝트 정보
    """
    project = Project(
        id=str(uuid.uuid4()),
        title=project_data.title,
        description=project_data.description,
        status="draft",
        render_progress=0,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    return ProjectResponse(
        id=project.id,
        title=project.title,
        description=project.description,
        status=project.status,
        render_progress=project.render_progress,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get("", response_model=List[ProjectResponse])
async def get_projects(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """
    프로젝트 목록 조회

    Args:
        skip: 건너뛸 레코드 수
        limit: 가져올 레코드 수
        db: 데이터베이스 세션

    Returns:
        List[ProjectResponse]: 프로젝트 목록
    """
    projects = db.query(Project).order_by(Project.created_at.desc()).offset(skip).limit(limit).all()

    return [
        ProjectResponse(
            id=p.id,
            title=p.title,
            description=p.description,
            status=p.status,
            render_progress=p.render_progress,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in projects
    ]


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project_detail(project_id: str, db: Session = Depends(get_db)):
    """
    프로젝트 상세 정보 조회 (선택된 영상 목록 포함)

    Args:
        project_id: 프로젝트 ID
        db: 데이터베이스 세션

    Returns:
        ProjectDetailResponse: 프로젝트 상세 정보
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 선택된 영상 조회 (순서대로)
    project_videos = (
        db.query(ProjectVideo)
        .filter(ProjectVideo.project_id == project_id)
        .order_by(ProjectVideo.order_index)
        .all()
    )

    videos = []
    for pv in project_videos:
        video = db.query(Video).filter(Video.id == pv.video_id).first()
        if video:
            videos.append(
                {
                    "id": video.id,
                    "tiktok_id": video.tiktok_id,
                    "author": video.author,
                    "title": video.title,
                    "duration": video.duration,
                    "views": video.views,
                    "likes": video.likes,
                    "thumbnail_url": video.thumbnail_url,
                    "local_path": video.local_path,
                    "order_index": pv.order_index,
                }
            )

    # 최종 영상 정보
    final_video = None
    if project.final_video_id:
        fv = db.query(FinalVideo).filter(FinalVideo.id == project.final_video_id).first()
        if fv:
            final_video = {
                "id": fv.id,
                "file_path": fv.file_path,
                "file_size": fv.file_size,
                "duration": fv.duration,
                "thumbnail_path": fv.thumbnail_path,
                "status": fv.status,
                "created_at": fv.created_at,
            }

    return ProjectDetailResponse(
        id=project.id,
        title=project.title,
        description=project.description,
        status=project.status,
        render_progress=project.render_progress,
        created_at=project.created_at,
        updated_at=project.updated_at,
        selected_videos=videos,
        final_video=final_video,
        error_message=project.error_message,
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, project_data: ProjectUpdate, db: Session = Depends(get_db)):
    """
    프로젝트 정보 수정

    Args:
        project_id: 프로젝트 ID
        project_data: 수정할 데이터
        db: 데이터베이스 세션

    Returns:
        ProjectResponse: 수정된 프로젝트 정보
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 업데이트
    if project_data.title is not None:
        project.title = project_data.title
    if project_data.description is not None:
        project.description = project_data.description

    project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(project)

    return ProjectResponse(
        id=project.id,
        title=project.title,
        description=project.description,
        status=project.status,
        render_progress=project.render_progress,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.post("/{project_id}/videos")
async def add_videos_to_project(project_id: str, video_ids: List[str], db: Session = Depends(get_db)):
    """
    프로젝트에 영상 추가 (순서대로)

    Args:
        project_id: 프로젝트 ID
        video_ids: 추가할 영상 ID 리스트 (순서 유지)
        db: 데이터베이스 세션

    Returns:
        dict: 추가된 영상 정보
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 기존 영상 제거
    db.query(ProjectVideo).filter(ProjectVideo.project_id == project_id).delete()

    # 새로운 영상 추가
    added_videos = []
    for index, video_id in enumerate(video_ids):
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail=f"Video not found: {video_id}")

        project_video = ProjectVideo(
            id=str(uuid.uuid4()),
            project_id=project_id,
            video_id=video_id,
            order_index=index,
        )
        db.add(project_video)
        added_videos.append(
            {
                "video_id": video_id,
                "order_index": index,
                "title": video.title,
                "thumbnail_url": video.thumbnail_url,
            }
        )

    project.updated_at = datetime.utcnow()
    db.commit()

    return {"project_id": project_id, "total_videos": len(added_videos), "videos": added_videos}


@router.post("/{project_id}/generate")
async def generate_video(
    project_id: str, music_path: str = None, db: Session = Depends(get_db)
):
    """
    랭킹 영상 생성 시작

    Args:
        project_id: 프로젝트 ID
        music_path: 배경음악 파일 경로 (선택)
        db: 데이터베이스 세션

    Returns:
        dict: 작업 정보
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 선택된 영상 확인
    project_videos = (
        db.query(ProjectVideo)
        .filter(ProjectVideo.project_id == project_id)
        .order_by(ProjectVideo.order_index)
        .all()
    )

    if not project_videos:
        raise HTTPException(status_code=400, detail="No videos selected for this project")

    if len(project_videos) < 3:
        raise HTTPException(
            status_code=400, detail="At least 3 videos are required for ranking video"
        )

    # 영상 ID 리스트 추출
    video_ids = [pv.video_id for pv in project_videos]

    # Celery 백그라운드 작업 시작
    task = generate_ranking_video_task.apply_async(
        args=[project_id, video_ids, music_path], queue="video_processing"
    )

    # task_id 저장
    project.task_id = task.id
    project.status = "queued"
    db.commit()

    return {
        "project_id": project_id,
        "task_id": task.id,
        "status": "queued",
        "message": "Video generation started",
    }


@router.get("/{project_id}/status")
async def get_project_status(project_id: str, db: Session = Depends(get_db)):
    """
    프로젝트 작업 진행 상황 조회

    Args:
        project_id: 프로젝트 ID
        db: 데이터베이스 세션

    Returns:
        dict: 작업 상태 정보
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Celery 작업 상태 조회
    if project.task_id:
        task = celery_app.AsyncResult(project.task_id)
        task_state = task.state
        task_info = task.info if task.info else {}

        return {
            "project_id": project.id,
            "status": project.status,
            "task_state": task_state,
            "task_info": task_info,
            "render_progress": project.render_progress,
            "error_message": project.error_message,
        }
    else:
        return {
            "project_id": project.id,
            "status": project.status,
            "task_state": "PENDING",
            "render_progress": project.render_progress,
            "error_message": project.error_message,
        }


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str, db: Session = Depends(get_db)):
    """
    프로젝트 삭제 (관련 파일은 유지)

    Args:
        project_id: 프로젝트 ID
        db: 데이터베이스 세션

    Returns:
        None (204 No Content)
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Celery 작업 취소 (진행 중인 경우)
    if project.task_id and project.status == "processing":
        celery_app.control.revoke(project.task_id, terminate=True)

    # 프로젝트 레코드 삭제 (CASCADE로 ProjectVideo도 자동 삭제)
    db.delete(project)
    db.commit()

    return None
