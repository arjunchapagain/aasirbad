"""Tests for the hosted-TTS pipeline, signed URLs, consent, limits and reset tokens."""

import time
import uuid

import pytest

from app.config import get_settings
from app.services.storage_service import sign_file_key, verify_file_signature
from app.utils.security import (
    create_password_reset_token,
    decode_password_reset_token,
    password_fingerprint,
)
from app.voice_engine.providers import DemoProvider, TTSError


# ── Providers ────────────────────────────────────────────────────────────────

def test_demo_provider_roundtrip():
    p = DemoProvider()
    vid = p.create_voice("me", [b"x" * 2000])
    wav = p.synthesize("hello there world", vid)
    assert wav[:4] == b"RIFF" and len(wav) > 5000
    assert p.synthesize("hello there world", vid) == wav  # deterministic


def test_demo_provider_needs_samples():
    with pytest.raises(TTSError):
        DemoProvider().create_voice("me", [])


# ── Signed URLs ──────────────────────────────────────────────────────────────

def test_signed_url_valid_expired_and_tampered():
    exp = int(time.time()) + 60
    sig = sign_file_key("a/b.wav", exp)
    assert verify_file_signature("a/b.wav", exp, sig)
    assert not verify_file_signature("a/other.wav", exp, sig)
    assert not verify_file_signature("a/b.wav", exp + 1, sig)
    old = int(time.time()) - 1
    assert not verify_file_signature("a/b.wav", old, sign_file_key("a/b.wav", old))


async def test_file_endpoint_rejects_unsigned(client):
    r = await client.get("/api/v1/files/recordings/x/y.wav")
    assert r.status_code == 403


# ── Reset tokens ─────────────────────────────────────────────────────────────

def test_reset_token_carries_fingerprint():
    uid = uuid.uuid4()
    tok = create_password_reset_token(uid, password_fingerprint("hash-1"))
    payload = decode_password_reset_token(tok)
    assert payload["pwf"] == password_fingerprint("hash-1")
    assert payload["pwf"] != password_fingerprint("hash-2")


async def test_reset_token_is_single_use(client, test_user):
    from app.services.auth_service import AuthService  # noqa: F401

    r = await client.post("/api/v1/auth/forgot-password", json={"email": test_user.email})
    assert r.status_code == 200
    from app.utils.security import password_fingerprint as fp

    tok = create_password_reset_token(test_user.id, fp(test_user.hashed_password))
    ok = await client.post("/api/v1/auth/reset-password",
                           json={"token": tok, "new_password": "brand-new-pass-1"})
    assert ok.status_code == 200
    again = await client.post("/api/v1/auth/reset-password",
                              json={"token": tok, "new_password": "another-pass-22"})
    assert again.status_code == 400


# ── Consent, limits, usage ───────────────────────────────────────────────────

async def test_consent_required(client, auth_headers):
    r = await client.post("/api/v1/voice-profiles", json={"name": "x"}, headers=auth_headers)
    assert r.status_code == 422
    r = await client.post("/api/v1/voice-profiles", json={"name": "x", "consent": False},
                          headers=auth_headers)
    assert r.status_code == 422


async def test_profile_cap(client, auth_headers):
    cap = get_settings().max_profiles_per_user
    for i in range(cap):
        r = await client.post("/api/v1/voice-profiles",
                              json={"name": f"v{i}", "consent": True}, headers=auth_headers)
        assert r.status_code == 201
    r = await client.post("/api/v1/voice-profiles", json={"name": "over", "consent": True},
                          headers=auth_headers)
    assert r.status_code == 403


async def _ready_profile(db_session, user_id):
    from app.models.voice_profile import ProfileStatus, VoiceProfile

    prof = VoiceProfile(
        user_id=user_id, name="ready", recording_token=uuid.uuid4().hex,
        status=ProfileStatus.READY, model_path="demo:demo-abcd1234",
    )
    db_session.add(prof)
    await db_session.commit()
    return prof


async def test_synthesis_and_monthly_limit(client, auth_headers, db_session, test_user, monkeypatch, tmp_path):
    monkeypatch.setattr(get_settings(), "local_storage_dir", str(tmp_path))
    import app.services.storage_service as ss
    monkeypatch.setattr(ss, "_storage_service", None)
    prof = await _ready_profile(db_session, test_user.id)

    r = await client.post("/api/v1/synthesis/generate",
                          json={"text": "Hello world", "voice_profile_id": str(prof.id)},
                          headers=auth_headers)
    assert r.status_code == 200, r.text
    assert "sig=" in r.json()["audio_url"]

    u = await client.get("/api/v1/synthesis/usage", headers=auth_headers)
    assert u.json()["used"] == len("Hello world")

    monkeypatch.setattr(get_settings(), "monthly_synthesis_chars", 15)
    r = await client.post("/api/v1/synthesis/generate",
                          json={"text": "Hello world", "voice_profile_id": str(prof.id)},
                          headers=auth_headers)
    assert r.status_code == 429


async def test_cannot_use_someone_elses_voice(client, db_session, auth_headers):
    from app.models.user import User
    from app.utils.security import hash_password

    other = User(id=uuid.uuid4(), email="o@example.com", full_name="O",
                 hashed_password=hash_password("whatever123"))
    db_session.add(other)
    await db_session.commit()
    prof = await _ready_profile(db_session, other.id)
    r = await client.post("/api/v1/synthesis/generate",
                          json={"text": "hi", "voice_profile_id": str(prof.id)},
                          headers=auth_headers)
    assert r.status_code == 400


async def test_synthesis_requires_auth(client):
    r = await client.post("/api/v1/synthesis/generate",
                          json={"text": "hi", "voice_profile_id": str(uuid.uuid4())})
    assert r.status_code in (401, 403)
