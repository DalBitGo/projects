from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VideoApprove(BaseModel):
    approved: bool
    notes: Optional[str] = None


class VideoResponse(BaseModel):
    video_id: str
    status: str
    moved_to: Optional[str]
    approved_at: Optional[datetime]


class VideoMetadata(BaseModel):
    id: str
    file_path: str
    thumbnail_path: Optional[str]
    file_size: int
    duration: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class VideoDetailResponse(BaseModel):
    id: str
    tiktok_id: str
    thumbnail_url: str
    title: str
    description: Optional[str] = None
    views: int
    likes: int
    comments: int
    shares: int
    duration: int
    download_url: str
    author_username: Optional[str] = None
    file_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
