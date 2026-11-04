"""End-to-end smoke test against a running API (default http://localhost:8000).

Usage: python scripts/e2e.py [base_url]
Requires: httpx, numpy, soundfile (already backend deps).
"""
import io
import sys
import time
import uuid

import httpx
import numpy as np
import soundfile as sf

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000").rstrip("/")
API = f"{BASE}/api/v1"


def speechlike_wav(seed: int, seconds: float = 3.0, sr: int = 22050) -> bytes:
    rng = np.random.default_rng(seed)
    t = np.arange(int(seconds * sr)) / sr
    f0 = 120 + 10 * seed
    sig = sum(np.sin(2 * np.pi * f0 * k * t) / k for k in range(1, 8))
    gate = np.clip((np.sin(2 * np.pi * 2.0 * t) + 0.5) * 3, 0, 1)  # speech bursts with pauses
    sig = sig * gate
    sig += 0.001 * rng.standard_normal(len(t))
    sig = 0.4 * sig / np.max(np.abs(sig))
    buf = io.BytesIO()
    sf.write(buf, sig.astype("float32"), sr, format="WAV")
    return buf.getvalue()


def check(cond: bool, msg: str) -> None:
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        sys.exit(1)


c = httpx.Client(timeout=60)
email = f"e2e-{uuid.uuid4().hex[:8]}@example.com"
r = c.post(f"{API}/auth/register", json={"email": email, "password": "password123", "full_name": "E2E"})
check(r.status_code == 201, "register")
r = c.post(f"{API}/auth/login", json={"email": email, "password": "password123"})
H = {"Authorization": f"Bearer {r.json()['access_token']}"}
check(c.get(f"{API}/voice-profiles").status_code in (401, 403), "profiles require auth")

r = c.post(f"{API}/voice-profiles", json={"name": "Me"}, headers=H)
check(r.status_code == 422, "profile creation without consent rejected")
r = c.post(f"{API}/voice-profiles", json={"name": "Me", "consent": True}, headers=H)
check(r.status_code == 201, "profile created with consent")
pid, token = r.json()["id"], r.json()["recording_token"]

r = c.post(f"{API}/voice-profiles/{pid}/train", headers=H)
check(r.status_code == 400, "training blocked until enough recordings")

for i in range(5):
    r = c.post(
        f"{API}/recordings/{token}/upload",
        data={"prompt_index": str(i)},
        files={"audio_file": ("recording.wav", speechlike_wav(i), "audio/wav")},
    )
    check(r.status_code in (200, 201), f"upload recording {i}: {r.status_code} {r.text[:120]}")

r = c.post(f"{API}/voice-profiles/{pid}/train", headers=H)
check(r.status_code == 200, f"training queued: {r.text[:100]}")
for _ in range(60):
    p = c.get(f"{API}/voice-profiles/{pid}", headers=H).json()
    if p["status"] in ("ready", "failed"):
        break
    time.sleep(0.5)
check(p["status"] == "ready", f"training finished ready (got {p['status']}, err={p['training_error']})")

r = c.post(f"{API}/synthesis/generate", json={"text": "Hello from my cloned voice.", "voice_profile_id": pid}, headers=H)
check(r.status_code == 200, f"synthesis: {r.text[:150]}")
url = r.json()["audio_url"]
a = c.get(BASE + url if url.startswith("/") else url)
check(a.status_code == 200 and len(a.content) > 1000, "signed audio URL downloads")
check(c.get(BASE + url.split("?")[0]).status_code == 403, "unsigned audio URL rejected")
check(c.get(BASE + url.replace("sig=", "sig=0")).status_code == 403, "tampered signature rejected")

u = c.get(f"{API}/synthesis/usage", headers=H).json()
check(u["used"] == len("Hello from my cloned voice."), f"usage tracked {u}")
r = c.post(f"{API}/synthesis/generate", json={"text": "x" * 1000, "voice_profile_id": pid}, headers=H)
for _ in range(10):
    if r.status_code == 429:
        break
    r = c.post(f"{API}/synthesis/generate", json={"text": "x" * 1000, "voice_profile_id": pid}, headers=H)
check(r.status_code == 429, "monthly free limit enforced")

# other users can't touch this profile
email2 = f"e2e-{uuid.uuid4().hex[:8]}@example.com"
c.post(f"{API}/auth/register", json={"email": email2, "password": "password123", "full_name": "Other"})
t2 = c.post(f"{API}/auth/login", json={"email": email2, "password": "password123"}).json()["access_token"]
H2 = {"Authorization": f"Bearer {t2}"}
check(c.get(f"{API}/voice-profiles/{pid}", headers=H2).status_code == 404, "other user cannot read profile")
r = c.post(f"{API}/synthesis/generate", json={"text": "hi", "voice_profile_id": pid}, headers=H2)
check(r.status_code == 400, "other user cannot synthesize with my voice")

check(c.delete(f"{API}/voice-profiles/{pid}", headers=H).status_code == 204, "profile deleted")
print("ALL E2E CHECKS PASSED")
