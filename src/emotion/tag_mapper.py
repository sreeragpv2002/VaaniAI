"""
src/emotion/tag_mapper.py - Explicit emotion, vocalization, and delivery tag mapper.

Maps bracketed tags ([angry], [whispering], [clears throat], etc.) to prosodic
parameters and descriptive conditioning prompts for both Parler-TTS and Edge-TTS.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class TagProfile:
    """Represents vocal and prosodic parameters derived from explicit tags."""
    pace: str
    pitch: str
    ssml_rate: str
    ssml_pitch: str
    ssml_volume: str
    parler_tone: str
    extra_pause_sec: float = 0.0
    has_pause: bool = False


# Comprehensive registry of all required tags
TAG_DEFINITIONS: Dict[str, TagProfile] = {
    # --- Emotion Tags ---
    "weak": TagProfile(
        pace="slow",
        pitch="faint and low",
        ssml_rate="-18%",
        ssml_pitch="-6Hz",
        ssml_volume="-20%",
        parler_tone="a weak, feeble, and frail tone with delicate fragility"
    ),
    "angry": TagProfile(
        pace="brisk",
        pitch="firm and commanding",
        ssml_rate="+15%",
        ssml_pitch="+6Hz",
        ssml_volume="+15%",
        parler_tone="a fierce, angry, and commanding tone filled with sharp indignation"
    ),
    "bored": TagProfile(
        pace="slow and flat",
        pitch="monotone and low",
        ssml_rate="-12%",
        ssml_pitch="-4Hz",
        ssml_volume="-5%",
        parler_tone="a flat, bored, and indifferent monotone"
    ),
    "menacing": TagProfile(
        pace="slow and deliberate",
        pitch="deep and sinister",
        ssml_rate="-14%",
        ssml_pitch="-10Hz",
        ssml_volume="+5%",
        parler_tone="a dark, menacing, and sinister tone with quiet malice"
    ),
    "playful": TagProfile(
        pace="lively and brisk",
        pitch="bright and buoyant",
        ssml_rate="+10%",
        ssml_pitch="+10Hz",
        ssml_volume="+0%",
        parler_tone="a lighthearted, playful, and teasing tone"
    ),
    "tired": TagProfile(
        pace="sluggish and slow",
        pitch="low and heavy",
        ssml_rate="-16%",
        ssml_pitch="-6Hz",
        ssml_volume="-10%",
        parler_tone="a weary, exhausted, and tired voice burdened with fatigue"
    ),
    "excited": TagProfile(
        pace="brisk and rapid",
        pitch="bright and elevated",
        ssml_rate="+18%",
        ssml_pitch="+14Hz",
        ssml_volume="+10%",
        parler_tone="an enthusiastic, excited, and exuberant tone full of energy"
    ),

    # --- Vocalizations ---
    "clears throat": TagProfile(
        pace="moderate",
        pitch="balanced",
        ssml_rate="+0%",
        ssml_pitch="+0Hz",
        ssml_volume="+0%",
        parler_tone="a composed, deliberate tone as if clearing one's throat",
        extra_pause_sec=0.45
    ),
    "coughing": TagProfile(
        pace="slow",
        pitch="rough and raspy",
        ssml_rate="-10%",
        ssml_pitch="-5Hz",
        ssml_volume="+0%",
        parler_tone="a raspy, strained tone with a slight coughing rasp",
        extra_pause_sec=0.35
    ),
    "chuckling": TagProfile(
        pace="moderate",
        pitch="warm and bouncy",
        ssml_rate="+8%",
        ssml_pitch="+8Hz",
        ssml_volume="+0%",
        parler_tone="a warm, amused tone laced with subtle chuckling"
    ),
    "sighing": TagProfile(
        pace="slow and breathy",
        pitch="low and mellow",
        ssml_rate="-15%",
        ssml_pitch="-6Hz",
        ssml_volume="-5%",
        parler_tone="a breathy, resigned tone accompanied by a heavy sigh",
        extra_pause_sec=0.40
    ),
    "sniffling": TagProfile(
        pace="slow and tremulous",
        pitch="faint and sorrowful",
        ssml_rate="-12%",
        ssml_pitch="-3Hz",
        ssml_volume="-10%",
        parler_tone="a tearful, sniffling tone filled with subdued sorrow",
        extra_pause_sec=0.30
    ),
    "yawning": TagProfile(
        pace="very slow and drawled",
        pitch="sluggish and low",
        ssml_rate="-22%",
        ssml_pitch="-8Hz",
        ssml_volume="-10%",
        parler_tone="a sleepy, drawn-out tone with a heavy, drowsy yawn",
        extra_pause_sec=0.40
    ),
    "laughing": TagProfile(
        pace="lively and upbeat",
        pitch="high and joyous",
        ssml_rate="+14%",
        ssml_pitch="+12Hz",
        ssml_volume="+8%",
        parler_tone="a laughing, cheerful tone bubbling with genuine mirth"
    ),
    "sharp exhale": TagProfile(
        pace="brisk",
        pitch="sharp and curt",
        ssml_rate="+10%",
        ssml_pitch="+4Hz",
        ssml_volume="+5%",
        parler_tone="a curt, exasperated tone with a sharp exhale",
        extra_pause_sec=0.25
    ),
    "scoffing": TagProfile(
        pace="brisk and biting",
        pitch="dry and dismissive",
        ssml_rate="+8%",
        ssml_pitch="+6Hz",
        ssml_volume="+5%",
        parler_tone="a dismissive, scoffing tone dripping with scorn"
    ),
    "humming": TagProfile(
        pace="gentle and steady",
        pitch="mellow and musical",
        ssml_rate="-5%",
        ssml_pitch="+4Hz",
        ssml_volume="-5%",
        parler_tone="a relaxed, musical, and contemplative humming tone"
    ),
    "panting": TagProfile(
        pace="rapid and breathless",
        pitch="tense and urgent",
        ssml_rate="+20%",
        ssml_pitch="+8Hz",
        ssml_volume="+5%",
        parler_tone="a breathless, panting tone full of urgent exertion"
    ),
    "gasping": TagProfile(
        pace="sudden and breathless",
        pitch="high and astonished",
        ssml_rate="+15%",
        ssml_pitch="+14Hz",
        ssml_volume="+10%",
        parler_tone="a startled, breathless, and gasping tone of sudden shock"
    ),

    # --- Delivery Styles ---
    "whispering": TagProfile(
        pace="slow and hushed",
        pitch="low and breathy",
        ssml_rate="-14%",
        ssml_pitch="-10Hz",
        ssml_volume="-25%",
        parler_tone="a hushed, whispery tone as if speaking in strict confidence"
    ),
    "singing": TagProfile(
        pace="rhythmic and melodic",
        pitch="melodic and resonant",
        ssml_rate="+5%",
        ssml_pitch="+12Hz",
        ssml_volume="+5%",
        parler_tone="a lyrical, melodic, and musical sing-song cadence"
    ),
    "slowly": TagProfile(
        pace="slow and deliberate",
        pitch="measured and calm",
        ssml_rate="-25%",
        ssml_pitch="-3Hz",
        ssml_volume="+0%",
        parler_tone="a slow, measured, and deliberate pace"
    ),
    "softly": TagProfile(
        pace="gentle and gentle",
        pitch="soft and mellow",
        ssml_rate="-10%",
        ssml_pitch="-4Hz",
        ssml_volume="-15%",
        parler_tone="a soft, soothing, and tender tone"
    ),
    "pause": TagProfile(
        pace="moderate",
        pitch="balanced",
        ssml_rate="+0%",
        ssml_pitch="+0Hz",
        ssml_volume="+0%",
        parler_tone="a thoughtful, measured pause",
        extra_pause_sec=0.85,
        has_pause=True
    ),
    "voice breaking": TagProfile(
        pace="slow and tremulous",
        pitch="quavering and emotional",
        ssml_rate="-15%",
        ssml_pitch="+6Hz",
        ssml_volume="-5%",
        parler_tone="an intensely emotional, trembling tone with a breaking voice"
    ),

    # --- Character Voice ---
    "sleepy drowsy voice": TagProfile(
        pace="very slow and sluggish",
        pitch="low, heavy, and languid",
        ssml_rate="-24%",
        ssml_pitch="-8Hz",
        ssml_volume="-15%",
        parler_tone="a deeply sleepy, languid, and drowsy voice heavy with slumber"
    ),
}


class TagMapper:
    """Resolves extracted tags into concrete prosody profiles."""

    @classmethod
    def get_profile(cls, tag_name: str) -> Optional[TagProfile]:
        """Looks up a tag by its normalized name."""
        return TAG_DEFINITIONS.get(tag_name.strip().lower())

    @classmethod
    def resolve_tags(cls, tags: List[str]) -> Optional[TagProfile]:
        """
        Combines multiple tags into a unified profile.
        If no tag is recognized, returns None.
        """
        if not tags:
            return None

        matched_profiles = []
        for t in tags:
            p = cls.get_profile(t)
            if p:
                matched_profiles.append(p)

        if not matched_profiles:
            return None

        # If only one tag, return directly
        if len(matched_profiles) == 1:
            return matched_profiles[0]

        # Merge multiple tags: primary tag takes precedence, with combined pauses
        primary = matched_profiles[0]
        extra_pause = sum(p.extra_pause_sec for p in matched_profiles)
        has_pause = any(p.has_pause for p in matched_profiles)
        combined_tones = ", ".join(p.parler_tone for p in matched_profiles)

        return TagProfile(
            pace=primary.pace,
            pitch=primary.pitch,
            ssml_rate=primary.ssml_rate,
            ssml_pitch=primary.ssml_pitch,
            ssml_volume=primary.ssml_volume,
            parler_tone=combined_tones,
            extra_pause_sec=extra_pause,
            has_pause=has_pause
        )
