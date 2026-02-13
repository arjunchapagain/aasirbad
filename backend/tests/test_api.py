"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuth:
    """Test authentication flow."""

    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
                "full_name": "New User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data

    async def test_register_duplicate_email(
        self, client: AsyncClient, test_user,  # noqa: ARG002
    ):
        """Test registration with existing email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
                "full_name": "Duplicate",
            },
        )
        assert response.status_code == 409

    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with password too short."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "weak@example.com",
                "password": "short",
                "full_name": "Weak Pass",
            },
        )
        assert response.status_code == 422  # Validation error

    async def test_login_success(
        self, client: AsyncClient, test_user,  # noqa: ARG002
    ):
        """Test successful login."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"  # noqa: S105

    async def test_login_wrong_password(
        self, client: AsyncClient, test_user,  # noqa: ARG002
    ):
        """Test login with wrong password."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    async def test_get_me_authenticated(self, client: AsyncClient, auth_headers):
        """Test getting current user info."""
        response = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"

    async def test_get_me_unauthenticated(self, client: AsyncClient):
        """Test accessing protected endpoint without token."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code in (401, 403)  # No credentials


@pytest.mark.asyncio
class TestVoiceProfiles:
    """Test voice profile operations."""

    async def test_create_profile(self, client: AsyncClient, auth_headers):
        """Test creating a voice profile."""
        response = await client.post(
            "/api/v1/voice-profiles",
            json={"name": "Test Voice", "description": "A test voice profile"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Voice"
        assert data["status"] == "pending"
        assert "recording_token" in data

    async def test_list_profiles(self, client: AsyncClient, auth_headers):
        """Test listing voice profiles."""
        # Create a profile first
        await client.post(
            "/api/v1/voice-profiles",
            json={"name": "Voice 1"},
            headers=auth_headers,
        )

        response = await client.get(
            "/api/v1/voice-profiles",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1

    async def test_get_recording_link(self, client: AsyncClient, auth_headers):
        """Test getting a recording link."""
        # Create profile
        create_resp = await client.post(
            "/api/v1/voice-profiles",
            json={"name": "Link Test"},
            headers=auth_headers,
        )
        profile_id = create_resp.json()["id"]

        # Get link
        response = await client.get(
            f"/api/v1/voice-profiles/{profile_id}/link",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "recording_url" in data
        assert "token" in data

    async def test_delete_profile(self, client: AsyncClient, auth_headers):
        """Test deleting a voice profile."""
        create_resp = await client.post(
            "/api/v1/voice-profiles",
            json={"name": "To Delete"},
            headers=auth_headers,
        )
        profile_id = create_resp.json()["id"]

        response = await client.delete(
            f"/api/v1/voice-profiles/{profile_id}",
            headers=auth_headers,
        )
        assert response.status_code == 204


@pytest.mark.asyncio
class TestHealthCheck:
    """Test system endpoints."""

    async def test_health(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
