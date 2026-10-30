"""
src/text_processing/punctuation_handler.py - Punctuation classification and pause calculation.
"""

import re
from typing import Dict, Any


class PunctuationHandler:
    """Handles punctuation detection, dialogue identification, and dynamic pause calculation."""

    def __init__(self, pause_timings: Dict[str, float], pause_scale: float = 1.0):
        self.pause_timings = pause_timings
        self.pause_scale = max(0.2, min(3.0, pause_scale))

    def identify_punctuation(self, text: str) -> str:
        """Determines the primary terminal punctuation mark of a sentence segment."""
        text = text.strip()
        if text.endswith("...") or "..." in text:
            return "..."
        elif text.endswith("?"):
            return "?"
        elif text.endswith("!"):
            return "!"
        # Check if quoted dialogue contains question or exclamation before attribution
        elif '?"' in text or "?'" in text:
            return "?"
        elif '!"' in text or "!'" in text:
            return "!"
        elif text.endswith(","):
            return ","
        elif text.endswith(";"):
            return ";"
        elif text.endswith(":"):
            return ":"
        return "."

    def is_dialogue_segment(self, text: str) -> bool:
        """Checks if a segment contains or represents character dialogue in quotes."""
        text = text.strip()
        # Direct quotes in double or single quotes
        if re.search(r'["\'].+?["\']', text) or text.startswith(('"', "'")):
            return True
        return False

    def is_clause_continuation(self, text: str) -> bool:
        """Checks if the segment is a sub-clause ending with comma, semicolon, or dash."""
        text = text.strip()
        return bool(text.endswith((",", ";", ":", "-")))

    def calculate_pause(
        self,
        punct: str,
        is_clause: bool,
        has_pause_tag: bool = False,
        extra_pause_sec: float = 0.0
    ) -> float:
        """Calculates precise pause duration in seconds based on punctuation and emotion tags."""
        if has_pause_tag:
            base_pause = max(0.6, self.pause_timings.get("ellipsis", 0.85))
        elif is_clause:
            base_pause = self.pause_timings.get("comma", 0.20)
        elif punct == "...":
            base_pause = self.pause_timings.get("ellipsis", 0.85)
        elif punct == "?":
            base_pause = self.pause_timings.get("question", 0.45)
        elif punct == "!":
            base_pause = self.pause_timings.get("exclamation", 0.45)
        elif punct in (";", ":"):
            base_pause = self.pause_timings.get("semicolon", 0.28)
        else:
            base_pause = self.pause_timings.get("period", 0.35)

        total_pause = (base_pause + extra_pause_sec) * self.pause_scale
        return round(total_pause, 2)
