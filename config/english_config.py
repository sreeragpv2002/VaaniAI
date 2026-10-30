"""
config/english_config.py - Indian English voice and language configuration.
"""

# Voice Definitions (Ensures One Consistent Base Voice throughout the narration)
EDGE_TTS_VOICES = {
    "male": "en-IN-PrabhatNeural",
    "female": "en-IN-NeerjaNeural",
}

PARLER_TTS_SPEAKERS = {
    "male": "Thoma",
    "female": "Mary",
}

DEFAULT_GENDER = "male"

# Common English Abbreviations that should NOT trigger sentence splitting
COMMON_ABBREVIATIONS = {
    "mr.", "mrs.", "ms.", "dr.", "prof.", "sr.", "jr.", "vs.", "etc.",
    "e.g.", "i.e.", "st.", "ave.", "gen.", "gov.", "capt.", "sgt.", "col.",
    "approx.", "dept.", "est.", "min.", "sec.", "no.", "vol.", "rev.",
    "a.m.", "p.m.", "lt."
}

# Base Pause Timings in seconds
PAUSE_TIMINGS = {
    "period": 0.35,
    "comma": 0.20,
    "semicolon": 0.28,
    "colon": 0.28,
    "question": 0.45,
    "exclamation": 0.45,
    "ellipsis": 0.85,
    "paragraph": 0.65,
}

# Parler Prompt Base Template for Indian English
PARLER_PROMPT_TEMPLATE = (
    "{speaker} speaks at a {pace} pace in {tone} with a {pitch} pitch, "
    "{delivery}. The recording is of pristine studio quality with crystal "
    "clear audio, balanced acoustics, and minimal background noise."
)
