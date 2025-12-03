from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
from app.db.base import Base


class Search(Base):
    __tablename__ = "searches"

    id = Column(String, primary_key=True)
    keyword = Column(String, nullable=False)
    status = Column(String, nullable=False)  # processing, completed, failed
    total_found = Column(Integer, default=0)
    task_id = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
