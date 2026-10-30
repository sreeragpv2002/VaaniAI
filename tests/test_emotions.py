"""
tests/test_emotions.py - Unit tests for emotion, vocalization, and delivery tags.

Verifies:
1. All required emotion tags ([weak], [angry], [bored], [menacing], [playful], [tired], [excited]).
2. All required vocalizations ([clears throat], [coughing], [chuckling], [sighing], etc.).
3. All delivery styles ([whispering], [singing], [slowly], [softly], [pause], [voice breaking]).
4. Character voice ([sleepy drowsy voice]).
5. Tags are completely stripped from spoken text (never spoken aloud).
6. Tags map to proper Parler and SSML prosody parameters.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.text_processing.text_normalizer import TextNormalizer
from src.emotion.tag_mapper import TagMapper, TAG_DEFINITIONS
from src.languages.english import EnglishLanguageProcessor


def test_all_tags_registered():
    """Ensures every required tag is registered in TAG_DEFINITIONS."""
    required_tags = [
        # Emotions
        "weak", "angry", "bored", "menacing", "playful", "tired", "excited",
        # Vocalizations
        "clears throat", "coughing", "chuckling", "sighing", "sniffling",
        "yawning", "laughing", "sharp exhale", "scoffing", "humming", "panting", "gasping",
        # Delivery
        "whispering", "singing", "slowly", "softly", "pause", "voice breaking",
        # Character Voice
        "sleepy drowsy voice"
    ]

    for tag in required_tags:
        profile = TagMapper.get_profile(tag)
        assert profile is not None, f"Tag '[{tag}]' is missing from TagMapper!"
        assert profile.pace, f"Tag '[{tag}]' has empty pace"
        assert profile.pitch, f"Tag '[{tag}]' has empty pitch"
        assert profile.parler_tone, f"Tag '[{tag}]' has empty parler_tone"
        assert profile.ssml_rate, f"Tag '[{tag}]' has empty ssml_rate"
    print(f"PASS: All {len(required_tags)} required tags are fully defined with prosody profiles.")


def test_tags_are_stripped_from_spoken_text():
    """Verifies tags are never included in the text sent to the voice synthesizer."""
    sample_text = (
        "[whispering] 'Be quiet,' she warned. "
        "[angry] 'How dare you enter without permission!' he shouted. "
        "[sighing] [tired] It has been such an exhausting journey. "
        "[clears throat] [pause] May I have your attention, please?"
    )

    processor = EnglishLanguageProcessor()
    segments = processor.process_text(sample_text)

    for seg in segments:
        assert "[" not in seg.spoken_text and "]" not in seg.spoken_text, (
            f"Tag was not stripped from spoken text: '{seg.spoken_text}'"
        )
        assert len(seg.tags) > 0, f"Expected tags for segment: '{seg.original_text}'"

    print("PASS: Tags are cleanly extracted and stripped from spoken text (never spoken aloud).")


def test_prosody_mapping():
    """Verifies that tags alter prosody without altering the speaker identity."""
    processor = EnglishLanguageProcessor(gender="male")
    segments = processor.process_text("[whispering] 'Do not make a sound.' [excited] 'We found it!'")

    assert len(segments) == 2
    whisper_seg = segments[0]
    excited_seg = segments[1]

    # Verify both use the exact same base speaker 'Thoma'
    assert "Thoma" in whisper_seg.parler_description
    assert "Thoma" in excited_seg.parler_description

    # Verify prosody varies based on the tag
    assert "whisper" in whisper_seg.parler_description.lower()
    assert "-14%" in whisper_seg.ssml_markup or "-10Hz" in whisper_seg.ssml_markup

    assert "excited" in excited_seg.parler_description.lower() or "exuberant" in excited_seg.parler_description.lower()
    assert "+18%" in excited_seg.ssml_markup or "+14Hz" in excited_seg.ssml_markup

    print("PASS: Tags correctly modulate prosody while preserving consistent base speaker identity.")


if __name__ == "__main__":
    print("=" * 70)
    print("RUNNING EMOTION & TAG UNIT TESTS")
    print("=" * 70)
    test_all_tags_registered()
    test_tags_are_stripped_from_spoken_text()
    test_prosody_mapping()
    print("=" * 70)
    print("ALL EMOTION TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)
