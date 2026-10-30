"""
tests/test_voice_cloner.py - Self-check unit tests for VoiceCloner.
"""

import sys
from pathlib import Path
import pytest

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.audio.voice_cloner import VoiceCloner


def test_voice_cloner_availability_check():
    """Verifies that is_available returns a boolean without throwing."""
    available = VoiceCloner.is_available()
    assert isinstance(available, bool)
    print(f"PASS: VoiceCloner availability check (is_available={available})")


def test_voice_cloner_missing_file_handling(tmp_path):
    """Missing input and reference files fail before invoking OpenVoice."""
    existing_file = tmp_path / "existing.wav"
    existing_file.touch()

    with pytest.raises(FileNotFoundError):
        VoiceCloner.clone(
            input_audio_path=str(tmp_path / "missing-input.wav"),
            ref_audio_path=str(existing_file),
        )

    with pytest.raises(FileNotFoundError):
        VoiceCloner.clone(
            input_audio_path=str(existing_file),
            ref_audio_path=str(tmp_path / "missing-reference.wav"),
        )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
