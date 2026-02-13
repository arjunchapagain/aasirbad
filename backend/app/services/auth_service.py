"""
Authentication service.

Handles user registration, login, and token management.
"""

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)

settings = get_settings()
logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, user_data: UserCreate) -> User:
        """Register a new user."""
        # Check if email already exists
        result = await self.db.execute(
            select(User).where(User.email == user_data.email)
        )
        existing = result.scalar_one_or_none()
        if existing:
            # Always hash to prevent timing-based email enumeration
            hash_password(user_data.password)
            raise ValueError("Email already registered")

        user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def authenticate(self, email: str, password: str) -> User | None:
        """Authenticate a user by email and password."""
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            # Hash a dummy password to prevent timing-based enumeration
            verify_password(password, hash_password("dummy-constant-time"))
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning("Failed login attempt for %s", email)
            return None

        if not user.is_active:
            return None

        return user

    def create_tokens(self, user: User) -> TokenResponse:
        """Create access and refresh tokens for a user."""
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )

    async def refresh_tokens(self, refresh_token_str: str) -> TokenResponse | None:
        """Refresh access token using a valid refresh token."""
        payload = decode_refresh_token(refresh_token_str)
        if not payload or payload.get("type") != "refresh":
            return None

        try:
            user_id = uuid.UUID(payload["sub"])
        except (ValueError, KeyError):
            return None

        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            return None

        return self.create_tokens(user)

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        """Get a user by their ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
