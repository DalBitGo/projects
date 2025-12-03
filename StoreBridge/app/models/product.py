"""Product-related database models."""

import enum
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class State(str, enum.Enum):
    """Registration state machine states."""

    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    UPLOADING = "UPLOADING"
    REGISTERING = "REGISTERING"
    COMPLETED = "COMPLETED"
    RETRYING = "RETRYING"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    FAILED = "FAILED"


class JobStatus(str, enum.Enum):
    """Job status."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class JobType(str, enum.Enum):
    """Job type."""

    IMPORT = "IMPORT"
    SYNC_PRICE = "SYNC_PRICE"
    SYNC_INVENTORY = "SYNC_INVENTORY"


class Product(Base):
    """Domeggook product raw data."""

    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    domeggook_item_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    images: Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    options: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    raw_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("idx_products_domeggook_id", "domeggook_item_id"),
        Index("idx_products_category", "category"),
        Index(
            "idx_products_name_gin",
            "name",
            postgresql_using="gin",
            postgresql_ops={"name": "gin_trgm_ops"},
        ),
        CheckConstraint("price >= 0", name="check_price_non_negative"),
    )


class ProductRegistration(Base):
    """Naver product registration tracking."""

    __tablename__ = "product_registrations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    state: Mapped[State] = mapped_column(
        Enum(State, native_enum=False), nullable=False, default=State.PENDING, index=True
    )
    naver_product_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    seller_product_code: Mapped[Optional[str]] = mapped_column(
        String(100), unique=True, nullable=True
    )
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    error_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    registration_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("idx_registrations_product_id", "product_id"),
        Index("idx_registrations_state", "state"),
        Index("idx_registrations_job_id", "job_id"),
        Index("idx_registrations_job_state", "job_id", "state"),
        Index(
            "idx_registrations_pending",
            "state",
            postgresql_where=(state == State.PENDING),
        ),
        Index(
            "idx_registrations_manual_review",
            "state",
            "created_at",
            postgresql_where=(state == State.MANUAL_REVIEW),
        ),
    )


class Job(Base):
    """Bulk import/sync job."""

    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    type: Mapped[JobType] = mapped_column(
        Enum(JobType, native_enum=False), nullable=False, index=True
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, native_enum=False), nullable=False, default=JobStatus.PENDING, index=True
    )
    config: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    total_count: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    error_summary: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("idx_jobs_type", "type"),
        Index("idx_jobs_status", "status"),
        Index("idx_jobs_created_at", "created_at"),
    )


class CategoryMapping(Base):
    """Domeggook to Naver category mapping."""

    __tablename__ = "category_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domeggook_category: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    naver_leaf_category_id: Mapped[str] = mapped_column(String(50), nullable=False)
    required_attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    default_attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    is_active: Mapped[bool] = mapped_column(Integer, default=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("idx_category_mappings_domeggook", "domeggook_category"),
        Index("idx_category_mappings_active", "is_active", "domeggook_category"),
    )
