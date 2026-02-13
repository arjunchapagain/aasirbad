"""
Voice Profile endpoints.

POST   /voice-profiles          - Create new voice profile
GET    /voice-profiles          - List user's profiles
GET    /voice-profiles/{id}     - Get profile details
DELETE /voice-profiles/{id}     - Delete a profile
GET    /voice-profiles/{id}/link - Get recording link
POST   /voice-profiles/{id}/train - Trigger training

GET    /record/{token}          - Public: Get recording session (via token)
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import get_settings
from app.database import get_db
from app.models.user import User
from app.models.voice_profile import ProfileStatus
from app.schemas.voice_profile import (
    RecordingLinkResponse,
    RecordingSessionResponse,
    TrainingTriggerResponse,
    VoiceProfileCreate,
    VoiceProfileListResponse,
    VoiceProfileResponse,
)
from app.services.recording_service import RecordingService
from app.services.voice_service import VoiceService

router = APIRouter()
settings = get_settings()


@router.post("", response_model=VoiceProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_voice_profile(
    data: VoiceProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new voice profile for cloning."""
    voice_service = VoiceService(db)
    return await voice_service.create_profile(current_user.id, data)


@router.get("", response_model=VoiceProfileListResponse)
async def list_voice_profiles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all voice profiles for the current user."""
    voice_service = VoiceService(db)
    profiles, total = await voice_service.list_profiles(current_user.id, page, page_size)

    return VoiceProfileListResponse(
        items=[VoiceProfileResponse.model_validate(p) for p in profiles],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{profile_id}", response_model=VoiceProfileResponse)
async def get_voice_profile(
    profile_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get details of a specific voice profile."""
    voice_service = VoiceService(db)
    profile = await voice_service.get_profile(profile_id, current_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Voice profile not found")

    return profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_voice_profile(
    profile_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a voice profile and all associated recordings."""
    voice_service = VoiceService(db)
    deleted = await voice_service.delete_profile(profile_id, current_user.id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Voice profile not found")


@router.get("/{profile_id}/link", response_model=RecordingLinkResponse)
async def get_recording_link(
    profile_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a shareable recording link for a voice profile."""
    voice_service = VoiceService(db)
    profile = await voice_service.get_profile(profile_id, current_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Voice profile not found")

    # Build the recording URL (frontend URL)
    frontend_base = settings.cors_origins[0] if settings.cors_origins else "http://localhost:3000"
    recording_url = voice_service.generate_recording_url(profile.recording_token, frontend_base)

    return RecordingLinkResponse(
        recording_url=recording_url,
        token=profile.recording_token,
        profile_name=profile.name,
    )


@router.post("/{profile_id}/train", response_model=TrainingTriggerResponse)
async def trigger_training(
    profile_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger voice model training for a profile."""
    voice_service = VoiceService(db)
    profile = await voice_service.get_profile(profile_id, current_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Voice profile not found")

    if profile.status == ProfileStatus.TRAINING:
        raise HTTPException(status_code=409, detail="Training already in progress")

    if profile.status == ProfileStatus.READY:
        raise HTTPException(status_code=409, detail="Voice model already trained")

    # Check minimum recordings
    recording_service = RecordingService(db)
    count = await recording_service.get_completed_count(profile_id)

    if count < settings.min_recordings_for_training:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum {settings.min_recordings_for_training} recordings required. "
            f"Currently have {count}.",
        )

    # Queue training job via Celery
    from app.workers.tasks import train_voice_model

    job = train_voice_model.delay(str(profile_id))

    # Update status to processing
    await voice_service.update_training_status(profile_id, ProfileStatus.PROCESSING)

    return TrainingTriggerResponse(
        job_id=job.id,
        status="queued",
        message=f"Training job queued. {count} recordings will be used.",
    )


# ── Public endpoints (no auth - accessed via token) ──────────────────────────


@router.get("/record/{token}", response_model=RecordingSessionResponse, tags=["Public Recording"])
async def get_recording_session(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Public endpoint: Get recording session details by token.
    This is accessed when a user clicks the recording link.
    """
    voice_service = VoiceService(db)
    profile = await voice_service.get_profile_by_token(token)

    if not profile:
        raise HTTPException(status_code=404, detail="Invalid recording link")

    if profile.status not in [ProfileStatus.PENDING, ProfileStatus.RECORDING]:
        raise HTTPException(
            status_code=400,
            detail="This voice profile is no longer accepting recordings",
        )

    recording_service = RecordingService(db)
    tips = recording_service.get_tips()
    suggestions = recording_service.get_suggestions()
    completed = await recording_service.get_completed_count(profile.id)

    return RecordingSessionResponse(
        profile_name=profile.name,
        tips=tips,
        suggestions=suggestions,
        completed_recordings=completed,
        max_recordings=settings.max_recordings_per_profile,
        min_required=settings.min_recordings_for_training,
    )
