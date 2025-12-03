from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str
    selected_videos: List[str]
    video_order: List[int]
    settings: Optional[Dict] = None


class ProjectResponse(BaseModel):
    project_id: str
    name: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectDetail(BaseModel):
    project_id: str
    name: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    videos: List[dict]
    settings: Optional[Dict]
    final_video: Optional[dict]


class ProjectDetailResponse(BaseModel):
    id: str
    name: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    videos: List[dict] = []
    settings: Optional[Dict] = None
    task_id: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    settings: Optional[Dict] = None


class GenerateVideoResponse(BaseModel):
    task_id: str
    project_id: str
    status: str
    message: str


class ProjectStatusResponse(BaseModel):
    project_id: str
    status: str
    progress: int
    current_step: str
    steps_completed: List[str]
    steps_pending: List[str]
    estimated_time: Optional[int]


class ProjectListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    projects: List[ProjectResponse]
