"""
Voice Trainer.

Handles voice model training using Tortoise TTS.
Tortoise uses "conditioning latents" extracted from reference audio
to clone a voice. This module:

1. Takes preprocessed audio samples
2. Extracts voice conditioning latents (voice embedding)
3. Saves the latents as the "voice model" for synthesis

For Tortoise TTS, training is actually latent extraction - it doesn't
fine-tune the base model but creates voice-specific conditioning tensors
that guide generation to sound like the target speaker.
"""

import io
import logging
import tempfile
from pathlib import Path

import torch
import torchaudio

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class VoiceTrainer:
    """
    Trains (extracts conditioning latents) a voice model from audio samples.

    Tortoise TTS approach:
    - Load reference audio clips
    - Run through autoregressive encoder to get voice embeddings
    - Average embeddings across clips for robust representation
    - Save conditioning latents for later synthesis
    """

    def __init__(self, device: str | None = None):
        self.device = device or settings.torch_device
        self._tts = None

    def _get_tts(self):
        """Lazy-load Tortoise TTS model."""
        if self._tts is None:
            logger.info(f"Loading Tortoise TTS on device: {self.device}")
            from tortoise.api import TextToSpeech

            self._tts = TextToSpeech(
                device=self.device,
                autoregressive_batch_size=1,  # Conservative for memory
            )
            logger.info("Tortoise TTS loaded successfully")
        return self._tts

    def train(
        self,
        audio_samples: list[bytes],
        progress_callback: callable | None = None,
    ) -> bytes:
        """
        Extract voice conditioning latents from audio samples.

        Args:
            audio_samples: List of preprocessed WAV audio bytes
            progress_callback: Optional callback(progress: float, step: str)

        Returns:
            Serialized voice model (conditioning latents) as bytes
        """
        if len(audio_samples) < 1:
            raise ValueError("At least 1 audio sample required")

        total_steps = len(audio_samples) + 2  # samples + load + save
        current_step = 0

        def report(step_name: str):
            nonlocal current_step
            current_step += 1
            progress = current_step / total_steps
            logger.info(f"Training step [{current_step}/{total_steps}]: {step_name}")
            if progress_callback:
                progress_callback(progress, step_name)

        # Step 1: Load TTS engine
        report("Loading Tortoise TTS engine")
        tts = self._get_tts()

        # Step 2: Load and prepare audio clips
        voice_clips = []
        for i, sample_bytes in enumerate(audio_samples):
            report(f"Processing audio sample {i+1}/{len(audio_samples)}")

            # Save to temp file (Tortoise expects file paths)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(sample_bytes)
                tmp_path = tmp.name

            try:
                # Load audio tensor
                audio, sr = torchaudio.load(tmp_path)

                # Resample to 22050 if needed
                if sr != 22050:
                    resampler = torchaudio.transforms.Resample(sr, 22050)
                    audio = resampler(audio)

                # Convert to mono if stereo
                if audio.shape[0] > 1:
                    audio = audio.mean(dim=0, keepdim=True)

                # Squeeze to 1D
                audio = audio.squeeze()

                voice_clips.append(audio)
            finally:
                Path(tmp_path).unlink(missing_ok=True)

        # Step 3: Extract conditioning latents
        report("Extracting voice conditioning latents")

        # Tortoise's get_conditioning_latents expects list of audio tensors
        conditioning_latents = tts.get_conditioning_latents(
            voice_clips,
            return_mels=True,
        )

        # Step 4: Serialize latents
        report("Saving voice model")
        model_bytes = self._serialize_latents(conditioning_latents)

        logger.info(
            f"Voice training complete. Model size: {len(model_bytes) / 1024:.1f}KB, "
            f"Used {len(audio_samples)} samples",
        )

        return model_bytes

    def _serialize_latents(self, latents: tuple) -> bytes:
        """Serialize conditioning latents to bytes."""
        buffer = io.BytesIO()
        torch.save(
            {
                "gpt_cond_latent": latents[0],
                "speaker_embedding": latents[1],
                "version": "1.0",
                "engine": "tortoise-tts",
            },
            buffer,
        )
        buffer.seek(0)
        return buffer.read()

    @staticmethod
    def deserialize_latents(model_bytes: bytes) -> tuple:
        """Deserialize conditioning latents from bytes."""
        buffer = io.BytesIO(model_bytes)
        data = torch.load(buffer, map_location="cpu", weights_only=True)
        return data["gpt_cond_latent"], data["speaker_embedding"]
