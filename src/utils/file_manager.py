"""
src/utils/file_manager.py - File resolution and path utilities.
"""

from pathlib import Path
from typing import Optional, Tuple
import re

from config.settings import (
    INPUT_ENGLISH_DIR,
    INPUT_MALAYALAM_DIR,
    OUTPUT_ENGLISH_DIR,
    OUTPUT_MALAYALAM_DIR,
)


class FileManager:
    """Manages file locations, auto-detects language, and ensures directory validity."""

    @staticmethod
    def read_text(file_path: str) -> str:
        """Reads text from file path with utf-8 encoding."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")
        return path.read_text(encoding="utf-8")

    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detects if text is primarily Malayalam (Unicode range 0D00-0D7F) or English.
        Returns: 'ml' or 'en'
        """
        malayalam_chars = len(re.findall(r'[\u0D00-\u0D7F]', text))
        if malayalam_chars > 10:
            return "ml"
        return "en"

    @staticmethod
    def resolve_output_path(
        output_arg: Optional[str],
        lang: str,
        default_name: str = "narration.wav",
    ) -> Path:
        """Resolves target output path in appropriate language-specific directory."""
        target_dir = OUTPUT_MALAYALAM_DIR if lang == "ml" else OUTPUT_ENGLISH_DIR
        target_dir.mkdir(parents=True, exist_ok=True)

        if output_arg:
            path = Path(output_arg)
            if not path.is_absolute() and len(path.parts) == 1:
                return target_dir / path.name
            path.parent.mkdir(parents=True, exist_ok=True)
            return path

        return target_dir / default_name
