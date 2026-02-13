"""
API v1 Router.

Aggregates all v1 endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.recordings import router as recordings_router
from app.api.v1.synthesis import router as synthesis_router
from app.api.v1.voice_profiles import router as voice_profiles_router

router = APIRouter(prefix="/v1")

router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(voice_profiles_router, prefix="/voice-profiles", tags=["Voice Profiles"])
router.include_router(recordings_router, prefix="/recordings", tags=["Recordings"])
router.include_router(synthesis_router, prefix="/synthesis", tags=["Synthesis"])
