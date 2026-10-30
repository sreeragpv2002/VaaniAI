"""
src/audio/tts_engine.py - Unified TTS engine interface for Edge-TTS and Indic-Parler-TTS.

Ensures strict consistency of base voice identity across all synthesized segments.
"""

from abc import ABC, abstractmethod
from typing import Optional
import asyncio
import subprocess
import numpy as np

from config.english_config import EDGE_TTS_VOICES as EN_EDGE_VOICES
from config.malayalam_config import EDGE_TTS_VOICES as ML_EDGE_VOICES
from src.languages.english import ProcessedSegment


class BaseTTSEngine(ABC):
    """Abstract base class for speech synthesis engines."""

    @abstractmethod
    def synthesize_segment(self, segment: ProcessedSegment) -> np.ndarray:
        """Synthesizes raw audio waveform for a single sentence segment."""
        pass


class EdgeTTSEngine(BaseTTSEngine):
    """
    High-speed neural speech synthesis using Microsoft Edge voices.
    Maintains one consistent base voice while varying prosody.
    """

    def __init__(self, voice_name: str):
        self.voice_name = voice_name
        self.sample_rate = 24000
        try:
            import edge_tts
            self._edge_tts = edge_tts
        except ImportError:
            raise RuntimeError(
                "edge-tts is not installed. Install it via: pip install edge-tts"
            )

    async def _synthesize_async(self, segment: ProcessedSegment) -> np.ndarray:
        communicate = self._edge_tts.Communicate(
            text=segment.spoken_text,
            voice=self.voice_name,
            rate=segment.ssml_rate,
            pitch=segment.ssml_pitch,
            volume=segment.ssml_volume,
        )
        mp3_bytes = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                mp3_bytes.extend(chunk["data"])

        if not mp3_bytes:
            return np.zeros(int(self.sample_rate * 0.1), dtype=np.float32)

        return self._decode_mp3(mp3_bytes)

    def _decode_mp3(self, mp3_bytes: bytes) -> np.ndarray:
        import imageio_ffmpeg

        try:
            result = subprocess.run(
                [imageio_ffmpeg.get_ffmpeg_exe(), "-i", "pipe:0", "-f", "f32le",
                 "-acodec", "pcm_f32le", "-ac", "1", "-ar", str(self.sample_rate), "pipe:1"],
                input=mp3_bytes,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            detail = exc.stderr.decode(errors="replace").strip()
            raise RuntimeError(f"Failed to decode Edge TTS MP3: {detail}") from exc
        return np.frombuffer(result.stdout, dtype="<f4").copy()

    def synthesize_segment(self, segment: ProcessedSegment) -> np.ndarray:
        return asyncio.run(self._synthesize_async(segment))


class IndicParlerTTSEngine(BaseTTSEngine):
    """
    Local neural speech synthesis using AI4Bharat Indic-Parler-TTS.
    Maintains one consistent base voice while dynamically varying natural language descriptions.
    """

    DEFAULT_MODEL_ID = "ai4bharat/indic-parler-tts"

    def __init__(
        self,
        model_id: str = DEFAULT_MODEL_ID,
        device: Optional[str] = None,
    ):
        import torch

        self.device = device or ("cuda:0" if torch.cuda.is_available() else "cpu")
        self._torch = torch
        from parler_tts import ParlerTTSForConditionalGeneration
        from transformers import AutoTokenizer

        self.model = ParlerTTSForConditionalGeneration.from_pretrained(model_id).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.description_tokenizer = AutoTokenizer.from_pretrained(
            self.model.config.text_encoder._name_or_path
        )
        self.sample_rate = self.model.config.sampling_rate
        self._desc_cache = {}

    def _get_description_inputs(self, description: str):
        if description not in self._desc_cache:
            desc_inputs = self.description_tokenizer(
                description, return_tensors="pt"
            ).to(self.device)
            self._desc_cache[description] = desc_inputs
        return self._desc_cache[description]

    def synthesize_segment(self, segment: ProcessedSegment) -> np.ndarray:
        desc_inputs = self._get_description_inputs(segment.parler_description)
        text_inputs = self.tokenizer(segment.spoken_text, return_tensors="pt").to(self.device)

        with self._torch.inference_mode():
            output = self.model.generate(
                input_ids=desc_inputs.input_ids,
                attention_mask=desc_inputs.attention_mask,
                prompt_input_ids=text_inputs.input_ids,
                prompt_attention_mask=text_inputs.attention_mask,
            )

        audio_arr = output.cpu().numpy().squeeze().astype(np.float32)
        return audio_arr


def create_tts_engine(
    engine_type: str = "edge-tts",
    lang: str = "en",
    gender: str = "male",
    device: Optional[str] = None,
) -> BaseTTSEngine:
    """
    Factory function ensuring a single consistent base voice is selected and locked in
    based on the engine, language, and gender.
    """
    engine_type = engine_type.lower()
    gender = gender.lower()

    if engine_type == "edge-tts":
        if lang == "ml":
            voice = ML_EDGE_VOICES.get(gender, ML_EDGE_VOICES["male"])
        else:
            voice = EN_EDGE_VOICES.get(gender, EN_EDGE_VOICES["male"])
        return EdgeTTSEngine(voice_name=voice)

    elif engine_type in ("indic-parler", "parler"):
        return IndicParlerTTSEngine(device=device)

    else:
        raise ValueError(
            f"Unsupported engine type: '{engine_type}'. Choose 'edge-tts' or 'indic-parler'."
        )
