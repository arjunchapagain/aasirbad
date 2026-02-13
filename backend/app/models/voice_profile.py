"""Voice Profile database model."""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProfileStatus(str, PyEnum):
    """Status of a voice profile through its lifecycle."""

    PENDING = "pending"  # Created, awaiting recordings
    RECORDING = "recording"  # User is actively recording
    PROCESSING = "processing"  # Audio preprocessing in progress
    TRAINING = "training"  # Model training in progress
    READY = "ready"  # Voice model trained and ready
    FAILED = "failed"  # Training failed
    ARCHIVED = "archived"  # Soft-deleted / archived


class VoiceProfile(Base):
    """Voice profile - represents a single voice identity to clone."""

    __tablename__ = "voice_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ProfileStatus] = mapped_column(
        Enum(ProfileStatus), default=ProfileStatus.PENDING, nullable=False
    )

    # Recording link token (unique, used to generate sharable recording URL)
    recording_token: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )

    # Training metadata
    total_recordings: Mapped[int] = mapped_column(Integer, default=0)
    total_duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    model_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    training_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    training_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    training_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    training_progress: Mapped[float] = mapped_column(Float, default=0.0)

    # Quality metrics
    voice_similarity_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="voice_profiles")  # noqa: F821
    recordings: Mapped[list["Recording"]] = relationship(  # noqa: F821
        "Recording", back_populates="voice_profile", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<VoiceProfile {self.name} ({self.status.value})>"
