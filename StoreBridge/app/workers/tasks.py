"""Celery tasks for product import and registration."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.connectors.domeggook_client import DomeggookClient
from app.connectors.naver_client import NaverClient
from app.models import Job, JobStatus, Product, ProductRegistration, State
from app.services.option_mapper import OptionMapper
from app.validators.product_validator import ProductValidator
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)

# Create async engine for database
engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def get_async_session() -> AsyncSession:
    """Get async database session."""
    return async_session_maker()


@celery_app.task(bind=True, name="app.workers.tasks.import_products_task")
def import_products_task(self, job_id: str) -> Dict[str, Any]:
    """
    Import products from Domeggook and queue for registration.

    Args:
        job_id: Job UUID string

    Returns:
        Task result with statistics
    """
    import asyncio

    logger.info(f"Starting import job: {job_id}")

    try:
        result = asyncio.run(_import_products_async(job_id))
        logger.info(f"Import job {job_id} completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Import job {job_id} failed: {e}", exc_info=True)
        asyncio.run(_mark_job_failed(job_id, str(e)))
        raise


async def _import_products_async(job_id: str) -> Dict[str, Any]:
    """Async implementation of product import."""
    async with get_async_session() as db:
        # Get job
        stmt = select(Job).where(Job.id == uuid.UUID(job_id))
        result = await db.execute(stmt)
        job = result.scalar_one_or_none()

        if not job:
            raise ValueError(f"Job not found: {job_id}")

        # Update job status to RUNNING
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(timezone.utc)
        await db.commit()

        try:
            # Extract config
            config = job.config
            source = config.get("source", "domeggook")
            filter_config = config.get("filter", {})
            limit = config.get("limit", 100)
            auto_register = config.get("auto_register", True)

            # Fetch products from Domeggook
            async with DomeggookClient() as client:
                response = await client.get_item_list(
                    page=1,
                    page_size=min(limit, 100),
                    category=filter_config.get("category"),
                    keyword=filter_config.get("keyword"),
                    price_min=filter_config.get("price_min"),
                    price_max=filter_config.get("price_max"),
                )

            items = response.get("items", [])
            total_count = len(items)

            # Update job total count
            job.total_count = total_count
            await db.commit()

            # Process each product
            success_count = 0
            failed_count = 0
            error_summary: Dict[str, int] = {}

            for item in items[:limit]:
                try:
                    # Create Product record
                    product = Product(
                        domeggook_item_id=item.get("item_id", str(uuid.uuid4())),
                        name=item.get("item_name", "Unknown"),
                        price=item.get("price", 0),
                        category=item.get("category"),
                        images=item.get("images", []),
                        options={"raw": item.get("options", [])},
                        raw_data=item,
                    )
                    db.add(product)
                    await db.flush()

                    # Create ProductRegistration record
                    registration = ProductRegistration(
                        product_id=product.id,
                        job_id=uuid.UUID(job_id),
                        state=State.PENDING,
                        seller_product_code=f"DG-{product.domeggook_item_id}",
                    )
                    db.add(registration)
                    await db.commit()

                    success_count += 1

                    # Queue registration task if auto_register
                    if auto_register:
                        register_product_task.delay(str(product.id))

                except Exception as e:
                    logger.error(f"Failed to process product {item.get('item_id')}: {e}")
                    failed_count += 1
                    error_type = type(e).__name__
                    error_summary[error_type] = error_summary.get(error_type, 0) + 1

            # Update job statistics
            job.success_count = success_count
            job.failed_count = failed_count
            job.error_summary = error_summary
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now(timezone.utc)
            await db.commit()

            return {
                "job_id": job_id,
                "total_count": total_count,
                "success_count": success_count,
                "failed_count": failed_count,
                "error_summary": error_summary,
            }

        except Exception as e:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now(timezone.utc)
            job.error_summary = {"error": str(e)}
            await db.commit()
            raise


async def _mark_job_failed(job_id: str, error_message: str) -> None:
    """Mark job as failed."""
    async with get_async_session() as db:
        stmt = select(Job).where(Job.id == uuid.UUID(job_id))
        result = await db.execute(stmt)
        job = result.scalar_one_or_none()

        if job:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now(timezone.utc)
            job.error_summary = {"error": error_message}
            await db.commit()


@celery_app.task(bind=True, name="app.workers.tasks.register_product_task")
def register_product_task(self, product_id: str) -> Dict[str, Any]:
    """
    Register a single product to Naver Smart Store.

    Args:
        product_id: Product UUID string

    Returns:
        Task result with registration status
    """
    import asyncio

    logger.info(f"Starting product registration: {product_id}")

    try:
        result = asyncio.run(_register_product_async(product_id))
        logger.info(f"Product {product_id} registered: {result}")
        return result
    except Exception as e:
        logger.error(f"Product {product_id} registration failed: {e}", exc_info=True)
        asyncio.run(_mark_registration_failed(product_id, str(e)))
        raise


async def _register_product_async(product_id: str) -> Dict[str, Any]:
    """Async implementation of product registration."""
    async with get_async_session() as db:
        # Get product and registration
        stmt = select(Product).where(Product.id == uuid.UUID(product_id))
        result = await db.execute(stmt)
        product = result.scalar_one_or_none()

        if not product:
            raise ValueError(f"Product not found: {product_id}")

        stmt = select(ProductRegistration).where(
            ProductRegistration.product_id == uuid.UUID(product_id)
        )
        result = await db.execute(stmt)
        registration = result.scalar_one_or_none()

        if not registration:
            raise ValueError(f"Registration not found for product: {product_id}")

        try:
            # Update state to VALIDATED
            registration.state = State.VALIDATED
            await db.commit()

            # Validate product
            validator = ProductValidator()
            validation_result = validator.validate(
                {
                    "name": product.name,
                    "price": product.price,
                    "description": product.raw_data.get("description", ""),
                    "images": product.images,
                    "category": product.category,
                    "options": product.options.get("raw", []) if product.options else [],
                }
            )

            if not validation_result.is_valid:
                # Move to manual review
                registration.state = State.MANUAL_REVIEW
                registration.error_message = "; ".join(validation_result.errors)
                await db.commit()
                return {
                    "product_id": product_id,
                    "status": "manual_review",
                    "errors": validation_result.errors,
                }

            # Parse options
            option_mapper = OptionMapper()
            raw_options = product.options.get("raw", []) if product.options else []
            parsed_options = option_mapper.parse(raw_options)
            naver_options = option_mapper.to_naver_format(parsed_options)

            # Prepare Naver product data
            naver_product_data = {
                "originProduct": {
                    "name": product.name[:100],  # Naver has 100 char limit
                    "salePrice": product.price,
                    "categoryId": "50000000",  # TODO: Category mapping
                    "images": [{"url": url} for url in product.images[:10]],
                    "detailContent": product.raw_data.get("description", ""),
                    "saleType": "NEW",
                    "saleStartDate": datetime.now(timezone.utc).isoformat(),
                    "sellerProductCode": registration.seller_product_code,
                    **naver_options,
                }
            }

            # Update state to REGISTERING
            registration.state = State.REGISTERING
            await db.commit()

            # Register to Naver
            async with NaverClient() as naver_client:
                naver_response = await naver_client.register_product(naver_product_data)

            # Update registration with Naver product ID
            registration.state = State.COMPLETED
            registration.naver_product_id = naver_response.get("originProductNo")
            await db.commit()

            return {
                "product_id": product_id,
                "status": "completed",
                "naver_product_id": registration.naver_product_id,
            }

        except Exception as e:
            # Increment retry count
            registration.retry_count += 1

            if registration.retry_count >= 3:
                # Max retries reached, move to FAILED
                registration.state = State.FAILED
                registration.error_message = str(e)
            else:
                # Move to RETRYING
                registration.state = State.RETRYING
                registration.error_message = str(e)
                # Re-queue task with exponential backoff
                self.retry(countdown=60 * (2**registration.retry_count), max_retries=3)

            await db.commit()
            raise


async def _mark_registration_failed(product_id: str, error_message: str) -> None:
    """Mark registration as failed."""
    async with get_async_session() as db:
        stmt = select(ProductRegistration).where(
            ProductRegistration.product_id == uuid.UUID(product_id)
        )
        result = await db.execute(stmt)
        registration = result.scalar_one_or_none()

        if registration:
            registration.state = State.FAILED
            registration.error_message = error_message
            await db.commit()


@celery_app.task(name="app.workers.tasks.update_job_status_task")
def update_job_status_task(job_id: str) -> Dict[str, Any]:
    """
    Update job status by checking all registrations.

    Args:
        job_id: Job UUID string

    Returns:
        Updated job statistics
    """
    import asyncio

    logger.info(f"Updating job status: {job_id}")

    try:
        result = asyncio.run(_update_job_status_async(job_id))
        return result
    except Exception as e:
        logger.error(f"Failed to update job status {job_id}: {e}", exc_info=True)
        raise


async def _update_job_status_async(job_id: str) -> Dict[str, Any]:
    """Async implementation of job status update."""
    from sqlalchemy import func

    async with get_async_session() as db:
        # Get job
        stmt = select(Job).where(Job.id == uuid.UUID(job_id))
        result = await db.execute(stmt)
        job = result.scalar_one_or_none()

        if not job:
            raise ValueError(f"Job not found: {job_id}")

        # Count registrations by state
        stmt = (
            select(
                ProductRegistration.state,
                func.count(ProductRegistration.id).label("count"),
            )
            .where(ProductRegistration.job_id == uuid.UUID(job_id))
            .group_by(ProductRegistration.state)
        )
        result = await db.execute(stmt)
        state_counts = {row.state: row.count for row in result}

        # Calculate success/failed counts
        success_count = state_counts.get(State.COMPLETED, 0)
        failed_count = state_counts.get(State.FAILED, 0)
        manual_review_count = state_counts.get(State.MANUAL_REVIEW, 0)

        # Update job
        job.success_count = success_count
        job.failed_count = failed_count + manual_review_count

        # Check if all registrations are complete
        pending_count = sum(
            state_counts.get(state, 0)
            for state in [State.PENDING, State.VALIDATED, State.UPLOADING, State.REGISTERING, State.RETRYING]
        )

        if pending_count == 0:
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now(timezone.utc)

        await db.commit()

        return {
            "job_id": job_id,
            "status": job.status.value,
            "success_count": success_count,
            "failed_count": failed_count,
            "manual_review_count": manual_review_count,
            "state_counts": {state.value: count for state, count in state_counts.items()},
        }
