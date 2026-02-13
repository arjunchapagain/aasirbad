"""Recording API schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.recording import RecordingStatus


class RecordingResponse(BaseModel):
    """Schema for recording in API responses."""

    id: uuid.UUID
    voice_profile_id: uuid.UUID
    prompt_text: str
    prompt_index: int
    status: RecordingStatus
    duration_seconds: float
    sample_rate: int
    snr_db: float | None
    rms_level: float | None
    clipping_detected: bool | None
    silence_ratio: float | None
    rejection_reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RecordingUploadResponse(BaseModel):
    """Response after uploading a recording."""

    recording_id: uuid.UUID
    status: RecordingStatus
    quality_metrics: dict | None
    message: str


class SynthesisRequest(BaseModel):
    """Request to synthesize speech."""

    text: str
    voice_profile_id: uuid.UUID
    speed: float = 1.0  # Speech speed multiplier
    preset: str = "fast"  # Tortoise quality preset: ultra_fast, fast, standard, high_quality


class SynthesisResponse(BaseModel):
    """Response after synthesis."""

    audio_url: str
    duration_seconds: float
    text: str
    voice_profile_id: uuid.UUID
