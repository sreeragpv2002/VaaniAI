"""
src/audio/audio_processor.py - Anti-click edge smoothing, silence creation, and loudness normalization.
"""

import numpy as np


class AudioProcessor:
    """Provides studio-grade audio smoothing and volume normalization routines."""

    @staticmethod
    def create_silence(duration_sec: float, sample_rate: int) -> np.ndarray:
        """Generates a zero-amplitude float32 array for a given duration in seconds."""
        num_samples = int(sample_rate * max(0.01, duration_sec))
        return np.zeros(num_samples, dtype=np.float32)

    @staticmethod
    def apply_fade_edges(audio: np.ndarray, sample_rate: int, fade_ms: float = 12.0) -> np.ndarray:
        """
        Applies a smooth raised-cosine (Hann window) taper to segment boundaries
        to eliminate audio clicks, pops, and phase discontinuities.
        """
        if audio.ndim > 1:
            audio = audio.squeeze()

        fade_samples = int(sample_rate * (fade_ms / 1000.0))
        if len(audio) <= 2 * fade_samples or fade_samples <= 0:
            return audio.copy()

        processed = audio.copy().astype(np.float32)
        fade_in = 0.5 * (1.0 - np.cos(np.linspace(0, np.pi, fade_samples)))
        fade_out = 0.5 * (1.0 + np.cos(np.linspace(0, np.pi, fade_samples)))

        processed[:fade_samples] *= fade_in
        processed[-fade_samples:] *= fade_out
        return processed

    @staticmethod
    def normalize_audio(audio: np.ndarray, target_dbfs: float = -1.5) -> np.ndarray:
        """
        Normalizes peak amplitude to the target dBFS to maintain consistent,
        broadcast-standard loudness across varied emotional sentences.
        """
        if len(audio) == 0:
            return audio

        peak = np.max(np.abs(audio))
        if peak == 0.0:
            return audio

        target_linear = 10.0 ** (target_dbfs / 20.0)
        scaling = target_linear / peak
        normalized = audio * scaling

        # Hard clip safeguard to prevent digital distortion beyond [-1.0, 1.0]
        return np.clip(normalized, -0.999, 0.999)
