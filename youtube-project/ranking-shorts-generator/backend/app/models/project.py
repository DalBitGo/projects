from sqlalchemy import Column, String, JSON, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)  # created, processing, completed, failed
    settings = Column(JSON, nullable=True)
    task_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class ProjectVideo(Base):
    __tablename__ = "project_videos"

    project_id = Column(String, ForeignKey("projects.id"), primary_key=True)
    video_id = Column(String, ForeignKey("videos.id"), primary_key=True)
    rank_order = Column(Integer, nullable=False)


class FinalVideo(Base):
    __tablename__ = "final_videos"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"))
    file_path = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
