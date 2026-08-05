from celery import Celery

from backend.core.config import settings

celery_app = Celery(
    "scriptloom",
    broker=settings.CELERY_BROKER_URL or settings.REDIS_URL,
    backend=settings.CELERY_RESULT_BACKEND or settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Explicitly import tasks so Celery always registers them.
import backend.jobs.tasks.video_processing
import backend.jobs.tasks.webhook_delivery