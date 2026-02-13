"""Tests for audio utility functions."""

import struct

import numpy as np

from app.utils.audio import (
    compute_audio_quality_metrics,
    load_audio_from_bytes,
    normalize_audio,
    validate_audio_file,
)


def _generate_wav_bytes(
    duration_s: float = 1.0,
    sample_rate: int = 16000,
    channels: int = 1,
    bits_per_sample: int = 16,
) -> bytes:
    """Generate a valid WAV file in memory with a sine wave tone."""
    import math

    num_samples = int(sample_rate * duration_s)
    frequency = 440.0  # A4 note
    amplitude = 0.5

    # Generate sine wave samples
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        value = amplitude * math.sin(2 * math.pi * frequency * t)
        sample = int(value * 32767)
        samples.append(struct.pack("<h", max(-32768, min(32767, sample))))

    data = b"".join(samples)
    data_size = len(data)
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8

    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + data_size,
        b"WAVE",
        b"fmt ",
        16,
        1,  # PCM
        channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b"data",
        data_size,
    )
    return header + data


class TestAudioValidation:
    """Test audio file validation."""

    def test_validate_valid_wav(self):
        """Test validation of a properly formatted WAV file."""
        wav_data = _generate_wav_bytes(duration_s=3.0)
        result = validate_audio_file(wav_data, "recording.wav")
        assert result["valid"] is True

    def test_validate_too_short(self):
        """Test rejection of audio that's too short."""
        wav_data = _generate_wav_bytes(duration_s=0.1)
        result = validate_audio_file(wav_data, "short.wav")
        assert result["valid"] is False

    def test_validate_unsupported_format(self):
        """Test rejection of unsupported file format."""
        result = validate_audio_file(b"not audio data", "file.xyz")
        assert result["valid"] is False


class TestAudioQualityMetrics:
    """Test audio quality metric computation."""

    def test_compute_metrics_valid(self):
        """Test computing metrics on valid audio."""
        wav_data = _generate_wav_bytes(duration_s=2.0)
        audio, sr = load_audio_from_bytes(wav_data)
        metrics = compute_audio_quality_metrics(audio, sr)
        assert "snr_db" in metrics
        assert "rms_level" in metrics
        assert "clipping_detected" in metrics
        assert "silence_ratio" in metrics
        assert isinstance(metrics["snr_db"], float)


class TestNormalization:
    """Test audio normalization."""

    def test_normalize_returns_audio(self):
        """Test that normalization returns valid audio data."""
        wav_data = _generate_wav_bytes(duration_s=1.0)
        audio, sr = load_audio_from_bytes(wav_data)
        result = normalize_audio(audio, target_db=-20.0)
        assert isinstance(result, np.ndarray)
        assert len(result) > 0
