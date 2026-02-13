"""Test configuration and fixtures."""

import asyncio
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.utils.security import hash_password


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ── Database fixtures (only used when a test requests them) ──────────────────

@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator:
    """Provide a test database session using in-memory SQLite."""
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from sqlalchemy.pool import StaticPool

    import app.models.recording  # noqa: F401

    # Import all models so Base.metadata knows about them
    import app.models.user  # noqa: F401
    import app.models.voice_profile  # noqa: F401
    from app.database import Base

    # Use in-memory SQLite with StaticPool so all connections share the same DB
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTP test client with injected test DB."""
    from app.database import get_db
    from app.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session):
    """Create a test user in the database."""
    from app.models.user import User

    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        hashed_password=hash_password("testpassword123"),
        full_name="Test User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user) -> dict:
    """Get authentication headers for test user."""
    from app.utils.security import create_access_token

    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}
