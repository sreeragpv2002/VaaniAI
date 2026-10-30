"""
tests/test_malayalam.py - Unit tests for Malayalam text and narration processing.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.languages.malayalam import MalayalamLanguageProcessor


def test_malayalam_sentence_splitting():
    """Verifies Malayalam sentence segmentation, abbreviations, and dialogue."""
    text = (
        "ശ്രീ. മാധവൻ നായർ രാവിലെ എട്ടുമണിക്ക് വീട്ടിൽ തിരിച്ചെത്തി. "
        '"ഇവിടെ എന്താണ് സംഭവിച്ചത്?" അദ്ദേഹം അമ്പരപ്പോടെ ചോദിച്ചു. '
        '"ഒന്നുമില്ല, എല്ലാം ശാന്തമാണ്!" മുത്തശ്ശി ചിരിയോടെ മറുപടി നൽകി.'
    )

    processor = MalayalamLanguageProcessor(gender="male")
    segments = processor.process_text(text)

    assert len(segments) == 3, f"Expected 3 segments, got {len(segments)}"
    assert "ശ്രീ. മാധവൻ നായർ" in segments[0].spoken_text
    assert segments[1].punctuation == "?"
    assert segments[2].punctuation == "!"

    print("PASS: Malayalam sentence segmentation with script, abbreviations, and dialogue.")


def test_malayalam_consistent_voice_and_emotions():
    """Verifies that Malayalam maintains the exact same base voice with emotion modulation."""
    text = (
        "മഴ പെയ്തൊഴിഞ്ഞ ഒരു ശാന്തമായ വൈകുന്നേരം. "
        "[whispering] 'വാതിൽ തുറക്കരുത്!' ഉള്ളിൽ നിന്ന് കുട്ടി ഭയത്തോടെ നിലവിളിച്ചു. "
        "[excited] 'നമുക്ക് സമ്മാനം ലഭിച്ചു!' അമ്മ ആഹ്ലാദത്തോടെ പറഞ്ഞു."
    )

    processor = MalayalamLanguageProcessor(gender="male")
    segments = processor.process_text(text)

    for seg in segments:
        # Every segment must maintain the exact same base speaker 'Harish'
        assert "Harish" in seg.parler_description, f"Voice changed on segment: {seg.spoken_text}"
        # Tags must be stripped from spoken text
        assert "[" not in seg.spoken_text and "]" not in seg.spoken_text

    # Verify tags influenced prosody
    assert segments[1].tags == ["whispering"]
    assert "-14%" in segments[1].ssml_markup or "-10Hz" in segments[1].ssml_markup

    assert segments[2].tags == ["excited"]
    assert "+18%" in segments[2].ssml_markup or "+14Hz" in segments[2].ssml_markup

    print("PASS: Malayalam consistent base voice with emotion and vocalization tags.")


if __name__ == "__main__":
    print("=" * 70)
    print("RUNNING MALAYALAM PROCESSING TESTS")
    print("=" * 70)
    test_malayalam_sentence_splitting()
    test_malayalam_consistent_voice_and_emotions()
    print("=" * 70)
    print("ALL MALAYALAM TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)
