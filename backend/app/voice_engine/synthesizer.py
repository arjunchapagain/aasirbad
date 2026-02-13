"""
Voice Synthesizer.

Generates speech from text using Tortoise TTS with trained voice conditioning latents.
Supports multiple quality presets for speed/quality tradeoff.
"""

import logging

import numpy as np
import torch

from app.config import get_settings
from app.voice_engine.trainer import VoiceTrainer

logger = logging.getLogger(__name__)
settings = get_settings()

# Tortoise TTS quality presets
QUALITY_PRESETS = {
    "ultra_fast": {
        "num_autoregressive_samples": 1,
        "diffusion_iterations": 10,
        "cond_free": False,
    },
    "fast": {
        "num_autoregressive_samples": 4,
        "diffusion_iterations": 30,
        "cond_free": False,
    },
    "standard": {
        "num_autoregressive_samples": 16,
        "diffusion_iterations": 100,
        "cond_free": True,
    },
    "high_quality": {
        "num_autoregressive_samples": 64,
        "diffusion_iterations": 200,
        "cond_free": True,
    },
}


class VoiceSynthesizer:
    """
    Generates speech from text using a trained voice model.

    Uses Tortoise TTS with conditioning latents extracted during training
    to produce speech that mimics the target speaker's voice.
    """

    def __init__(self, device: str | None = None):
        self.device = device or settings.torch_device
        self._tts = None

    def _get_tts(self):
        """Lazy-load Tortoise TTS model."""
        if self._tts is None:
            logger.info(f"Loading Tortoise TTS for synthesis on device: {self.device}")
            from tortoise.api import TextToSpeech

            self._tts = TextToSpeech(
                device=self.device,
                autoregressive_batch_size=1,
            )
            logger.info("Tortoise TTS loaded for synthesis")
        return self._tts

    def generate_speech(
        self,
        text: str,
        voice_model_bytes: bytes,
        preset: str = "fast",
    ) -> tuple[np.ndarray, int]:
        """
        Generate speech from text using a trained voice model.

        Args:
            text: Text to convert to speech
            voice_model_bytes: Serialized voice conditioning latents
            preset: Quality preset (ultra_fast, fast, standard, high_quality)

        Returns:
            Tuple of (audio_array, sample_rate)
        """
        if preset not in QUALITY_PRESETS:
            raise ValueError(
                f"Unknown preset: {preset}. "
                f"Choose from: {list(QUALITY_PRESETS.keys())}",
            )

        logger.info(f"Generating speech: '{text[:50]}...' with preset={preset}")

        # Load TTS model
        tts = self._get_tts()

        # Load voice conditioning latents
        gpt_cond_latent, speaker_embedding = VoiceTrainer.deserialize_latents(voice_model_bytes)

        # Move to device
        gpt_cond_latent = gpt_cond_latent.to(self.device)
        speaker_embedding = speaker_embedding.to(self.device)

        # Get preset parameters
        QUALITY_PRESETS[preset]

        # Generate speech
        with torch.no_grad():
            audio = tts.tts_with_preset(
                text,
                voice_samples=None,  # Using pre-computed latents instead
                conditioning_latents=(gpt_cond_latent, speaker_embedding),
                preset=preset,
            )

        # Convert to numpy
        if isinstance(audio, torch.Tensor):
            audio_np = audio.squeeze().cpu().numpy()
        else:
            audio_np = np.array(audio).squeeze()

        # Tortoise outputs at 24000 Hz
        sample_rate = 24000

        logger.info(f"Generated {len(audio_np)/sample_rate:.2f}s of audio")

        return audio_np, sample_rate

    def generate_speech_streaming(
        self,
        text: str,
        voice_model_bytes: bytes,
        preset: str = "fast",
        chunk_size: int = 4096,
    ):
        """
        Generator that yields audio chunks for streaming playback.

        Useful for real-time audio streaming over WebSocket.
        """
        audio, sr = self.generate_speech(text, voice_model_bytes, preset)

        # Yield in chunks
        for i in range(0, len(audio), chunk_size):
            chunk = audio[i : i + chunk_size]
            yield chunk, sr
