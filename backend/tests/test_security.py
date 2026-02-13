"""Tests for security utility functions."""

import uuid
from datetime import timedelta

from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_recording_token,
)


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_and_verify(self):
        """Test that a hashed password can be verified."""
        plain = "supersecretpassword"
        hashed = hash_password(plain)
        assert hashed != plain
        assert verify_password(plain, hashed) is True

    def test_wrong_password(self):
        """Test that wrong password fails verification."""
        hashed = hash_password("correct_password")
        assert verify_password("wrong_password", hashed) is False

    def test_hash_uniqueness(self):
        """Test that same password produces different hashes (salted)."""
        h1 = hash_password("samepassword")
        h2 = hash_password("samepassword")
        assert h1 != h2


class TestJWTTokens:
    """Test JWT token creation and decoding."""

    def test_access_token_roundtrip(self):
        """Test creating and decoding an access token."""
        user_id = uuid.uuid4()
        token = create_access_token(user_id)
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"

    def test_refresh_token_roundtrip(self):
        """Test creating and decoding a refresh token."""
        user_id = uuid.uuid4()
        token = create_refresh_token(user_id)
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"

    def test_invalid_token(self):
        """Test that an invalid token returns None."""
        payload = decode_token("invalid.jwt.token")
        assert payload is None

    def test_custom_expiry(self):
        """Test token with custom expiry."""
        user_id = uuid.uuid4()
        token = create_access_token(
            user_id,
            expires_delta=timedelta(hours=1),
        )
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == str(user_id)


class TestRecordingToken:
    """Test recording token generation."""

    def test_token_generation(self):
        """Test that recording tokens are generated."""
        token = generate_recording_token()
        assert isinstance(token, str)
        assert len(token) > 20  # Should be substantial

    def test_token_uniqueness(self):
        """Test that tokens are unique."""
        tokens = {generate_recording_token() for _ in range(100)}
        assert len(tokens) == 100
