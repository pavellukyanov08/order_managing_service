from celery import Celery

from app.settings import celery_settings


celery_app = Celery(
    "order_managing_service",
    broker=celery_settings.BROKER_URL,
    backend=celery_settings.RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_retry_delay=5,
    task_max_retries=3,
    broker_connection_retry_on_startup=True,
)

celery_app.conf.task_routes = {
    "app.api.orders.tasks.*": {"queue": "orders"},
}

celery_app.autodiscover_tasks(["app.api.orders.tasks"])