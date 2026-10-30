"""
src/utils/logger.py - Formatted logging for TTS narration progress.
"""

import sys
from typing import Any
from src.languages.english import ProcessedSegment


def setup_logger():
    """Configures console output encoding."""
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except AttributeError:
            pass


def log_segment(seg: ProcessedSegment, total: int, engine_type: str = "edge-tts"):
    """Prints formatted progress for each synthesized sentence segment."""
    tag_info = f" [TAGS: {', '.join(seg.tags)}]" if seg.tags else ""
    dialogue_info = " [DIALOGUE]" if seg.is_dialogue else " [NARRATION]"

    print("-" * 80)
    print(f"Segment [{seg.index:02d}/{total:02d}]{dialogue_info}{tag_info}")
    print(f"  * Spoken:        \"{seg.spoken_text}\"")
    print(f"  * Emotion:       {seg.emotion.upper()} (conf: {seg.confidence:.2f})")
    print(f"  * Punctuation:   '{seg.punctuation}' | Pause: {seg.pause_after_sec}s")
    print(f"  * Prosody:       Pace: {seg.pace} | Pitch: {seg.pitch}")
    if engine_type == "indic-parler":
        print(f"  * Prompt:        \"{seg.parler_description[:85]}...\"")
    else:
        print(f"  * SSML Prosody:  rate=\"{seg.ssml_rate}\" pitch=\"{seg.ssml_pitch}\" volume=\"{seg.ssml_volume}\"")
