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


def test_voice_cloner_missing_file_handling():
    """Verifies that VoiceCloner raises FileNotFoundError on non-existent input files."""
    try:
        VoiceCloner.clone(
            input_audio_path="non_existent_input.wav",
            ref_audio_path="input/actress.wav",
        )
        assert False, "Should have raised FileNotFoundError for missing input file"
    except FileNotFoundError:
        print("PASS: Missing input file raises FileNotFoundError correctly")

    try:
        VoiceCloner.clone(
            input_audio_path="input/actress.wav",
            ref_audio_path="non_existent_ref.wav",
        )
        assert False, "Should have raised FileNotFoundError for missing reference file"
    except FileNotFoundError:
        print("PASS: Missing reference file raises FileNotFoundError correctly")


if __name__ == "__main__":
    test_voice_cloner_availability_check()
    test_voice_cloner_missing_file_handling()
    print("ALL VOICE CLONER TESTS PASSED.")
