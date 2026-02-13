"""
Synthesis service.

Handles text-to-speech generation using trained voice models.
"""

import uuid
import tempfile
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.voice_profile import ProfileStatus, VoiceProfile
from app.services.storage_service import get_storage_service
from app.services.voice_service import VoiceService
from app.utils.audio import audio_to_wav_bytes

settings = get_settings()


class SynthesisService:
    """Service for voice synthesis operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.storage = get_storage_service()
        self.voice_service = VoiceService(db)

    async def synthesize(
        self,
        text: str,
        voice_profile_id: uuid.UUID,
        user_id: uuid.UUID,
        preset: str = "fast",
    ) -> dict:
        """
        Synthesize speech from text using a trained voice model.
        
        Args:
            text: Text to convert to speech
            voice_profile_id: ID of the trained voice profile
            user_id: ID of the requesting user
            preset: Tortoise TTS quality preset
            
        Returns:
            dict with audio_url, duration_seconds, etc.
        """
        # Verify profile is ready
        profile = await self.voice_service.get_ready_profile(voice_profile_id, user_id)
        if not profile:
            raise ValueError("Voice profile not found or not ready for synthesis")

        if not profile.model_path:
            raise ValueError("Voice model not found for this profile")

        # Import voice engine (lazy import to avoid loading torch at startup)
        from app.voice_engine.synthesizer import VoiceSynthesizer

        synthesizer = VoiceSynthesizer()

        # Download voice conditioning latents from S3
        model_bytes = self.storage.download_model(profile.model_path)

        # Generate speech
        audio, sr = synthesizer.generate_speech(
            text=text,
            voice_model_bytes=model_bytes,
            preset=preset,
        )

        # Convert to WAV bytes
        wav_bytes = audio_to_wav_bytes(audio, sr)

        # Upload synthesized audio to S3
        s3_key = f"synthesized/{voice_profile_id}/{uuid.uuid4().hex}.wav"
        self.storage.upload_audio(
            file_bytes=wav_bytes,
            voice_profile_id=str(voice_profile_id),
            filename=f"{uuid.uuid4().hex}.wav",
        )

        # Generate presigned URL for playback
        audio_url = self.storage.get_presigned_url(s3_key, expires_in=3600)

        duration = len(audio) / sr

        return {
            "audio_url": audio_url,
            "duration_seconds": round(duration, 2),
            "text": text,
            "voice_profile_id": voice_profile_id,
        }
