"""
Recording endpoints.

POST /recordings/{token}/upload - Public: Upload recording via token
GET  /recordings/{profile_id}   - List recordings for a profile
"""

import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.recording import RecordingStatus
from app.models.user import User
from app.models.voice_profile import ProfileStatus
from app.schemas.recording import RecordingResponse, RecordingUploadResponse
from app.services.recording_service import RecordingService
from app.services.voice_service import VoiceService

router = APIRouter()


@router.post(
    "/{token}/upload",
    response_model=RecordingUploadResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Public Recording"],
)
async def upload_recording(
    token: str,
    prompt_index: int = Form(...),
    audio_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Public endpoint: Upload an audio recording for a voice profile.
    Accessed via the recording link token - no authentication required.
    """
    # Validate token and profile
    voice_service = VoiceService(db)
    profile = await voice_service.get_profile_by_token(token)

    if not profile:
        raise HTTPException(status_code=404, detail="Invalid recording link")

    if profile.status not in [ProfileStatus.PENDING, ProfileStatus.RECORDING]:
        raise HTTPException(
            status_code=400,
            detail="This voice profile is no longer accepting recordings",
        )

    # Read file bytes
    file_bytes = await audio_file.read()
    filename = audio_file.filename or "recording.wav"

    # Process recording
    recording_service = RecordingService(db)

    try:
        recording = await recording_service.upload_recording(
            voice_profile_id=profile.id,
            prompt_index=prompt_index,
            file_bytes=file_bytes,
            filename=filename,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    quality_metrics = None
    if recording.snr_db is not None:
        quality_metrics = {
            "snr_db": recording.snr_db,
            "rms_level": recording.rms_level,
            "clipping_detected": recording.clipping_detected,
            "silence_ratio": recording.silence_ratio,
        }

    message = "Recording uploaded successfully"
    if recording.status == RecordingStatus.REJECTED:
        message = f"Recording rejected: {recording.rejection_reason}"

    return RecordingUploadResponse(
        recording_id=recording.id,
        status=recording.status,
        quality_metrics=quality_metrics,
        message=message,
    )


@router.get(
    "/profile/{profile_id}",
    response_model=list[RecordingResponse],
)
async def list_recordings(
    profile_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all recordings for a voice profile (authenticated)."""
    # Verify ownership
    voice_service = VoiceService(db)
    profile = await voice_service.get_profile(profile_id, current_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Voice profile not found")

    recording_service = RecordingService(db)
    recordings = await recording_service.get_recordings(profile_id)
    return recordings
