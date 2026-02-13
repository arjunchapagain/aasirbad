"""
Audio Preprocessor.

Handles audio preprocessing pipeline before training:
- Noise reduction
- Normalization
- Voice Activity Detection (VAD) trimming
- Resampling to target sample rate
- Quality validation

This ensures consistent, clean audio for voice model training.
"""

import io
import logging
from typing import NamedTuple

import librosa
import numpy as np
import noisereduce as nr
import soundfile as sf

from app.config import get_settings
from app.utils.audio import compute_audio_quality_metrics, normalize_audio, resample_audio

logger = logging.getLogger(__name__)
settings = get_settings()


class ProcessedAudio(NamedTuple):
    """Result of audio preprocessing."""

    audio: np.ndarray
    sample_rate: int
    duration_seconds: float
    quality_metrics: dict


class AudioPreprocessor:
    """
    Professional audio preprocessing pipeline for voice cloning.
    
    Pipeline steps:
    1. Load and convert to mono
    2. Resample to target sample rate (22050 Hz for Tortoise)
    3. Apply noise reduction (spectral gating)
    4. Trim silence from beginning and end
    5. Normalize audio levels
    6. Compute quality metrics
    """

    def __init__(
        self,
        target_sr: int = 22050,
        noise_reduction_strength: float = 0.7,
        silence_threshold_db: float = -40.0,
        target_loudness_db: float = -20.0,
    ):
        self.target_sr = target_sr
        self.noise_reduction_strength = noise_reduction_strength
        self.silence_threshold_db = silence_threshold_db
        self.target_loudness_db = target_loudness_db

    def process(self, audio_bytes: bytes) -> ProcessedAudio:
        """
        Run the full preprocessing pipeline on raw audio bytes.
        
        Args:
            audio_bytes: Raw audio file bytes (WAV, MP3, etc.)
            
        Returns:
            ProcessedAudio with cleaned audio and quality metrics
        """
        logger.info("Starting audio preprocessing pipeline")

        # Step 1: Load audio
        audio, sr = self._load_audio(audio_bytes)
        logger.info(f"Loaded audio: {len(audio)/sr:.2f}s at {sr}Hz")

        # Step 2: Resample
        audio = resample_audio(audio, sr, self.target_sr)
        sr = self.target_sr
        logger.info(f"Resampled to {sr}Hz")

        # Step 3: Noise reduction
        audio = self._reduce_noise(audio, sr)
        logger.info("Applied noise reduction")

        # Step 4: Trim silence
        audio = self._trim_silence(audio, sr)
        logger.info(f"Trimmed silence: {len(audio)/sr:.2f}s remaining")

        # Step 5: Normalize
        audio = normalize_audio(audio, target_db=self.target_loudness_db)
        logger.info(f"Normalized to {self.target_loudness_db}dB")

        # Step 6: Quality metrics
        quality = compute_audio_quality_metrics(audio, sr)
        logger.info(f"Quality metrics: SNR={quality['snr_db']}dB, RMS={quality['rms_level']}dB")

        duration = len(audio) / sr

        return ProcessedAudio(
            audio=audio,
            sample_rate=sr,
            duration_seconds=round(duration, 2),
            quality_metrics=quality,
        )

    def process_batch(self, audio_bytes_list: list[bytes]) -> list[ProcessedAudio]:
        """Process multiple audio files."""
        results = []
        for i, audio_bytes in enumerate(audio_bytes_list):
            logger.info(f"Processing recording {i+1}/{len(audio_bytes_list)}")
            try:
                result = self.process(audio_bytes)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process recording {i+1}: {e}")
                continue
        return results

    def _load_audio(self, audio_bytes: bytes) -> tuple[np.ndarray, int]:
        """Load audio from bytes and convert to mono float32."""
        buffer = io.BytesIO(audio_bytes)
        audio, sr = sf.read(buffer, dtype="float32")

        # Convert to mono if stereo
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)

        return audio, sr

    def _reduce_noise(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Apply spectral noise reduction.
        
        Uses noisereduce library which implements spectral gating:
        1. Estimates noise profile from quietest segments
        2. Creates a spectral gate to reduce noise below threshold
        3. Applies smoothly to preserve speech quality
        """
        try:
            reduced = nr.reduce_noise(
                y=audio,
                sr=sr,
                prop_decrease=self.noise_reduction_strength,
                stationary=False,  # Non-stationary noise (better for real-world recordings)
                n_fft=2048,
                hop_length=512,
            )
            return reduced
        except Exception as e:
            logger.warning(f"Noise reduction failed, using original audio: {e}")
            return audio

    def _trim_silence(
        self,
        audio: np.ndarray,
        sr: int,
        top_db: float = 25.0,
        frame_length: int = 2048,
        hop_length: int = 512,
    ) -> np.ndarray:
        """
        Trim leading and trailing silence from audio.
        
        Uses librosa's trim which is based on the signal being above
        a threshold in dB relative to the peak.
        """
        trimmed, _ = librosa.effects.trim(
            audio,
            top_db=top_db,
            frame_length=frame_length,
            hop_length=hop_length,
        )

        # Ensure minimum length (0.5 seconds)
        min_samples = int(0.5 * sr)
        if len(trimmed) < min_samples:
            logger.warning("Audio too short after trimming, using original")
            return audio

        # Add small silence padding (50ms) at start and end for natural sound
        pad_samples = int(0.05 * sr)
        padded = np.pad(trimmed, (pad_samples, pad_samples), mode="constant")

        return padded

    def to_wav_bytes(self, audio: np.ndarray, sr: int) -> bytes:
        """Convert processed audio to WAV bytes for storage."""
        buffer = io.BytesIO()
        sf.write(buffer, audio, sr, format="WAV", subtype="PCM_16")
        buffer.seek(0)
        return buffer.read()
