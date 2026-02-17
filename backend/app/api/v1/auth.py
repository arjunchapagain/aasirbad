"""
Authentication endpoints.

POST /auth/register       - Register new user
POST /auth/login          - Login and get tokens
POST /auth/refresh        - Refresh access token
GET  /auth/me             - Get current user info
POST /auth/forgot-password - Request password reset
POST /auth/reset-password  - Reset password with token
POST /auth/admin/reset    - Admin generates reset link
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import get_settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    AdminPasswordReset,
    PasswordResetConfirm,
    PasswordResetRequest,
    TokenRefresh,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter()
settings = get_settings()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    auth_service = AuthService(db)
    try:
        return await auth_service.register(user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT tokens."""
    auth_service = AuthService(db)
    user = await auth_service.authenticate(credentials.email, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    return auth_service.create_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: TokenRefresh, db: AsyncSession = Depends(get_db)):
    """Refresh an expired access token."""
    auth_service = AuthService(db)
    tokens = await auth_service.refresh_tokens(body.refresh_token)

    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    return tokens


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information."""
    return current_user


@router.post("/logout")
async def logout():
    """
    Logout endpoint.
    Client should discard its tokens. Server-side token blacklisting
    can be added via Redis when needed.
    """
    return {"detail": "Successfully logged out"}


@router.post("/forgot-password")
async def forgot_password(
    body: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """Request a password reset.

    Always returns 200 to prevent email enumeration.
    If the email exists, a reset token is generated.
    In production, this would send an email.
    For now, the admin can use /auth/admin/reset.
    """
    auth_service = AuthService(db)
    token = await auth_service.create_reset_token(body.email)

    # In a real setup with SMTP configured, we'd email the link.
    # For now, just log it so admin can retrieve from logs if needed.
    if token:
        import logging

        logging.getLogger(__name__).info(
            "Password reset link: https://aasirbad.works/reset-password?token=%s",
            token,
        )

    # Always return same response to prevent email enumeration
    return {
        "detail": "If an account with that email exists, a reset link has been sent.",
    }


@router.post("/reset-password")
async def reset_password(
    body: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
):
    """Reset password using a valid reset token."""
    auth_service = AuthService(db)
    success = await auth_service.reset_password(body.token, body.new_password)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    return {"detail": "Password has been reset successfully"}


@router.post("/admin/reset")
async def admin_reset(
    body: AdminPasswordReset,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Admin generates a password reset link for a user.

    Only superusers can use this endpoint.
    Returns the reset URL that admin can share with the user.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can generate reset links",
        )

    auth_service = AuthService(db)
    token = await auth_service.admin_reset_password(body.email)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    reset_url = f"https://aasirbad.works/reset-password?token={token}"
    return {"reset_url": reset_url, "expires_in_minutes": 30}
