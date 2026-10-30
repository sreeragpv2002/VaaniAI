"""
config/settings.py - Global settings and path definitions for TTS system.
"""

from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"

INPUT_ENGLISH_DIR = INPUT_DIR / "english"
INPUT_MALAYALAM_DIR = INPUT_DIR / "malayalam"
OUTPUT_ENGLISH_DIR = OUTPUT_DIR / "english"
OUTPUT_MALAYALAM_DIR = OUTPUT_DIR / "malayalam"

# Ensure directories exist
for path in [
    INPUT_ENGLISH_DIR,
    INPUT_MALAYALAM_DIR,
    OUTPUT_ENGLISH_DIR,
    OUTPUT_MALAYALAM_DIR,
]:
    path.mkdir(parents=True, exist_ok=True)

# Default Engine & Audio Settings
DEFAULT_ENGINE = "edge-tts"  # 'edge-tts' or 'indic-parler'
DEFAULT_SAMPLE_RATE = 24000
DEFAULT_VOLUME_TARGET_DBFS = -1.5
DEFAULT_FADE_MS = 12.0
DEFAULT_PAUSE_SCALE = 1.0

# Supported Languages
SUPPORTED_LANGUAGES = ["en", "ml"]
DEFAULT_LANGUAGE = "en"
