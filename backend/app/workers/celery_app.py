"""
Celery application configuration.

Defines the Celery app instance with Redis broker/backend,
task routing, and worker configuration.
"""

from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "voiceforge",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task settings
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3300,  # Soft limit at 55 minutes
    task_acks_late=True,  # Acknowledge after completion (crash safety)
    task_reject_on_worker_lost=True,

    # Worker settings
    worker_prefetch_multiplier=1,  # One task at a time (GPU-bound)
    worker_max_tasks_per_child=10,  # Restart worker after 10 tasks (memory leaks)
    worker_max_memory_per_child=8_000_000,  # 8GB limit

    # Task routing
    task_routes={
        "app.workers.tasks.train_voice_model": {"queue": "gpu"},
        "app.workers.tasks.preprocess_recordings": {"queue": "cpu"},
    },

    # Result settings
    result_expires=86400,  # 24 hours
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.workers"])
