"""
src/audio/audio_merger.py - Stitches audio chunks with punctuation pauses and exports WAV.
"""

from typing import List, Tuple
from pathlib import Path
import numpy as np
import soundfile as sf

from .audio_processor import AudioProcessor


class AudioMerger:
    """Merges sentence-level audio segments seamlessly with punctuation-aware pauses."""

    @staticmethod
    def merge_segments(
        segments_with_pauses: List[Tuple[np.ndarray, float]],
        sample_rate: int,
        fade_ms: float = 12.0,
        normalize: bool = True,
        target_dbfs: float = -1.5,
    ) -> np.ndarray:
        """
        Smooths edges of each segment, appends punctuation pause, concatenates,
        and normalizes volume.
        """
        stitched_chunks: List[np.ndarray] = []

        for idx, (audio, pause_sec) in enumerate(segments_with_pauses):
            if audio is None or len(audio) == 0:
                continue

            # 1. Smooth edges of spoken segment
            smoothed = AudioProcessor.apply_fade_edges(audio, sample_rate, fade_ms)
            stitched_chunks.append(smoothed)

            # 2. Append tailored silence pause after segment (except after final sentence)
            if idx < len(segments_with_pauses) - 1 and pause_sec > 0:
                pause_audio = AudioProcessor.create_silence(pause_sec, sample_rate)
                stitched_chunks.append(pause_audio)

        if not stitched_chunks:
            return np.zeros(sample_rate, dtype=np.float32)

        combined = np.concatenate(stitched_chunks)

        if normalize:
            combined = AudioProcessor.normalize_audio(combined, target_dbfs=target_dbfs)

        return combined

    @staticmethod
    def export_wav(filepath: str, audio: np.ndarray, sample_rate: int) -> str:
        """Writes audio array to disk in 16-bit PCM WAV format."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(path), audio, sample_rate, subtype="PCM_16")
        return str(path.resolve())
