"""
Database session management.

Provides async SQLAlchemy engine and session factory with proper lifecycle management.
"""

import asyncio
import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Only echo SQL when DEBUG is explicitly true AND in development
_engine_kwargs: dict = {"echo": settings.debug and settings.app_env == "development"}
if settings.db_backend == "postgresql":
    _engine_kwargs.update(
        pool_size=3,
        max_overflow=5,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_timeout=30,
        connect_args={"server_settings": {"application_name": "aasirbad"}},
    )

engine = create_async_engine(settings.database_url, **_engine_kwargs)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all database models."""



async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides a database session per request."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def wait_for_db(retries: int = 5, delay: float = 3.0) -> bool:
    """Wait for database to become available, with retries."""
    from sqlalchemy import text

    for attempt in range(1, retries + 1):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Database connected (attempt %d/%d)", attempt, retries)
            return True
        except Exception as e:
            logger.warning(
                "Database not ready (attempt %d/%d): %s",
                attempt,
                retries,
                e,
            )
            if attempt < retries:
                await asyncio.sleep(delay)
    logger.error("Database connection failed after %d attempts", retries)
    return False


async def init_db() -> None:
    """Initialize database tables (development only)."""
    # Import models to register them with Base.metadata
    import app.models.recording  # noqa: F401
    import app.models.user  # noqa: F401
    import app.models.voice_profile  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Dispose database engine connections."""
    await engine.dispose()
