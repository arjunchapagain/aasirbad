"""
VoiceForge Configuration.

Centralized configuration management using pydantic-settings.
All settings are loaded from environment variables with validation.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = "Aasirbad"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"  # noqa: S105
    api_version: str = "v1"

    # ── Server ───────────────────────────────────────────────────────────────
    backend_host: str = "0.0.0.0"  # noqa: S104
    backend_port: int = 8000
    backend_workers: int = 4
    backend_cors_origins: str = "http://localhost:3000"

    # ── Database ─────────────────────────────────────────────────────────────
    db_backend: Literal["postgresql", "sqlite"] = "postgresql"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "aasirbad"
    postgres_password: str = "aasirbad_secret"  # noqa: S105
    postgres_db: str = "aasirbad"

    # Direct URL overrides (used by Render / Railway / hosted platforms)
    database_url_env: str = Field("", alias="DATABASE_URL")

    @computed_field  # type: ignore[misc]
    @property
    def database_url(self) -> str:
        if self.db_backend == "sqlite":
            return "sqlite+aiosqlite:///./aasirbad.db"
        # Prefer explicit DATABASE_URL from platform (Render, Railway, etc.)
        if self.database_url_env:
            url = self.database_url_env
            # Render gives postgres:// but asyncpg needs postgresql+asyncpg://
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field  # type: ignore[misc]
    @property
    def database_url_sync(self) -> str:
        if self.db_backend == "sqlite":
            return "sqlite:///./aasirbad.db"
        if self.database_url_env:
            url = self.database_url_env
            # Ensure sync driver
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            return url.replace("postgresql+asyncpg://", "postgresql://")
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # ── Redis ────────────────────────────────────────────────────────────────
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""

    # Direct URL override (used by Render / Railway / hosted platforms)
    redis_url_env: str = Field("", alias="REDIS_URL")

    @computed_field  # type: ignore[misc]
    @property
    def redis_url(self) -> str:
        if self.redis_url_env:
            return self.redis_url_env
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/0"

    @computed_field  # type: ignore[misc]
    @property
    def celery_broker_url(self) -> str:
        if self.redis_url_env:
            # Use db 1 for broker
            base = self.redis_url_env.rstrip("/").rsplit("/", 1)[0]
            return f"{base}/1"
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/1"

    @computed_field  # type: ignore[misc]
    @property
    def celery_result_backend(self) -> str:
        if self.redis_url_env:
            base = self.redis_url_env.rstrip("/").rsplit("/", 1)[0]
            return f"{base}/2"
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/2"

    # ── Storage ───────────────────────────────────────────────────────────────
    storage_backend: Literal["local", "s3"] = "local"
    local_storage_dir: str = "./storage"

    # AWS S3 (only needed when storage_backend = "s3")
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    s3_bucket_name: str = "aasirbad-audio"
    s3_model_bucket: str = "aasirbad-models"

    # ── JWT Auth ─────────────────────────────────────────────────────────────
    jwt_secret_key: str = "jwt-secret-change-in-production"  # noqa: S105
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # ── Voice Engine ─────────────────────────────────────────────────────────
    tortoise_model_dir: str = "./models/tortoise"
    max_recording_duration_seconds: int = 30
    min_recordings_for_training: int = 5
    max_recordings_per_profile: int = 50
    audio_sample_rate: int = 22050
    audio_format: str = "wav"

    # ── GPU ───────────────────────────────────────────────────────────────────
    torch_device: str = "cpu"

    # ── Email ────────────────────────────────────────────────────────────────
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_email: str = "noreply@aasirbad.com"

    # ── Monitoring ───────────────────────────────────────────────────────────
    sentry_dsn: str = ""
    log_level: str = "INFO"

    @computed_field  # type: ignore[misc]
    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
