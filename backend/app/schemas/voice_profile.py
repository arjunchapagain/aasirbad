"""Voice Profile API schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.voice_profile import ProfileStatus


class VoiceProfileCreate(BaseModel):
    """Schema for creating a voice profile."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)


class VoiceProfileResponse(BaseModel):
    """Schema for voice profile in API responses."""

    id: uuid.UUID
    name: str
    description: str | None
    status: ProfileStatus
    recording_token: str
    total_recordings: int
    total_duration_seconds: float
    training_progress: float
    voice_similarity_score: float | None
    training_started_at: datetime | None
    training_completed_at: datetime | None
    training_error: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VoiceProfileListResponse(BaseModel):
    """Paginated list of voice profiles."""

    items: list[VoiceProfileResponse]
    total: int
    page: int
    page_size: int


class RecordingLinkResponse(BaseModel):
    """Response containing a shareable recording link."""

    recording_url: str
    token: str
    profile_name: str
    expires_at: datetime | None = None


class RecordingPrompt(BaseModel):
    """A text prompt for the user to read aloud."""

    index: int
    text: str
    category: str  # e.g., "pangram", "emotion", "conversational"
    estimated_duration_seconds: int


class RecordingSessionResponse(BaseModel):
    """Response for a recording session (accessed via token)."""

    profile_name: str
    prompts: list[RecordingPrompt]
    completed_recordings: int
    total_prompts: int
    min_required: int


class TrainingTriggerResponse(BaseModel):
    """Response after triggering voice training."""

    job_id: str
    status: str
    message: str


class TrainingStatusResponse(BaseModel):
    """Real-time training status."""

    profile_id: uuid.UUID
    status: ProfileStatus
    progress: float  # 0.0 to 1.0
    current_step: str
    estimated_time_remaining_seconds: int | None
    error: str | None
