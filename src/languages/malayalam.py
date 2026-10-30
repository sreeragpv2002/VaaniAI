"""
src/languages/malayalam.py - Malayalam language processor.
"""

from dataclasses import dataclass
from typing import List, Optional

from config.malayalam_config import (
    MALAYALAM_ABBREVIATIONS,
    PAUSE_TIMINGS,
    PARLER_TTS_SPEAKERS,
    PARLER_PROMPT_TEMPLATE,
    DEFAULT_GENDER,
)
from src.text_processing.sentence_splitter import SentenceSplitter
from src.text_processing.text_normalizer import TextNormalizer
from src.text_processing.punctuation_handler import PunctuationHandler
from src.emotion.tag_mapper import TagMapper, TagProfile
from src.emotion.emotion_analyzer import EmotionAnalyzer
from src.emotion.context_analyzer import ContextAnalyzer
from .english import ProcessedSegment


class MalayalamLanguageProcessor:
    """Processes Malayalam text with contextual prosody, Malayalam script handling, and tag extraction."""

    def __init__(
        self,
        gender: str = DEFAULT_GENDER,
        base_speed: str = "moderate",
        expressiveness: str = "moderate",
        pause_scale: float = 1.0,
    ):
        self.gender = gender.lower()
        self.base_speaker = PARLER_TTS_SPEAKERS.get(self.gender, "Anjali")
        self.base_speed = base_speed
        self.expressiveness = expressiveness
        self.pause_scale = pause_scale

        self.splitter = SentenceSplitter(MALAYALAM_ABBREVIATIONS)
        self.punct_handler = PunctuationHandler(PAUSE_TIMINGS, pause_scale)
        self.emotion_analyzer = EmotionAnalyzer("ml")
        self.context_analyzer = ContextAnalyzer(base_speed, expressiveness)

    def process_text(self, text: str) -> List[ProcessedSegment]:
        """Splits text, extracts tags, analyzes context, and builds conditioning prompts."""
        raw_sentences = self.splitter.split_sentences(text)
        segments: List[ProcessedSegment] = []

        for idx, raw_sent in enumerate(raw_sentences):
            # 1. Extract and strip any bracketed emotion/delivery tags from spoken text
            spoken_text, extracted_tags = TextNormalizer.extract_and_strip_tags(raw_sent)
            if not spoken_text:
                continue

            # 2. Resolve tags if any are present
            tag_profile = TagMapper.resolve_tags(extracted_tags) if extracted_tags else None

            # 3. Detect emotion semantics if no tag profile overrides
            if tag_profile is not None:
                emotion = extracted_tags[0]
                confidence = 1.0
            else:
                detected_em, conf = self.emotion_analyzer.analyze_sentence(spoken_text)
                emotion, confidence = self.context_analyzer.smooth_emotion(
                    detected_em, conf, spoken_text
                )

            # 4. Punctuation and dialogue flags
            punct = self.punct_handler.identify_punctuation(spoken_text)
            is_dialogue = self.punct_handler.is_dialogue_segment(spoken_text)
            is_clause = self.punct_handler.is_clause_continuation(spoken_text)

            # 5. Derive prosody parameters
            pace, pitch, ssml_rate, ssml_pitch, ssml_volume = self.context_analyzer.derive_prosody(
                emotion=emotion,
                punctuation=punct,
                tag_profile=tag_profile,
            )

            # 6. Calculate pause duration
            has_pause_tag = tag_profile.has_pause if tag_profile else False
            extra_pause = tag_profile.extra_pause_sec if tag_profile else 0.0
            pause_sec = self.punct_handler.calculate_pause(
                punct=punct,
                is_clause=is_clause,
                has_pause_tag=has_pause_tag,
                extra_pause_sec=extra_pause,
            )

            # 7. Build Parler-TTS prompt maintaining the exact same base speaker
            parler_prompt = self._build_parler_prompt(
                speaker=self.base_speaker,
                pace=pace,
                pitch=pitch,
                emotion=emotion,
                is_dialogue=is_dialogue,
                tag_profile=tag_profile,
            )

            # 8. Build SSML markup fragment for Edge-TTS
            ssml_markup = self._build_ssml(
                clean_text=spoken_text,
                rate=ssml_rate,
                pitch=ssml_pitch,
                volume=ssml_volume,
                pause_sec=pause_sec,
            )

            segment = ProcessedSegment(
                index=idx + 1,
                original_text=raw_sent,
                spoken_text=spoken_text,
                tags=extracted_tags,
                punctuation=punct,
                is_dialogue=is_dialogue,
                is_clause=is_clause,
                emotion=emotion,
                confidence=confidence,
                pace=pace,
                pitch=pitch,
                ssml_rate=ssml_rate,
                ssml_pitch=ssml_pitch,
                ssml_volume=ssml_volume,
                pause_after_sec=pause_sec,
                parler_description=parler_prompt,
                ssml_markup=ssml_markup,
            )
            segments.append(segment)

        return segments

    def _build_parler_prompt(
        self,
        speaker: str,
        pace: str,
        pitch: str,
        emotion: str,
        is_dialogue: bool,
        tag_profile: Optional[TagProfile] = None,
    ) -> str:
        """Constructs conditioning prompt ensuring the speaker identity never changes."""
        if tag_profile is not None and tag_profile.parler_tone:
            tone_desc = tag_profile.parler_tone
        else:
            tone_map = {
                "happy": "a cheerful, joyful tone full of warmth and enthusiasm",
                "sad": "a sombre, melancholic tone with quiet sadness",
                "fear": "a tense, fearful tone conveying anxiety and alarm",
                "anger": "a stern, forceful tone with commanding anger",
                "surprise": "an astonished, wide-eyed tone filled with wonder",
                "suspense": "a mysterious, hushed tone with deliberate dramatic suspense",
                "curiosity": "an inquisitive, thoughtful tone",
                "warmth": "a gentle, tender tone brimming with kindness",
                "neutral": "a clear, natural narrative tone",
            }
            tone_desc = tone_map.get(emotion, "a clear, natural narrative tone")

        delivery = (
            "delivering conversational Malayalam dialogue with authentic Kerala cadence as spoken by people in Kerala"
            if is_dialogue
            else "delivering traditional Malayalam storytelling with authentic Kerala pronunciation, natural cadence, and melodic intonation"
        )

        return PARLER_PROMPT_TEMPLATE.format(
            speaker=speaker,
            pace=pace,
            tone=tone_desc,
            pitch=pitch,
            delivery=delivery,
        )

    def _build_ssml(
        self,
        clean_text: str,
        rate: str,
        pitch: str,
        volume: str,
        pause_sec: float,
    ) -> str:
        """Constructs an SSML fragment tuned for natural Kerala speech rhythm."""
        # In Malayalam, speaking with a relaxed cadence (-6%) prevents robotic rushing
        # and preserves natural Kerala geminate consonants (കൂട്ടക്ഷരങ്ങൾ)
        if rate == "+0%":
            rate = "-6%"
        elif rate.startswith("+"):
            val = int(rate.replace("+", "").replace("%", ""))
            rate = f"+{max(0, val - 6)}%"

        break_ms = int(pause_sec * 1000)
        return (
            f'<prosody rate="{rate}" pitch="{pitch}" volume="{volume}">{clean_text}</prosody>'
            f'<break time="{break_ms}ms"/>'
        )
