"""Job API routes."""

import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Job, JobStatus, JobType

router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobConfig(BaseModel):
    """Job configuration."""

    source: str = Field(..., description="Source platform (e.g., 'domeggook')")
    filter: Optional[Dict[str, Any]] = Field(None, description="Filter criteria")
    limit: Optional[int] = Field(None, description="Max items to import")
    auto_register: bool = Field(True, description="Auto-register without manual review")
    priority: str = Field("normal", description="Job priority (normal, high, urgent)")


class CreateJobRequest(BaseModel):
    """Create job request."""

    type: JobType = Field(..., description="Job type")
    config: JobConfig = Field(..., description="Job configuration")


class JobResponse(BaseModel):
    """Job response."""

    job_id: str
    type: JobType
    status: JobStatus
    total_count: int
    success_count: int
    failed_count: int
    config: Dict[str, Any]
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@router.post("", status_code=201)
async def create_job(
    request: CreateJobRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Create a new bulk import/sync job.

    Args:
        request: Job creation request
        db: Database session

    Returns:
        {
            "success": True,
            "data": {
                "job_id": "uuid",
                "type": "IMPORT",
                "status": "PENDING",
                "total_count": 0,
                "estimated_duration_minutes": 15
            }
        }
    """
    # Create job record
    job = Job(
        type=request.type,
        status=JobStatus.PENDING,
        config=request.config.model_dump(),
        total_count=0,
        success_count=0,
        failed_count=0,
    )

    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Enqueue Celery task to process job
    from app.workers.tasks import import_products_task
    import_products_task.delay(str(job.id))

    return {
        "success": True,
        "data": {
            "job_id": str(job.id),
            "type": job.type.value,
            "status": job.status.value,
            "total_count": job.total_count,
            "estimated_duration_minutes": 15,  # TODO: Calculate based on config
        },
    }


@router.get("/{job_id}")
async def get_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get job status and progress.

    Args:
        job_id: Job UUID
        db: Database session

    Returns:
        {
            "success": True,
            "data": {
                "job_id": "uuid",
                "status": "RUNNING",
                "statistics": {
                    "total_count": 100,
                    "success_count": 45,
                    "failed_count": 3,
                    "progress_percent": 48.0
                },
                "error_summary": {
                    "CATEGORY_MISMATCH": 2,
                    "FORBIDDEN_WORD": 1
                },
                "timeline": {
                    "created_at": "2025-10-16T10:00:00Z",
                    "started_at": "2025-10-16T10:00:05Z",
                    "duration_seconds": 600,
                    "estimated_remaining_seconds": 650
                }
            }
        }
    """
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if job is None:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    # Calculate progress
    progress_percent = 0.0
    if job.total_count > 0:
        completed = job.success_count + job.failed_count
        progress_percent = (completed / job.total_count) * 100

    # Calculate duration
    duration_seconds = None
    if job.started_at:
        if job.completed_at:
            duration_seconds = (job.completed_at - job.started_at).total_seconds()
        else:
            from datetime import datetime, timezone

            now = datetime.now(timezone.utc)
            duration_seconds = (now - job.started_at).total_seconds()

    return {
        "success": True,
        "data": {
            "job_id": str(job.id),
            "type": job.type.value,
            "status": job.status.value,
            "statistics": {
                "total_count": job.total_count,
                "success_count": job.success_count,
                "failed_count": job.failed_count,
                "progress_percent": round(progress_percent, 2),
            },
            "error_summary": job.error_summary or {},
            "timeline": {
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "duration_seconds": duration_seconds,
            },
            "config": job.config,
        },
    }


@router.get("")
async def list_jobs(
    type: Optional[JobType] = Query(None, description="Filter by job type"),
    status: Optional[JobStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    List jobs with pagination and filtering.

    Args:
        type: Filter by job type
        status: Filter by status
        page: Page number (1-indexed)
        page_size: Items per page (max 100)
        db: Database session

    Returns:
        {
            "success": True,
            "data": {
                "items": [...],
                "pagination": {
                    "page": 1,
                    "page_size": 20,
                    "total": 100
                }
            }
        }
    """
    stmt = select(Job)

    if type:
        stmt = stmt.where(Job.type == type)
    if status:
        stmt = stmt.where(Job.status == status)

    # Count total
    from sqlalchemy import func

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size).order_by(Job.created_at.desc())

    result = await db.execute(stmt)
    jobs = result.scalars().all()

    items = []
    for job in jobs:
        items.append(
            {
                "job_id": str(job.id),
                "type": job.type.value,
                "status": job.status.value,
                "total_count": job.total_count,
                "success_count": job.success_count,
                "failed_count": job.failed_count,
                "created_at": job.created_at.isoformat() if job.created_at else None,
            }
        )

    return {
        "success": True,
        "data": {
            "items": items,
            "pagination": {"page": page, "page_size": page_size, "total": total},
        },
    }


@router.delete("/{job_id}")
async def cancel_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Cancel a running job.

    Args:
        job_id: Job UUID
        db: Database session

    Returns:
        {"success": True}
    """
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if job is None:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    if job.status not in [JobStatus.PENDING, JobStatus.RUNNING]:
        raise HTTPException(
            status_code=400, detail=f"Cannot cancel job with status: {job.status}"
        )

    job.status = JobStatus.CANCELLED
    await db.commit()

    # Revoke Celery tasks
    from app.workers.celery_app import celery_app
    celery_app.control.revoke(str(job.id), terminate=True)

    return {"success": True}
