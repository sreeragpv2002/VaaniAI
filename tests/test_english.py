"""
tests/test_english.py - Unit tests for Indian English text and narration processing.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.languages.english import EnglishLanguageProcessor


def test_english_sentence_splitting():
    """Verifies that abbreviations, decimals, and dialogue are handled without incorrect splits."""
    text = (
        'Dr. Sharma arrived at 10.30 a.m. to meet Mr. Verma at the laboratory. '
        '"Are the samples ready?" he asked eagerly. '
        '"Yes, everything is prepared!" replied Dr. Sharma with a smile.'
    )

    processor = EnglishLanguageProcessor(gender="male")
    segments = processor.process_text(text)

    # Should split into exactly 3 sentences
    assert len(segments) == 3, f"Expected 3 segments, got {len(segments)}"
    assert "Dr. Sharma arrived at 10.30 a.m." in segments[0].spoken_text
    assert "Are the samples ready?" in segments[1].spoken_text
    assert segments[1].punctuation == "?"
    assert segments[2].punctuation == "!"

    print("PASS: English sentence segmentation with abbreviations, decimals, and dialogue.")


def test_consistent_base_voice():
    """Verifies that the entire text maintains the exact same base voice across varied emotions."""
    text = (
        "It was a peaceful morning in Kochi. "
        "Suddenly, a thunderous explosion shook the walls! "
        "He walked cautiously towards the door... and listened. "
        '"Who is there?" he demanded angrily.'
    )

    processor = EnglishLanguageProcessor(gender="female")
    segments = processor.process_text(text)

    for seg in segments:
        # Every segment must use the exact same base speaker 'Mary'
        assert "Mary" in seg.parler_description, f"Voice changed on segment: {seg.spoken_text}"

    # Punctuation pauses should vary
    assert segments[0].pause_after_sec == 0.35  # Period
    assert segments[1].pause_after_sec == 0.45  # Exclamation
    assert segments[2].pause_after_sec == 0.85  # Ellipsis

    print("PASS: Single consistent base voice maintained with dynamic context-aware prosody.")


if __name__ == "__main__":
    print("=" * 70)
    print("RUNNING ENGLISH PROCESSING TESTS")
    print("=" * 70)
    test_english_sentence_splitting()
    test_consistent_base_voice()
    print("=" * 70)
    print("ALL ENGLISH TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)
