"""
Voice profile management service.

Handles CRUD operations for voice profiles, recording link generation,
and training orchestration.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.models.voice_profile import ProfileStatus, VoiceProfile
from app.schemas.voice_profile import VoiceProfileCreate
from app.utils.security import generate_recording_token

settings = get_settings()


class VoiceService:
    """Service for voice profile management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_profile(
        self,
        user_id: uuid.UUID,
        data: VoiceProfileCreate,
    ) -> VoiceProfile:
        """Create a new voice profile with a unique recording token."""
        token = generate_recording_token()

        profile = VoiceProfile(
            user_id=user_id,
            name=data.name,
            description=data.description,
            recording_token=token,
            status=ProfileStatus.PENDING,
        )

        self.db.add(profile)
        await self.db.flush()
        await self.db.refresh(profile)
        return profile

    async def get_profile(
        self,
        profile_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> VoiceProfile | None:
        """Get a voice profile by ID, scoped to user."""
        result = await self.db.execute(
            select(VoiceProfile).where(
                VoiceProfile.id == profile_id,
                VoiceProfile.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_profile_by_token(self, token: str) -> VoiceProfile | None:
        """Get a voice profile by its recording token (public access)."""
        result = await self.db.execute(
            select(VoiceProfile)
            .where(VoiceProfile.recording_token == token)
            .options(selectinload(VoiceProfile.recordings))
        )
        return result.scalar_one_or_none()

    async def list_profiles(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[VoiceProfile], int]:
        """List all voice profiles for a user with pagination."""
        # Count total
        from sqlalchemy import func

        count_result = await self.db.execute(
            select(func.count(VoiceProfile.id)).where(VoiceProfile.user_id == user_id)
        )
        total = count_result.scalar_one()

        # Fetch page
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(VoiceProfile)
            .where(VoiceProfile.user_id == user_id)
            .order_by(VoiceProfile.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        profiles = list(result.scalars().all())

        return profiles, total

    async def delete_profile(
        self,
        profile_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Delete a voice profile."""
        profile = await self.get_profile(profile_id, user_id)
        if not profile:
            return False

        await self.db.delete(profile)
        return True

    async def update_training_status(
        self,
        profile_id: uuid.UUID,
        status: ProfileStatus,
        progress: float = 0.0,
        error: str | None = None,
        model_path: str | None = None,
    ) -> VoiceProfile | None:
        """Update training status of a voice profile (called by worker)."""
        result = await self.db.execute(
            select(VoiceProfile).where(VoiceProfile.id == profile_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            return None

        profile.status = status
        profile.training_progress = progress

        if status == ProfileStatus.TRAINING and not profile.training_started_at:
            profile.training_started_at = datetime.now(timezone.utc)

        if status == ProfileStatus.READY:
            profile.training_completed_at = datetime.now(timezone.utc)
            if model_path:
                profile.model_path = model_path

        if status == ProfileStatus.FAILED and error:
            profile.training_error = error

        await self.db.flush()
        await self.db.refresh(profile)
        return profile

    async def get_ready_profile(
        self,
        profile_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> VoiceProfile | None:
        """Get a voice profile that is ready for synthesis."""
        result = await self.db.execute(
            select(VoiceProfile).where(
                VoiceProfile.id == profile_id,
                VoiceProfile.user_id == user_id,
                VoiceProfile.status == ProfileStatus.READY,
            )
        )
        return result.scalar_one_or_none()

    def generate_recording_url(self, token: str, base_url: str) -> str:
        """Generate a shareable recording URL."""
        return f"{base_url}/record/{token}"
