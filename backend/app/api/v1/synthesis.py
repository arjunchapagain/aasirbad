"""
Synthesis endpoints.

POST /synthesis/generate - Generate speech from text using a trained voice
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.recording import SynthesisRequest, SynthesisResponse
from app.services.synthesis_service import SynthesisService

router = APIRouter()


@router.post("/generate", response_model=SynthesisResponse)
async def generate_speech(
    request: SynthesisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate speech from text using a trained voice model.

    The voice profile must be in READY status (training completed).
    """
    synthesis_service = SynthesisService(db)

    try:
        result = await synthesis_service.synthesize(
            text=request.text,
            voice_profile_id=request.voice_profile_id,
            user_id=current_user.id,
            preset=request.preset,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return SynthesisResponse(**result)
