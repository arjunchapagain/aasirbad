"""
Synthesis service.

Generates speech with the configured hosted TTS provider from a cloned voice,
enforcing free-tier monthly character limits.
"""

import asyncio
import io
import uuid
import wave
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.usage import SynthesisUsage
from app.services.storage_service import get_storage_service
from app.services.voice_service import VoiceService
from app.voice_engine.providers import TTSError, get_provider

settings = get_settings()


def _month_start() -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _duration_seconds(audio: bytes, media_type: str) -> float:
    if media_type == "audio/wav":
        with wave.open(io.BytesIO(audio)) as w:
            return w.getnframes() / w.getframerate()
    # MP3: rough estimate from typical 128 kbps stream
    return len(audio) * 8 / 128_000


class SynthesisService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.storage = get_storage_service()
        self.voice_service = VoiceService(db)

    async def chars_used_this_month(self, user_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.coalesce(func.sum(SynthesisUsage.characters), 0)).where(
                SynthesisUsage.user_id == user_id,
                SynthesisUsage.created_at >= _month_start(),
            ),
        )
        return int(result.scalar_one())

    async def usage(self, user_id: uuid.UUID) -> dict:
        used = await self.chars_used_this_month(user_id)
        limit = settings.monthly_synthesis_chars
        return {"used": used, "limit": limit, "remaining": max(0, limit - used)}

    async def synthesize(self, text: str, voice_profile_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        text = text.strip()
        if not text:
            raise ValueError("Text is empty")
        if len(text) > settings.max_synthesis_chars_per_request:
            raise ValueError(
                f"Text too long (max {settings.max_synthesis_chars_per_request} characters)",
            )

        profile = await self.voice_service.get_ready_profile(voice_profile_id, user_id)
        if not profile or not profile.model_path or ":" not in profile.model_path:
            raise ValueError("Voice profile not found or not ready for synthesis")

        used = await self.chars_used_this_month(user_id)
        if used + len(text) > settings.monthly_synthesis_chars:
            raise PermissionError(
                f"Monthly free limit reached ({used}/{settings.monthly_synthesis_chars} "
                "characters). It resets at the start of next month.",
            )

        provider_name, voice_id = profile.model_path.split(":", 1)
        provider = get_provider()
        if provider.name != provider_name:
            raise ValueError(
                "This voice was created with a different TTS provider. Please retrain it.",
            )

        try:
            audio = await asyncio.to_thread(provider.synthesize, text, voice_id)
        except TTSError as e:
            raise ValueError(str(e)) from e

        key = self.storage.upload_audio(
            file_bytes=audio,
            voice_profile_id=f"synth-{voice_profile_id}",
            filename=f"{uuid.uuid4().hex}{provider.audio_ext}",
        )
        self.db.add(SynthesisUsage(user_id=user_id, characters=len(text)))
        await self.db.flush()

        return {
            "audio_url": self.storage.get_presigned_url(key, expires_in=3600),
            "duration_seconds": round(_duration_seconds(audio, provider.media_type), 2),
            "text": text,
            "voice_profile_id": voice_profile_id,
        }
