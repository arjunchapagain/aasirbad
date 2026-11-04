"""
TTS providers.

All voice cloning / speech synthesis goes through the TTSProvider interface so the
hosted vendor can be swapped without touching the rest of the app.

- DemoProvider: offline, no network. Produces placeholder audio (NOT a real clone).
  Lets the whole app run end to end without an API key.
- ElevenLabsProvider: real instant voice cloning via the ElevenLabs HTTP API.
"""

import io
import logging
import math
import re
import uuid
import wave
from abc import ABC, abstractmethod

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


class TTSError(RuntimeError):
    """Raised when the provider fails; message is safe to show to the user."""


class TTSProvider(ABC):
    name: str
    audio_ext: str
    media_type: str

    @abstractmethod
    def create_voice(self, name: str, samples: list[bytes]) -> str:
        """Create a cloned voice from audio samples. Returns an opaque provider voice id."""

    @abstractmethod
    def synthesize(self, text: str, voice_id: str) -> bytes:
        """Synthesize speech. Returns encoded audio bytes."""

    def delete_voice(self, voice_id: str) -> None:  # noqa: B027
        """Best-effort cleanup of a provider voice."""


class DemoProvider(TTSProvider):
    """Placeholder audio: a soft tone sequence whose rhythm follows the text."""

    name = "demo"
    audio_ext = ".wav"
    media_type = "audio/wav"
    _sr = 22050

    def create_voice(self, name: str, samples: list[bytes]) -> str:  # noqa: ARG002
        if not samples:
            raise TTSError("No audio samples provided")
        return f"demo-{uuid.uuid4().hex[:12]}"

    def synthesize(self, text: str, voice_id: str) -> bytes:
        # Pitch derived from voice id so each profile "sounds" different
        base = 140 + (int(voice_id.split("-")[-1][:4], 16) % 120)
        frames: list[int] = []
        for word in re.findall(r"\S+", text)[:200]:
            dur = min(0.45, 0.08 + 0.04 * len(word))
            freq = base + (sum(map(ord, word)) % 80)
            n = int(self._sr * dur)
            for i in range(n):
                env = math.sin(math.pi * i / n)
                frames.append(int(9000 * env * math.sin(2 * math.pi * freq * i / self._sr)))
            frames.extend([0] * int(self._sr * 0.06))
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(self._sr)
            w.writeframes(b"".join(f.to_bytes(2, "little", signed=True) for f in frames))
        return buf.getvalue()


class ElevenLabsProvider(TTSProvider):
    name = "elevenlabs"
    audio_ext = ".mp3"
    media_type = "audio/mpeg"
    _base = "https://api.elevenlabs.io/v1"

    def __init__(self) -> None:
        s = get_settings()
        if not s.elevenlabs_api_key:
            raise TTSError("ELEVENLABS_API_KEY is not configured")
        self._key = s.elevenlabs_api_key
        self._model = s.elevenlabs_model

    def _headers(self) -> dict[str, str]:
        return {"xi-api-key": self._key}

    def create_voice(self, name: str, samples: list[bytes]) -> str:
        files = [("files", (f"sample{i}.wav", b, "audio/wav")) for i, b in enumerate(samples)]
        try:
            r = httpx.post(
                f"{self._base}/voices/add", headers=self._headers(),
                data={"name": name[:100]}, files=files, timeout=120,
            )
        except httpx.HTTPError as e:
            logger.error("ElevenLabs create_voice network error: %s", e)
            raise TTSError("Voice service unreachable, try again later") from e
        if r.status_code >= 400:
            logger.error("ElevenLabs create_voice %s: %s", r.status_code, r.text[:300])
            raise TTSError(f"Voice service rejected the samples (HTTP {r.status_code})")
        return r.json()["voice_id"]

    def synthesize(self, text: str, voice_id: str) -> bytes:
        try:
            r = httpx.post(
                f"{self._base}/text-to-speech/{voice_id}", headers=self._headers(),
                json={"text": text, "model_id": self._model}, timeout=120,
            )
        except httpx.HTTPError as e:
            logger.error("ElevenLabs synthesize network error: %s", e)
            raise TTSError("Voice service unreachable, try again later") from e
        if r.status_code >= 400:
            logger.error("ElevenLabs synthesize %s: %s", r.status_code, r.text[:300])
            raise TTSError(f"Voice service failed (HTTP {r.status_code})")
        return r.content

    def delete_voice(self, voice_id: str) -> None:
        try:
            httpx.delete(f"{self._base}/voices/{voice_id}", headers=self._headers(), timeout=30)
        except httpx.HTTPError:
            logger.warning("Could not delete provider voice %s", voice_id)


def get_provider() -> TTSProvider:
    name = get_settings().tts_provider
    if name == "elevenlabs":
        return ElevenLabsProvider()
    return DemoProvider()
