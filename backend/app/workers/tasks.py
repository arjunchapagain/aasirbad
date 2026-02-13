"""
Celery tasks for voice processing.

These tasks run asynchronously on worker nodes:
- preprocess_recordings: Clean and prepare audio files
- train_voice_model: Extract voice conditioning latents
"""

import logging

import redis as redis_client

from app.config import get_settings
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)
settings = get_settings()


def _get_redis():
    """Get Redis connection for publishing training status updates."""
    return redis_client.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password or None,
        db=0,
    )


def _publish_progress(profile_id: str, progress: float, step: str, status: str = "training"):
    """Publish training progress via Redis Pub/Sub for WebSocket forwarding."""
    import json

    r = _get_redis()
    r.publish(
        f"training:{profile_id}",
        json.dumps({
            "profile_id": profile_id,
            "progress": progress,
            "step": step,
            "status": status,
        }),
    )


@celery_app.task(bind=True, name="app.workers.tasks.preprocess_recordings")
def preprocess_recordings(self, profile_id: str):
    """
    Preprocess all recordings for a voice profile.

    1. Download original recordings from S3
    2. Run preprocessing pipeline (noise reduction, normalization, VAD)
    3. Upload processed audio to S3
    4. Update recording metadata in DB
    """
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session

    from app.models.recording import Recording, RecordingStatus
    from app.services.storage_service import get_storage_service
    from app.voice_engine.preprocessor import AudioPreprocessor

    logger.info(f"Preprocessing recordings for profile {profile_id}")

    # Sync DB session (Celery workers use sync)
    engine = create_engine(settings.database_url_sync)
    storage = get_storage_service()
    preprocessor = AudioPreprocessor(target_sr=settings.audio_sample_rate)

    with Session(engine) as db:
        # Get all uploaded recordings
        recordings = db.execute(
            select(Recording).where(
                Recording.voice_profile_id == profile_id,
                Recording.status == RecordingStatus.UPLOADED,
            ),
        ).scalars().all()

        total = len(recordings)
        logger.info(f"Found {total} recordings to preprocess")

        for i, recording in enumerate(recordings):
            try:
                # Update progress
                progress = (i + 1) / total
                self.update_state(
                    state="PROGRESS",
                    meta={"current": i + 1, "total": total, "step": "preprocessing"},
                )
                _publish_progress(profile_id, progress * 0.3, f"Preprocessing {i+1}/{total}")

                # Download from S3
                audio_bytes = storage.download_file(recording.original_file_path)

                # Preprocess
                result = preprocessor.process(audio_bytes)

                # Upload processed audio
                processed_bytes = preprocessor.to_wav_bytes(result.audio, result.sample_rate)
                processed_key = storage.upload_processed_audio(processed_bytes, profile_id)

                # Update recording
                recording.processed_file_path = processed_key
                recording.status = RecordingStatus.PROCESSED
                recording.snr_db = result.quality_metrics["snr_db"]
                recording.rms_level = result.quality_metrics["rms_level"]
                recording.clipping_detected = result.quality_metrics["clipping_detected"]
                recording.silence_ratio = result.quality_metrics["silence_ratio"]
                recording.duration_seconds = result.duration_seconds

                db.commit()
                logger.info(f"Preprocessed recording {i+1}/{total}: {recording.id}")

            except Exception as e:
                logger.error(f"Failed to preprocess recording {recording.id}: {e}")
                recording.status = RecordingStatus.FAILED
                db.commit()

    return {"profile_id": profile_id, "processed": total}


@celery_app.task(bind=True, name="app.workers.tasks.train_voice_model")
def train_voice_model(self, profile_id: str):
    """
    Train a voice model (extract conditioning latents) for a profile.

    Full pipeline:
    1. Preprocess recordings if needed
    2. Download all processed audio
    3. Extract Tortoise TTS conditioning latents
    4. Upload model to S3
    5. Update profile status
    """
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session

    from app.models.recording import Recording, RecordingStatus
    from app.models.voice_profile import ProfileStatus, VoiceProfile
    from app.services.storage_service import get_storage_service
    from app.voice_engine.trainer import VoiceTrainer

    logger.info(f"Starting voice model training for profile {profile_id}")

    engine = create_engine(settings.database_url_sync)
    storage = get_storage_service()

    with Session(engine) as db:
        try:
            # Update profile status to training
            profile = db.execute(
                select(VoiceProfile).where(VoiceProfile.id == profile_id),
            ).scalar_one()

            profile.status = ProfileStatus.TRAINING
            db.commit()

            _publish_progress(profile_id, 0.05, "Starting training pipeline")

            # Step 1: Preprocess recordings first
            _publish_progress(profile_id, 0.1, "Preprocessing recordings")
            preprocess_recordings(profile_id)

            # Step 2: Download processed audio
            _publish_progress(profile_id, 0.35, "Downloading processed audio")

            recordings = db.execute(
                select(Recording).where(
                    Recording.voice_profile_id == profile_id,
                    Recording.status == RecordingStatus.PROCESSED,
                ),
            ).scalars().all()

            if len(recordings) < settings.min_recordings_for_training:
                raise ValueError(
                    f"Not enough valid recordings: {len(recordings)} "
                    f"(need {settings.min_recordings_for_training})",
                )

            audio_samples = []
            for rec in recordings:
                if rec.processed_file_path:
                    audio_bytes = storage.download_file(rec.processed_file_path)
                    audio_samples.append(audio_bytes)

            logger.info(f"Downloaded {len(audio_samples)} processed recordings")

            # Step 3: Train (extract conditioning latents)
            _publish_progress(profile_id, 0.4, "Extracting voice characteristics")

            trainer = VoiceTrainer(device=settings.torch_device)

            def training_progress_callback(progress: float, step: str):
                # Map trainer progress (0-1) to our range (0.4-0.9)
                overall_progress = 0.4 + (progress * 0.5)
                _publish_progress(profile_id, overall_progress, step)
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "progress": overall_progress,
                        "step": step,
                    },
                )

            model_bytes = trainer.train(
                audio_samples=audio_samples,
                progress_callback=training_progress_callback,
            )

            # Step 4: Upload model to S3
            _publish_progress(profile_id, 0.92, "Saving voice model")
            model_key = storage.upload_model(model_bytes, profile_id)

            # Step 5: Update profile
            _publish_progress(profile_id, 0.98, "Finalizing")

            profile = db.execute(
                select(VoiceProfile).where(VoiceProfile.id == profile_id),
            ).scalar_one()

            profile.status = ProfileStatus.READY
            profile.model_path = model_key
            profile.training_progress = 1.0
            from datetime import datetime, timezone
            profile.training_completed_at = datetime.now(timezone.utc)
            db.commit()

            _publish_progress(profile_id, 1.0, "Training complete!", status="ready")
            logger.info(f"Voice model training complete for profile {profile_id}")

            return {
                "profile_id": profile_id,
                "status": "ready",
                "model_key": model_key,
            }

        except Exception as e:
            logger.error(f"Training failed for profile {profile_id}: {e}")

            # Update profile with error
            profile = db.execute(
                select(VoiceProfile).where(VoiceProfile.id == profile_id),
            ).scalar_one()

            profile.status = ProfileStatus.FAILED
            profile.training_error = str(e)
            db.commit()

            _publish_progress(profile_id, 0.0, f"Training failed: {e}", status="failed")

            raise
