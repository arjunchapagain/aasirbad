"""Celery tasks (only used when TASK_MODE=celery)."""

from app.workers.celery_app import celery_app


@celery_app.task(bind=True, name="app.workers.tasks.train_voice_model")
def train_voice_model(self, profile_id: str):  # noqa: ARG001
    from app.services.training_service import run_training

    return run_training(profile_id)
