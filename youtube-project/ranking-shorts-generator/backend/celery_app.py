"""
Celery Application Configuration
Based on design doc: docs/03-tech-stack.md
"""
from celery import Celery
from app.config import settings

# Celery 앱 생성
celery_app = Celery(
    "ranking_shorts_generator",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.core.tasks"],
)

# Celery 설정
celery_app.conf.update(
    # 작업 설정
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # 타임아웃 설정
    task_soft_time_limit=3600,  # 1시간 소프트 제한
    task_time_limit=7200,  # 2시간 하드 제한
    # 재시도 설정
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # 결과 설정
    result_expires=86400,  # 24시간 후 결과 삭제
    result_backend_transport_options={
        "master_name": "mymaster",
        "visibility_timeout": 3600,
    },
    # 워커 설정
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    # 이벤트 설정
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Task routes (disabled for simplicity - all tasks use default queue)
# celery_app.conf.task_routes = {
#     "app.core.tasks.scrape_tiktok_task": {"queue": "scraping"},
#     "app.core.tasks.download_video_task": {"queue": "download"},
#     "app.core.tasks.generate_ranking_video_task": {"queue": "video_processing"},
# }

# Beat schedule (주기적 작업이 필요한 경우)
celery_app.conf.beat_schedule = {
    # 예: 임시 파일 정리 (매일 자정)
    "cleanup-temp-files": {
        "task": "app.core.tasks.cleanup_temp_files",
        "schedule": 86400.0,  # 24시간
    },
}
