"""Celery application configuration."""

from celery import Celery

from app.config import settings

# Create Celery app
celery_app = Celery(
    "storebridge",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"],
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes max per task
    task_soft_time_limit=1500,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,  # One task at a time for rate limiting
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks (prevent memory leaks)
    task_acks_late=True,  # Acknowledge tasks after completion
    task_reject_on_worker_lost=True,  # Reject tasks if worker dies
    result_expires=3600,  # Keep results for 1 hour
    broker_connection_retry_on_startup=True,
)

# Task routing (optional - for multiple queues)
celery_app.conf.task_routes = {
    "app.workers.tasks.import_products_task": {"queue": "import"},
    "app.workers.tasks.register_product_task": {"queue": "register"},
    "app.workers.tasks.update_job_status_task": {"queue": "default"},
}
