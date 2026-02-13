"""
Recording service.

Handles audio file upload, preprocessing, and quality checks.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.recording import Recording, RecordingStatus
from app.models.voice_profile import ProfileStatus, VoiceProfile
from app.services.storage_service import get_storage_service
from app.utils.audio import (
    compute_audio_quality_metrics,
    load_audio_from_bytes,
    validate_audio_file,
)

settings = get_settings()


# Free-form recording — no scripts. Speakers record in Nepali naturally.
# Tips shown to guide the speaker on how to record well.
RECORDING_TIPS = [
    {"text_ne": "शान्त ठाउँमा रेकर्ड गर्नुहोस्", "text_en": "Record in a quiet place"},
    {"text_ne": "माइक्रोफोनलाई मुखको नजिक राख्नुहोस्", "text_en": "Keep the microphone close to your mouth"},
    {"text_ne": "स्पष्ट र प्राकृतिक रूपमा बोल्नुहोस्", "text_en": "Speak clearly and naturally"},
    {"text_ne": "प्रत्येक रेकर्डिङ ३ देखि ३० सेकेन्ड लामो हुनुपर्छ", "text_en": "Each recording should be 3-30 seconds long"},
    {"text_ne": "विभिन्न विषयमा बोल्नुहोस् — कथा, समाचार, आफ्नो बारेमा", "text_en": "Talk about different topics — stories, news, about yourself"},
    {"text_ne": "खुसी, दुखी, गम्भीर — विभिन्न भावनामा बोल्नुहोस्", "text_en": "Speak in different emotions — happy, sad, serious"},
]

# Suggestions for what to talk about (optional, shown as ideas)
RECORDING_SUGGESTIONS = [
    {"text_ne": "आफ्नो परिचय दिनुहोस्", "text_en": "Introduce yourself"},
    {"text_ne": "आजको मौसम बारेमा बताउनुहोस्", "text_en": "Talk about today's weather"},
    {"text_ne": "कुनै कथा सुनाउनुहोस्", "text_en": "Tell a story"},
    {"text_ne": "आफ्नो मनपर्ने खानाको बारेमा बताउनुहोस्", "text_en": "Talk about your favourite food"},
    {"text_ne": "आफ्नो परिवारको बारेमा बताउनुहोस्", "text_en": "Talk about your family"},
    {"text_ne": "आफ्नो गाउँ वा शहरको बारेमा बताउनुहोस्", "text_en": "Talk about your village or city"},
    {"text_ne": "कुनै समाचार बारेमा बोल्नुहोस्", "text_en": "Talk about some news"},
    {"text_ne": "दैनिक जीवनको बारेमा बताउनुहोस्", "text_en": "Talk about your daily life"},
]


# Quality thresholds
QUALITY_THRESHOLDS = {
    "min_snr_db": 10.0,
    "min_rms_level": -40.0,
    "max_silence_ratio": 0.5,
    "max_clipping": False,
}


class RecordingService:
    """Service for managing audio recordings."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.storage = get_storage_service()

    def get_tips(self) -> list[dict]:
        """Get recording tips (Nepali)."""
        return RECORDING_TIPS

    def get_suggestions(self) -> list[dict]:
        """Get optional topic suggestions (Nepali)."""
        return RECORDING_SUGGESTIONS

    async def upload_recording(
        self,
        voice_profile_id: uuid.UUID,
        prompt_index: int,
        file_bytes: bytes,
        filename: str,
    ) -> Recording:
        """
        Upload and process a new recording.
        
        1. Validate audio format
        2. Upload original to S3
        3. Compute quality metrics
        4. Store metadata in DB
        """
        # Validate the audio file
        metadata = validate_audio_file(file_bytes, filename)
        if not metadata.get("valid"):
            raise ValueError(metadata.get("error", "Invalid audio file"))

        # Validate recording number
        if prompt_index < 0 or prompt_index >= settings.max_recordings_per_profile:
            raise ValueError(f"Recording number {prompt_index} is out of range")

        # Upload original to storage
        s3_key = self.storage.upload_audio(
            file_bytes=file_bytes,
            voice_profile_id=str(voice_profile_id),
            filename=filename,
        )

        # Load audio and compute quality metrics
        audio, sr = load_audio_from_bytes(file_bytes, target_sr=settings.audio_sample_rate)
        quality = compute_audio_quality_metrics(audio, sr)

        # Determine if recording passes quality checks
        status = RecordingStatus.UPLOADED
        rejection_reason = None

        if quality["snr_db"] < QUALITY_THRESHOLDS["min_snr_db"]:
            status = RecordingStatus.REJECTED
            rejection_reason = f"Low signal-to-noise ratio: {quality['snr_db']}dB (min: {QUALITY_THRESHOLDS['min_snr_db']}dB)"

        if quality["rms_level"] < QUALITY_THRESHOLDS["min_rms_level"]:
            status = RecordingStatus.REJECTED
            rejection_reason = f"Volume too low: {quality['rms_level']}dB"

        if quality["silence_ratio"] > QUALITY_THRESHOLDS["max_silence_ratio"]:
            status = RecordingStatus.REJECTED
            rejection_reason = f"Too much silence: {quality['silence_ratio']*100:.0f}%"

        if quality["clipping_detected"]:
            status = RecordingStatus.REJECTED
            rejection_reason = "Audio clipping detected - volume too high"

        # Create recording record
        recording = Recording(
            voice_profile_id=voice_profile_id,
            prompt_text=f"रेकर्डिङ {prompt_index + 1}",
            prompt_index=prompt_index,
            status=status,
            original_file_path=s3_key,
            file_size_bytes=metadata["file_size_bytes"],
            duration_seconds=metadata["duration_seconds"],
            sample_rate=sr,
            snr_db=quality["snr_db"],
            rms_level=quality["rms_level"],
            clipping_detected=quality["clipping_detected"],
            silence_ratio=quality["silence_ratio"],
            rejection_reason=rejection_reason,
        )

        self.db.add(recording)
        await self.db.flush()

        # Update voice profile stats
        await self._update_profile_stats(voice_profile_id)

        await self.db.refresh(recording)
        return recording

    async def get_recordings(self, voice_profile_id: uuid.UUID) -> list[Recording]:
        """Get all recordings for a voice profile."""
        result = await self.db.execute(
            select(Recording)
            .where(Recording.voice_profile_id == voice_profile_id)
            .order_by(Recording.prompt_index)
        )
        return list(result.scalars().all())

    async def get_completed_count(self, voice_profile_id: uuid.UUID) -> int:
        """Get count of successfully uploaded recordings."""
        result = await self.db.execute(
            select(func.count(Recording.id)).where(
                Recording.voice_profile_id == voice_profile_id,
                Recording.status.in_([RecordingStatus.UPLOADED, RecordingStatus.PROCESSED]),
            )
        )
        return result.scalar_one()

    async def _update_profile_stats(self, voice_profile_id: uuid.UUID) -> None:
        """Update voice profile recording statistics."""
        # Count total valid recordings
        count_result = await self.db.execute(
            select(func.count(Recording.id)).where(
                Recording.voice_profile_id == voice_profile_id,
                Recording.status != RecordingStatus.REJECTED,
            )
        )
        total_count = count_result.scalar_one()

        # Sum total duration
        duration_result = await self.db.execute(
            select(func.sum(Recording.duration_seconds)).where(
                Recording.voice_profile_id == voice_profile_id,
                Recording.status != RecordingStatus.REJECTED,
            )
        )
        total_duration = duration_result.scalar_one() or 0.0

        # Update profile
        result = await self.db.execute(
            select(VoiceProfile).where(VoiceProfile.id == voice_profile_id)
        )
        profile = result.scalar_one()
        profile.total_recordings = total_count
        profile.total_duration_seconds = total_duration

        if profile.status == ProfileStatus.PENDING and total_count > 0:
            profile.status = ProfileStatus.RECORDING
