"""User API schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user in API responses."""

    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105
    expires_in: int


class TokenRefresh(BaseModel):
    """Schema for refreshing a token."""

    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Schema for requesting a password reset."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for resetting password with token."""

    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class AdminPasswordReset(BaseModel):
    """Schema for admin-initiated password reset."""

    email: EmailStr
