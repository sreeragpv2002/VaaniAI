"""
src/text_processing/text_normalizer.py - Unicode normalization, whitespace cleanup,
and emotion/vocalization tag extraction.
"""

import re
import unicodedata
from typing import List, Tuple


class TextNormalizer:
    """Normalizes text and strips emotion/vocalization tags so they are not spoken aloud."""

    # Matches any bracketed tag e.g. [angry], [whispering], [clears throat], [sleepy drowsy voice]
    TAG_REGEX = re.compile(r'\[([a-zA-Z0-9\s_\-]+)\]')

    @classmethod
    def normalize_unicode(cls, text: str) -> str:
        """Standardizes Unicode characters to NFC format and harmonizes quotes."""
        if not text:
            return ""
        text = unicodedata.normalize("NFC", text)
        # Standardize curly quotes and dashes
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        text = text.replace("—", " - ").replace("–", " - ")
        return text

    @classmethod
    def clean_paragraph_whitespace(cls, para: str) -> str:
        """Removes single line breaks within paragraphs and fixes stray punctuation spaces."""
        para = re.sub(r'\s*\n\s*', ' ', para)
        para = re.sub(r'\s+([.,!?;:])', r'\1', para)
        para = re.sub(r'\s+', ' ', para)
        return para.strip()

    @classmethod
    def extract_and_strip_tags(cls, sentence: str) -> Tuple[str, List[str]]:
        """
        Detects any explicit emotion/delivery/vocalization tags in the sentence,
        extracts their normalized names, and removes them from the spoken text.

        Example:
            "[whispering] 'Do not move,' she warned."
            -> returns ("'Do not move,' she warned.", ["whispering"])
        """
        tags = []
        for match in cls.TAG_REGEX.finditer(sentence):
            tag_name = match.group(1).strip().lower()
            tags.append(tag_name)

        # Remove the bracketed tags from the spoken text
        cleaned_text = cls.TAG_REGEX.sub('', sentence)
        # Clean any double spaces left behind by tag removal
        cleaned_text = re.sub(r'\s+([.,!?;:])', r'\1', cleaned_text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

        return cleaned_text, tags
