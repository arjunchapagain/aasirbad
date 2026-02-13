"""Recording database model."""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RecordingStatus(str, PyEnum):
    """Status of an individual recording."""

    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    REJECTED = "rejected"  # Failed quality checks
    FAILED = "failed"


class Recording(Base):
    """Individual audio recording for a voice profile."""

    __tablename__ = "recordings"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    voice_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("voice_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Recording metadata
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_index: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[RecordingStatus] = mapped_column(
        Enum(RecordingStatus), default=RecordingStatus.UPLOADED, nullable=False
    )

    # Audio file info
    original_file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    processed_file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    sample_rate: Mapped[int] = mapped_column(Integer, nullable=False)

    # Quality metrics (computed during preprocessing)
    snr_db: Mapped[float | None] = mapped_column(Float, nullable=True)  # Signal-to-noise ratio
    rms_level: Mapped[float | None] = mapped_column(Float, nullable=True)  # Volume level
    clipping_detected: Mapped[bool | None] = mapped_column(nullable=True)
    silence_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Rejection reason if quality check fails
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    voice_profile: Mapped["VoiceProfile"] = relationship(  # noqa: F821
        "VoiceProfile", back_populates="recordings"
    )

    def __repr__(self) -> str:
        return f"<Recording {self.id} prompt={self.prompt_index} ({self.status.value})>"
