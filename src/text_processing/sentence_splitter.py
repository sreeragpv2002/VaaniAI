"""
src/text_processing/sentence_splitter.py - Robust paragraph and sentence boundary segmentation.
"""

import re
from typing import List, Set
from .text_normalizer import TextNormalizer


class SentenceSplitter:
    """Splits raw text into paragraph-aware and sentence-aware chunks."""

    def __init__(self, abbreviations: Set[str], max_clause_len: int = 150):
        self.abbreviations = abbreviations
        self.max_clause_len = max_clause_len

    def split_paragraphs(self, text: str) -> List[str]:
        """Separates text into distinct paragraphs divided by double newlines."""
        normalized = TextNormalizer.normalize_unicode(text)
        paragraphs = [p.strip() for p in normalized.split("\n\n") if p.strip()]
        return paragraphs

    def split_sentences(self, text: str) -> List[str]:
        """Splits full text into individual sentence chunks while preserving dialogue attributions."""
        paragraphs = self.split_paragraphs(text)
        all_sentences: List[str] = []

        for para in paragraphs:
            para_sentences = self._split_single_paragraph(para)
            all_sentences.extend(para_sentences)

        return all_sentences

    def _split_single_paragraph(self, para: str) -> List[str]:
        """Splits an individual paragraph into sentence segments."""
        cleaned = TextNormalizer.clean_paragraph_whitespace(para)
        if not cleaned:
            return []

        # 1. Protect ellipsis (...)
        protected = re.sub(r'\.{3,}', '__ELLIPSIS__', cleaned)

        # 2. Protect numbers with decimals (e.g. 10.30, 3.14)
        protected = re.sub(r'(\d+)\.(\d+)', r'\1__DECDOT__\2', protected)

        # 3. Protect common abbreviations (case-insensitive)
        for abbr in self.abbreviations:
            pattern = re.compile(re.escape(abbr), re.IGNORECASE)
            def repl(m):
                return m.group(0).replace(".", "__DOT__")
            protected = pattern.sub(repl, protected)

        # 4. Protect single-letter initials like 'A. B. Patel'
        protected = re.sub(r'\b([A-Z])\.\s+(?=[A-Z]\b)', r'\1__INITDOT__ ', protected)

        # 5. Protect dialogue quote closures followed by dialogue attribution tags
        def protect_dialogue(m):
            return m.group(0).replace("!", "__EXCL__").replace("?", "__QMARK__")

        dialogue_pattern = (
            r'([\"\'‘][^\"\'’]*?[!?][\"\'’])(\s+[a-zA-Z\u0D00-\u0D7F]+'
            r'(?:\s+[a-zA-Z\u0D00-\u0D7F]+){0,4}\s*'
            r'(?:said|asked|shouted|whispered|screamed|cried|replied|demanded|gasped|growled|snapped|murmured|sighed|laughed|yelled|roared|ചിരിച്ചു|ചോദിച്ചു|പറഞ്ഞു|നിലവിളിച്ചു|ഓർത്തു|മൊഴിഞ്ഞു|മറുപടി നൽകി|നൽകി|വ്യക്തമാക്കി|വിളിച്ചു))'
        )
        protected = re.sub(dialogue_pattern, protect_dialogue, protected, flags=re.IGNORECASE)

        # 6. Sentence splitting on punctuation (. ! ?) followed by optional quote and whitespace
        sentence_pattern = r'([.!?]["\'’]?)\s+(?=[A-Z0-9"\'‘\[\u0D00-\u0D7F])'
        marked = re.sub(sentence_pattern, r'\1__SENT_SPLIT__', protected)
        raw_parts = marked.split('__SENT_SPLIT__')

        sentences = []
        for part in raw_parts:
            # Restore protected tokens
            s = part.replace("__DOT__", ".") \
                    .replace("__DECDOT__", ".") \
                    .replace("__INITDOT__", ". ") \
                    .replace("__EXCL__", "!") \
                    .replace("__QMARK__", "?") \
                    .replace("__ELLIPSIS__", "...") \
                    .strip()
            if s:
                sentences.append(s)

        # 7. Sub-split very long sentences (> max_clause_len) at natural clause boundaries
        final_segments = []
        for s in sentences:
            if len(s) > self.max_clause_len:
                clauses = self._split_long_clause(s)
                final_segments.extend(clauses)
            else:
                final_segments.append(s)

        return final_segments

    def _split_long_clause(self, sentence: str) -> List[str]:
        """Sub-splits a long sentence at natural clause boundaries (commas, semicolons)."""
        parts = re.split(r'(?<=[,;:\-])\s+', sentence)
        result = []
        curr = ""
        for p in parts:
            if not curr:
                curr = p
            elif len(curr) + len(p) + 1 <= self.max_clause_len:
                curr += " " + p
            else:
                result.append(curr.strip())
                curr = p
        if curr:
            result.append(curr.strip())
        return result
