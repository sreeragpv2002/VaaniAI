"""
config/malayalam_config.py - Malayalam voice and language configuration.
Optimized for authentic native Kerala speech style, natural intonation, and expressive narration.
"""

# Voice Definitions (Ensures One Consistent Base Voice throughout the narration)
EDGE_TTS_VOICES = {
    # ml-IN-SobhanaNeural: Highly recommended for natural, authentic Kerala storytelling
    "female": "ml-IN-SobhanaNeural",
    # ml-IN-MidhunNeural: Male voice, tuned with -8% rate for natural Kerala cadence
    "male": "ml-IN-MidhunNeural",
}

PARLER_TTS_SPEAKERS = {
    # Anjali: Native Malayalam voice trained by AI4Bharat on IIT Madras Kerala corpus
    "female": "Anjali",
    "female_alt": "Anju",
    # Harish: Malayalam male voice
    "male": "Harish",
}

# Sobhana/Anjali is the primary authentic Kerala storytelling voice
DEFAULT_GENDER = "female"

# Common Malayalam Abbreviations that should NOT trigger sentence splitting
MALAYALAM_ABBREVIATIONS = {
    "ഡോ.", "ശ്രീ.", "ശ്രീമതി.", "പ്രൊഫ.", "റവ.", "മു.", "കി.മീ.", "സെ.മീ."
}

# Base Pause Timings in seconds (tuned for natural Kerala breath cadence)
PAUSE_TIMINGS = {
    "period": 0.38,
    "comma": 0.22,
    "semicolon": 0.30,
    "colon": 0.30,
    "question": 0.48,
    "exclamation": 0.48,
    "ellipsis": 0.90,
    "paragraph": 0.70,
}

# Parler Prompt Base Template for authentic Kerala accent
PARLER_PROMPT_TEMPLATE = (
    "{speaker}, a native Malayalam speaker from Kerala, delivers natural and expressive "
    "Malayalam speech in an authentic Kerala accent and melodic intonation at a {pace} pace in "
    "{tone} with a {pitch} pitch, {delivery}. The recording is of pristine studio quality with "
    "crystal clear audio, warm room acoustics, and zero background noise."
)
