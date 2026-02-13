"""
Security utilities for authentication and token management.
"""

import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Use separate keys for access vs refresh tokens
_ACCESS_KEY = settings.jwt_secret_key
_REFRESH_KEY = settings.jwt_secret_key + ":refresh"


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_id: uuid.UUID,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token with jti, iss, aud claims."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_hex(16),
        "iss": "aasirbad",
        "aud": "aasirbad:api",
    }
    return jwt.encode(payload, _ACCESS_KEY, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: uuid.UUID) -> str:
    """Create a JWT refresh token with separate signing key."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_hex(16),
        "iss": "aasirbad",
        "aud": "aasirbad:refresh",
    }
    return jwt.encode(payload, _REFRESH_KEY, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict | None:
    """Decode and validate a JWT access token. Returns payload or None."""
    try:
        payload = jwt.decode(
            token,
            _ACCESS_KEY,
            algorithms=[settings.jwt_algorithm],
            audience="aasirbad:api",
            issuer="aasirbad",
        )
        return payload
    except JWTError as e:
        logger.warning("Access token validation failed: %s", e)
        return None


def decode_refresh_token(token: str) -> dict | None:
    """Decode and validate a JWT refresh token. Returns payload or None."""
    try:
        payload = jwt.decode(
            token,
            _REFRESH_KEY,
            algorithms=[settings.jwt_algorithm],
            audience="aasirbad:refresh",
            issuer="aasirbad",
        )
        return payload
    except JWTError as e:
        logger.warning("Refresh token validation failed: %s", e)
        return None


# Keep backward-compatible alias for non-typed decode (used in deps)
decode_token = decode_access_token


def generate_recording_token() -> str:
    """Generate a cryptographically secure recording session token."""
    return secrets.token_urlsafe(48)
