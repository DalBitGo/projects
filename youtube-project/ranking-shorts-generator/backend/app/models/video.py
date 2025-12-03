from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, DateTime
from datetime import datetime
from app.db.base import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True)
    search_id = Column(String, ForeignKey("searches.id"))
    tiktok_id = Column(String, unique=True)
    thumbnail_url = Column(Text)
    title = Column(Text)
    description = Column(Text, nullable=True)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    duration = Column(Integer)
    download_url = Column(Text)
    local_path = Column(Text, nullable=True)
    downloaded = Column(Boolean, default=False)
    author_username = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
