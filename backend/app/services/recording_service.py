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


# Well-curated prompts covering diverse phonemes, emotions, and speech patterns
RECORDING_PROMPTS = [
    {
        "index": 0,
        "text": "The quick brown fox jumps over the lazy dog near the riverbank.",
        "category": "pangram",
        "estimated_duration_seconds": 5,
    },
    {
        "index": 1,
        "text": "She sells seashells by the seashore, where the waves crash against the rocky cliffs.",
        "category": "articulation",
        "estimated_duration_seconds": 6,
    },
    {
        "index": 2,
        "text": "How vexingly quick daft zebras jump! A wizard's job is to vex chumps quickly in fog.",
        "category": "pangram",
        "estimated_duration_seconds": 7,
    },
    {
        "index": 3,
        "text": "I woke up this morning feeling absolutely wonderful, like today is going to be the best day ever!",
        "category": "emotion_happy",
        "estimated_duration_seconds": 7,
    },
    {
        "index": 4,
        "text": "Unfortunately, we regret to inform you that the project deadline has been moved up by two weeks.",
        "category": "emotion_formal",
        "estimated_duration_seconds": 7,
    },
    {
        "index": 5,
        "text": "Wait, are you serious? That's incredible! I can't believe it actually worked!",
        "category": "emotion_surprised",
        "estimated_duration_seconds": 5,
    },
    {
        "index": 6,
        "text": "Let me explain the process step by step. First, you need to open the application. Then, navigate to settings.",
        "category": "instructional",
        "estimated_duration_seconds": 8,
    },
    {
        "index": 7,
        "text": "The total revenue for the third quarter was approximately fourteen point seven million dollars, representing a twelve percent increase.",
        "category": "numbers",
        "estimated_duration_seconds": 8,
    },
    {
        "index": 8,
        "text": "So basically, I was thinking we could, you know, maybe grab some coffee later and talk about the project?",
        "category": "conversational",
        "estimated_duration_seconds": 7,
    },
    {
        "index": 9,
        "text": "In the quiet of the evening, the stars painted the sky with their ancient, unwavering light.",
        "category": "narrative",
        "estimated_duration_seconds": 6,
    },
    {
        "index": 10,
        "text": "Please confirm your email address at support at example dot com, and your reference number is A B C one two three four five.",
        "category": "alphanumeric",
        "estimated_duration_seconds": 8,
    },
    {
        "index": 11,
        "text": "I'm not angry, I'm just disappointed. We talked about this already, and I thought we had an understanding.",
        "category": "emotion_serious",
        "estimated_duration_seconds": 7,
    },
    {
        "index": 12,
        "text": "Good morning everyone! Welcome to today's presentation. I'll be covering three main topics during our session.",
        "category": "presentation",
        "estimated_duration_seconds": 7,
    },
    {
        "index": 13,
        "text": "The thunderstorm raged outside, lightning splitting the sky as rain hammered against the windows with relentless fury.",
        "category": "dramatic",
        "estimated_duration_seconds": 7,
    },
    {
        "index": 14,
        "text": "Could you repeat that, please? I didn't quite catch what you said. Was it Thursday or Tuesday?",
        "category": "question",
        "estimated_duration_seconds": 6,
    },
    {
        "index": 15,
        "text": "Technology continues to reshape our world in ways we never imagined possible just a decade ago.",
        "category": "neutral",
        "estimated_duration_seconds": 6,
    },
    {
        "index": 16,
        "text": "Ha ha, that's the funniest thing I've heard all week! Oh man, you really got me with that one.",
        "category": "emotion_laughing",
        "estimated_duration_seconds": 6,
    },
    {
        "index": 17,
        "text": "Attention passengers: the next train to downtown will arrive at platform three in approximately five minutes.",
        "category": "announcement",
        "estimated_duration_seconds": 7,
    },
    {
        "index": 18,
        "text": "I'd like to order a large cappuccino with oat milk, two blueberry muffins, and a sparkling water, please.",
        "category": "everyday",
        "estimated_duration_seconds": 7,
    },
    {
        "index": 19,
        "text": "To summarize, our findings suggest that continued investment in research and development is essential for long-term growth.",
        "category": "conclusion",
        "estimated_duration_seconds": 8,
    },
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

    def get_prompts(self) -> list[dict]:
        """Get all recording prompts."""
        return RECORDING_PROMPTS

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

        # Validate prompt index
        if prompt_index < 0 or prompt_index >= len(RECORDING_PROMPTS):
            raise ValueError(f"Invalid prompt index: {prompt_index}")

        prompt = RECORDING_PROMPTS[prompt_index]

        # Upload original to S3
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
            prompt_text=prompt["text"],
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
