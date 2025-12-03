from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SearchCreate(BaseModel):
    keyword: str
    limit: int = 30


class SearchResponse(BaseModel):
    id: str
    keyword: str
    status: str
    total_found: int
    task_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SearchDetailResponse(BaseModel):
    id: str
    keyword: str
    status: str
    total_found: int
    task_id: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    videos: List[dict] = []

    class Config:
        from_attributes = True


class VideoInfo(BaseModel):
    id: str
    tiktok_id: str
    thumbnail_url: str
    title: str
    description: Optional[str]
    views: int
    likes: int
    comments: int
    shares: int
    duration: int
    download_url: str
    author_username: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SearchResultResponse(BaseModel):
    search_id: str
    status: str
    keyword: str
    total_found: int
    videos: List[VideoInfo]


class SearchProgressResponse(BaseModel):
    search_id: str
    status: str
    progress: int
    current_step: str
    estimated_time: Optional[int]
