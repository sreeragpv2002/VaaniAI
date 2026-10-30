"""
src/emotion/context_analyzer.py - Contextual smoothing, prosody derivation, and emotion decay.
"""

from typing import Tuple, Optional
from .tag_mapper import TagProfile


class ContextAnalyzer:
    """Maintains emotional context across narrative sentences and derives prosody."""

    def __init__(self, base_speed: str = "moderate", expressiveness: str = "moderate"):
        self.base_speed = base_speed
        self.expressiveness = expressiveness
        self.prev_emotion = "neutral"
        self.prev_confidence = 0.0

    def smooth_emotion(
        self,
        current_emotion: str,
        current_confidence: float,
        sentence_text: str
    ) -> Tuple[str, float]:
        """
        Smooths emotion transitions, decays past momentum, and ensures scene-setting
        narration does not carry over unwarranted anger or shouting.
        """
        words = sentence_text.lower().split()

        # If current sentence has clear emotion, update context
        if current_confidence >= 0.45:
            self.prev_emotion = current_emotion
            self.prev_confidence = current_confidence
            return current_emotion, current_confidence

        # Check if sentence is neutral descriptive scene-setting
        is_scene_desc = any(w in words for w in [
            "outside", "courtyard", "leaves", "trees", "room", "sky", "morning",
            "sun", "palace", "chamber", "river", "boats", "തോട്ടം", "മുറി", "ആകാശം", "പുഴ"
        ])

        # If previous emotion exists and not anger/shouting into scene description
        if self.prev_emotion not in ("neutral", "anger") and not is_scene_desc and self.prev_confidence > 0.5:
            decayed_conf = self.prev_confidence * 0.60
            if decayed_conf > 0.35:
                return self.prev_emotion, decayed_conf

        self.prev_emotion = "neutral"
        self.prev_confidence = 0.0
        return "neutral", 0.0

    def derive_prosody(
        self,
        emotion: str,
        punctuation: str,
        tag_profile: Optional[TagProfile] = None
    ) -> Tuple[str, str, str, str, str]:
        """
        Derives pace, pitch, ssml_rate, ssml_pitch, and ssml_volume.
        If an explicit tag_profile exists, it takes precedence.
        Returns: (pace, pitch, ssml_rate, ssml_pitch, ssml_volume)
        """
        # If an explicit tag profile is present, use its defined characteristics
        if tag_profile is not None:
            return (
                tag_profile.pace,
                tag_profile.pitch,
                tag_profile.ssml_rate,
                tag_profile.ssml_pitch,
                tag_profile.ssml_volume
            )

        # Baseline mappings
        pace = self.base_speed
        pitch = "balanced"
        ssml_rate = "+0%"
        ssml_pitch = "+0Hz"
        ssml_volume = "+0%"

        if emotion == "happy":
            pace = "brisk" if self.base_speed in ("moderate", "brisk") else self.base_speed
            pitch = "bright and cheerful"
            ssml_rate = "+12%"
            ssml_pitch = "+12Hz"
        elif emotion == "anger":
            pace = "brisk"
            pitch = "firm and commanding"
            ssml_rate = "+14%"
            ssml_pitch = "+6Hz"
            ssml_volume = "+10%"
        elif emotion == "sad":
            pace = "slow and measured"
            pitch = "low and solemn"
            ssml_rate = "-14%"
            ssml_pitch = "-8Hz"
        elif emotion == "fear":
            pace = "brisk"
            pitch = "trembling and tense"
            ssml_rate = "+12%"
            ssml_pitch = "+8Hz"
        elif emotion == "surprise":
            pace = "brisk"
            pitch = "high and astonished"
            ssml_rate = "+14%"
            ssml_pitch = "+14Hz"
        elif emotion == "suspense":
            pace = "slow and deliberate"
            pitch = "low and hushed"
            ssml_rate = "-16%"
            ssml_pitch = "-10Hz"
        elif emotion == "curiosity":
            pace = "measured"
            pitch = "inquiring with upward inflection"
            ssml_rate = "-5%"
            ssml_pitch = "+8Hz"
        elif emotion == "warmth":
            pace = "gentle and steady"
            pitch = "warm and mellow"
            ssml_rate = "-6%"
            ssml_pitch = "-3Hz"

        # Punctuation adjustments
        if punctuation == "...":
            pace = "slow and thoughtful"
            ssml_rate = "-18%"
        elif punctuation == "?" and ssml_pitch == "+0Hz":
            pitch = "inquiring with upward inflection"
            ssml_pitch = "+8Hz"

        # Apply expressiveness scaling
        if self.expressiveness == "subtle":
            ssml_rate = "+0%"
        elif self.expressiveness == "dramatic":
            # Amplify pitch inflection
            if ssml_pitch.startswith("+"):
                val = int(ssml_pitch.replace("+", "").replace("Hz", ""))
                ssml_pitch = f"+{int(val * 1.3)}Hz"

        return pace, pitch, ssml_rate, ssml_pitch, ssml_volume
