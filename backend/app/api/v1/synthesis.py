"""
Synthesis endpoints.

POST /synthesis/generate - Generate speech from text using a cloned voice
GET  /synthesis/usage    - Free-tier usage for the current month
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.recording import SynthesisRequest, SynthesisResponse, UsageResponse
from app.services.synthesis_service import SynthesisService

router = APIRouter()


@router.post("/generate", response_model=SynthesisResponse)
async def generate_speech(
    request: SynthesisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate speech from text. The voice profile must be READY."""
    try:
        result = await SynthesisService(db).synthesize(
            text=request.text,
            voice_profile_id=request.voice_profile_id,
            user_id=current_user.id,
        )
    except PermissionError as e:
        raise HTTPException(status_code=429, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return SynthesisResponse(**result)


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return UsageResponse(**await SynthesisService(db).usage(current_user.id))
