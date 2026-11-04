"""
Voice training (cloning) pipeline.

Sends a profile's accepted recordings to the configured hosted TTS provider and
stores the returned voice reference. Runs synchronously so it can be used both from
a FastAPI background task (task_mode=inline) and from a Celery worker.
"""

import json
import logging
from datetime import datetime, timezone

import redis as redis_client
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.recording import Recording, RecordingStatus
from app.models.voice_profile import ProfileStatus, VoiceProfile
from app.services.storage_service import get_storage_service
from app.voice_engine.providers import TTSError, get_provider

logger = logging.getLogger(__name__)
settings = get_settings()

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(settings.database_url_sync, pool_pre_ping=True)
    return _engine


def _publish(profile_id: str, progress: float, step: str, status: str = "training") -> None:
    """Best-effort realtime update; the DB is the source of truth."""
    try:
        r = redis_client.Redis.from_url(settings.redis_url, socket_connect_timeout=0.5)
        r.publish(
            f"training:{profile_id}",
            json.dumps({"progress": progress, "step": step, "status": status}),
        )
    except Exception:  # noqa: BLE001
        pass


def _set_progress(db: Session, profile: VoiceProfile, progress: float, step: str) -> None:
    profile.training_progress = progress
    db.commit()
    _publish(str(profile.id), progress, step)


def run_training(profile_id: str) -> dict:
    """Clone the voice for a profile. Updates profile status/progress in the DB."""
    storage = get_storage_service()
    with Session(_get_engine()) as db:
        profile = db.execute(
            select(VoiceProfile).where(VoiceProfile.id == profile_id),
        ).scalar_one()
        try:
            profile.status = ProfileStatus.TRAINING
            profile.training_error = None
            profile.training_started_at = datetime.now(timezone.utc)
            _set_progress(db, profile, 0.05, "Collecting recordings")

            recordings = db.execute(
                select(Recording).where(
                    Recording.voice_profile_id == profile.id,
                    Recording.status.in_([RecordingStatus.UPLOADED, RecordingStatus.PROCESSED]),
                ).order_by(Recording.prompt_index),
            ).scalars().all()
            if len(recordings) < settings.min_recordings_for_training:
                raise TTSError(
                    f"Not enough valid recordings: {len(recordings)} "
                    f"(need {settings.min_recordings_for_training})",
                )

            samples = []
            for i, rec in enumerate(recordings):
                path = rec.processed_file_path or rec.original_file_path
                samples.append(storage.download_file(path))
                _set_progress(db, profile, 0.05 + 0.35 * (i + 1) / len(recordings), "Loading audio")

            _set_progress(db, profile, 0.5, "Cloning voice")
            provider = get_provider()
            old_ref = profile.model_path
            voice_id = provider.create_voice(profile.name, samples)
            if old_ref and old_ref.startswith(provider.name + ":"):
                provider.delete_voice(old_ref.split(":", 1)[1])

            profile.model_path = f"{provider.name}:{voice_id}"
            profile.status = ProfileStatus.READY
            profile.training_progress = 1.0
            profile.training_completed_at = datetime.now(timezone.utc)
            db.commit()
            _publish(profile_id, 1.0, "Voice ready", status="ready")
            return {"profile_id": profile_id, "status": "ready"}

        except Exception as e:  # noqa: BLE001
            logger.exception("Training failed for profile %s", profile_id)
            db.rollback()
            profile = db.execute(
                select(VoiceProfile).where(VoiceProfile.id == profile_id),
            ).scalar_one()
            profile.status = ProfileStatus.FAILED
            profile.training_error = str(e) if isinstance(e, TTSError | ValueError) else (
                "Training failed unexpectedly. Please try again."
            )
            db.commit()
            _publish(profile_id, 0.0, "Training failed", status="failed")
            return {"profile_id": profile_id, "status": "failed"}
