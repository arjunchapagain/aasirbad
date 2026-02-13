"""
Audio utility functions for processing, validation, and format conversion.

Uses soundfile + scipy for core operations (always available).
librosa is used only if installed (optional ML extra).
"""

import io
import struct
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

from app.config import get_settings

settings = get_settings()

# Optional: librosa for advanced resampling
try:
    import librosa
    _HAS_LIBROSA = True
except ImportError:
    _HAS_LIBROSA = False


def validate_audio_file(file_bytes: bytes, filename: str) -> dict:
    """
    Validate an uploaded audio file.

    Returns dict with 'valid' bool and either metadata or 'error' message.
    """
    allowed_extensions = {".wav", ".mp3", ".flac", ".ogg", ".webm"}
    ext = Path(filename).suffix.lower()

    if ext not in allowed_extensions:
        return {"valid": False, "error": f"Unsupported audio format: {ext}. Allowed: {allowed_extensions}"}

    if len(file_bytes) < 1000:
        return {"valid": False, "error": "Audio file is too small - likely empty or corrupted"}

    if len(file_bytes) > 50 * 1024 * 1024:  # 50MB limit
        return {"valid": False, "error": "Audio file exceeds 50MB size limit"}

    # Load and analyze audio
    try:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=True) as tmp:
            tmp.write(file_bytes)
            tmp.flush()

            if _HAS_LIBROSA:
                audio, sr = librosa.load(tmp.name, sr=None)
            else:
                audio, sr = sf.read(tmp.name, dtype="float32")
                if audio.ndim > 1:
                    audio = np.mean(audio, axis=1)
    except Exception as e:
        return {"valid": False, "error": f"Cannot read audio file: {e}"}

    duration = len(audio) / sr

    if duration < 1.0:
        return {"valid": False, "error": "Recording too short - minimum 1 second required"}

    if duration > settings.max_recording_duration_seconds:
        return {"valid": False, "error": f"Recording too long - maximum {settings.max_recording_duration_seconds} seconds"}

    return {
        "valid": True,
        "duration_seconds": round(duration, 2),
        "sample_rate": sr,
        "channels": 1 if audio.ndim == 1 else audio.shape[0],
        "file_size_bytes": len(file_bytes),
    }


def compute_audio_quality_metrics(audio: np.ndarray, sr: int) -> dict:
    """
    Compute quality metrics for an audio recording.
    
    Returns:
        dict with snr_db, rms_level, clipping_detected, silence_ratio
    """
    # RMS level
    rms = np.sqrt(np.mean(audio**2))
    rms_db = 20 * np.log10(rms + 1e-10)

    # Signal-to-noise ratio (estimated)
    # Use the quietest 10% as noise floor estimate
    frame_length = int(0.025 * sr)  # 25ms frames
    hop_length = int(0.010 * sr)  # 10ms hop

    if _HAS_LIBROSA:
        frames = librosa.util.frame(audio, frame_length=frame_length, hop_length=hop_length)
    else:
        # Manual framing without librosa
        n_frames = 1 + (len(audio) - frame_length) // hop_length
        frames = np.stack([audio[i * hop_length : i * hop_length + frame_length] for i in range(n_frames)], axis=1)
    frame_rms = np.sqrt(np.mean(frames**2, axis=0))

    sorted_rms = np.sort(frame_rms)
    noise_floor = np.mean(sorted_rms[: max(1, len(sorted_rms) // 10)])
    signal_level = np.mean(sorted_rms[len(sorted_rms) // 2 :])

    snr_db = 20 * np.log10((signal_level + 1e-10) / (noise_floor + 1e-10))

    # Clipping detection
    clipping_threshold = 0.99
    clipping_samples = np.sum(np.abs(audio) > clipping_threshold)
    clipping_detected = clipping_samples > len(audio) * 0.001  # >0.1% samples

    # Silence ratio (using energy-based VAD)
    silence_threshold = noise_floor * 2
    silence_frames = np.sum(frame_rms < silence_threshold)
    silence_ratio = silence_frames / len(frame_rms)

    return {
        "snr_db": round(float(snr_db), 2),
        "rms_level": round(float(rms_db), 2),
        "clipping_detected": bool(clipping_detected),
        "silence_ratio": round(float(silence_ratio), 3),
    }


def resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """Resample audio to target sample rate."""
    if orig_sr == target_sr:
        return audio
    if _HAS_LIBROSA:
        return librosa.resample(audio, orig_sr=orig_sr, target_sr=target_sr)
    # Fallback: linear interpolation via scipy
    from scipy.signal import resample as scipy_resample
    target_length = int(len(audio) * target_sr / orig_sr)
    return scipy_resample(audio, target_length).astype(np.float32)


def normalize_audio(audio: np.ndarray, target_db: float = -20.0) -> np.ndarray:
    """Normalize audio to a target RMS dB level."""
    rms = np.sqrt(np.mean(audio**2))
    current_db = 20 * np.log10(rms + 1e-10)
    gain_db = target_db - current_db
    gain_linear = 10 ** (gain_db / 20)
    normalized = audio * gain_linear
    # Prevent clipping
    max_val = np.max(np.abs(normalized))
    if max_val > 0.95:
        normalized = normalized * (0.95 / max_val)
    return normalized


def audio_to_wav_bytes(audio: np.ndarray, sr: int) -> bytes:
    """Convert numpy audio array to WAV bytes."""
    buffer = io.BytesIO()
    sf.write(buffer, audio, sr, format="WAV", subtype="PCM_16")
    buffer.seek(0)
    return buffer.read()


def load_audio_from_bytes(file_bytes: bytes, target_sr: int | None = None) -> tuple[np.ndarray, int]:
    """Load audio from bytes, optionally resampling."""
    buffer = io.BytesIO(file_bytes)
    audio, sr = sf.read(buffer, dtype="float32")

    # Convert to mono if stereo
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    if target_sr and sr != target_sr:
        audio = resample_audio(audio, sr, target_sr)
        sr = target_sr

    return audio, sr
