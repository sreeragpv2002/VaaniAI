"""
main.py - Unified Expressive TTS Narration System for English & Malayalam.

Key Features:
1. One Consistent Base Voice throughout the narration (no voice switching).
2. Support for emotion, delivery, vocalization, and character tags ([angry], [whispering], etc.).
3. Tags are never spoken aloud; they are parsed and mapped to prosody/conditioning prompts.
4. Native support for both Indian English and Malayalam.
5. Dual engine architecture: 'edge-tts' (high-speed CPU) and 'indic-parler' (local offline).
6. Automatic sentence-level emotion, punctuation, and context analysis.
7. Anti-click boundary fading, punctuation pauses, and loudness normalization.
"""

import sys
import argparse
from pathlib import Path
from typing import List, Tuple
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.logger import setup_logger, log_segment
from src.utils.file_manager import FileManager
from src.languages.english import EnglishLanguageProcessor, ProcessedSegment
from src.languages.malayalam import MalayalamLanguageProcessor
from src.audio.tts_engine import create_tts_engine
from src.audio.audio_merger import AudioMerger
from src.audio.voice_cloner import VoiceCloner
from config.settings import DEFAULT_ENGINE, DEFAULT_PAUSE_SCALE


def run_preview(segments: List[ProcessedSegment], lang: str, voice: str, engine_type: str):
    """Prints the sentence-by-sentence emotion, tag, and prosody breakdown."""
    print("\n" + "=" * 90)
    print(f"SENTENCE-LEVEL NLP PREVIEW ({lang.upper()}, BASE VOICE: {voice.upper()}, ENGINE: {engine_type.upper()})")
    print("=" * 90)

    for seg in segments:
        log_segment(seg, len(segments), engine_type=engine_type)

    print("\n" + "=" * 90)
    print(f"TOTAL SEGMENTS: {len(segments)}")
    print("=" * 90 + "\n")


def synthesize_narration(
    text: str,
    lang: str = "en",
    voice: str = "male",
    engine_type: str = "edge-tts",
    speed: str = "moderate",
    expressiveness: str = "moderate",
    pause_scale: float = DEFAULT_PAUSE_SCALE,
    output_path: str = None,
    preview_only: bool = False,
    device: str = None,
    clone_voice: str = None,
) -> str:
    """End-to-end pipeline orchestrating text analysis, emotion detection, TTS, and audio merging."""
    setup_logger()

    # 1. Select Language Processor
    if lang == "ml":
        processor = MalayalamLanguageProcessor(
            gender=voice,
            base_speed=speed,
            expressiveness=expressiveness,
            pause_scale=pause_scale,
        )
    else:
        processor = EnglishLanguageProcessor(
            gender=voice,
            base_speed=speed,
            expressiveness=expressiveness,
            pause_scale=pause_scale,
        )

    # 2. Analyze Text into Segments
    segments = processor.process_text(text)
    if not segments:
        print("Warning: No speech segments found in the input text.")
        return ""

    # 3. Preview Mode
    if preview_only:
        run_preview(segments, lang, voice, engine_type)
        return ""

    # 4. Resolve Output Path
    default_name = f"{'malayalam' if lang == 'ml' else 'english'}_{voice}_narration.wav"
    final_output_path = FileManager.resolve_output_path(output_path, lang, default_name)

    print("\n" + "=" * 80)
    print("STARTING EXPRESSIVE TTS SYNTHESIS")
    print(f"Language:       {lang.upper()}")
    print(f"Base Voice:     {voice.upper()} (Maintained consistently throughout narration)")
    print(f"TTS Engine:     {engine_type.upper()}")
    print(f"Pace / Style:   Speed: {speed} | Expressiveness: {expressiveness} | Pause Scale: {pause_scale}x")
    print(f"Output File:    {final_output_path}")
    print("=" * 80 + "\n")

    # 5. Initialize Engine with Consistent Voice
    tts_engine = create_tts_engine(
        engine_type=engine_type,
        lang=lang,
        gender=voice,
        device=device,
    )

    audio_segments_with_pauses: List[Tuple[np.ndarray, float]] = []

    # 6. Synthesize Each Segment
    for seg in segments:
        log_segment(seg, len(segments), engine_type=engine_type)
        audio_chunk = tts_engine.synthesize_segment(seg)
        audio_segments_with_pauses.append((audio_chunk, seg.pause_after_sec))

    # 7. Stitch Audio Segments with Punctuation Pauses and Volume Normalization
    print(f"\n[Audio] Stitching {len(audio_segments_with_pauses)} segments with anti-click fading...")
    final_audio = AudioMerger.merge_segments(
        segments_with_pauses=audio_segments_with_pauses,
        sample_rate=tts_engine.sample_rate,
        fade_ms=12.0,
        normalize=True,
    )

    # 8. Export WAV File
    exported_file = AudioMerger.export_wav(str(final_output_path), final_audio, tts_engine.sample_rate)
    duration_sec = len(final_audio) / tts_engine.sample_rate

    print("\n" + "=" * 80)
    print(f"[Done] Synthesized {duration_sec:.1f}s of expressive {lang.upper()} narration!")
    print(f"[Done] Audio saved to: {exported_file}")
    print("=" * 80 + "\n")

    # 9. Optional Voice Cloning (Tone Color Conversion)
    if clone_voice:
        try:
            cloned_file = VoiceCloner.clone(
                input_audio_path=exported_file,
                ref_audio_path=clone_voice,
                device=device or "cpu",
            )
            return cloned_file
        except Exception as e:
            print(f"[VoiceCloner] Notice: {e}")
            print(f"[VoiceCloner] Base narration remains available at: {exported_file}")

    return exported_file


def prompt_voice_selection(lang: str) -> str:
    """Interactively prompts the user at runtime to choose between Female (1) and Male (2)."""
    lang_name = "Malayalam" if lang == "ml" else "English"
    female_info = "Sobhana / Anjali (Authentic Kerala storytelling style)" if lang == "ml" else "Neerja / Mary (Clear Indian English)"
    male_info = "Midhun / Harish" if lang == "ml" else "Prabhat / Thoma (Indian English)"
    default_choice = "1"

    # If running non-interactively (e.g. redirected or automated test), return default
    if not sys.stdin.isatty():
        return "female" if default_choice == "1" else "male"

    print("\n" + "=" * 65)
    print(f" SELECT NARRATOR VOICE FOR {lang_name.upper()}")
    print("=" * 65)
    print(f"  [1] Female Voice - {female_info}")
    print(f"  [2] Male Voice   - {male_info}")
    print("-" * 65)

    while True:
        try:
            choice = input(f"Enter choice [1 for Female, 2 for Male] (Default: {default_choice}): ").strip()
            if choice == "" or choice == default_choice:
                selected = "female"
                print(f"-> Selected: FEMALE\n")
                return selected
            elif choice == "1" or choice.lower().startswith("f"):
                print("-> Selected: FEMALE\n")
                return "female"
            elif choice == "2" or choice.lower().startswith("m"):
                print("-> Selected: MALE\n")
                return "male"
            else:
                print("Invalid choice. Please type 1 (Female) or 2 (Male).")
        except (KeyboardInterrupt, EOFError):
            print("\nDefaulting to Female voice.")
            return "female"


def main():
    parser = argparse.ArgumentParser(
        description="Unified Expressive TTS Narration System for English & Malayalam."
    )
    parser.add_argument(
        "--file", "-f", type=str, default=None,
        help="Path to input text file (English or Malayalam)"
    )
    parser.add_argument(
        "--text", "-t", type=str, default=None,
        help="Direct text string to synthesize (overrides --file)"
    )
    parser.add_argument(
        "--lang", "-l", type=str, default=None, choices=["en", "ml"],
        help="Language: 'en' (English) or 'ml' (Malayalam). Auto-detected if omitted."
    )
    parser.add_argument(
        "--voice", "-v", type=str, default=None, choices=["1", "2", "male", "female"],
        help="Base voice identity: '1' or 'female', '2' or 'male' (Prompts at runtime if omitted)"
    )
    parser.add_argument(
        "--engine", type=str, default="edge-tts", choices=["edge-tts", "indic-parler"],
        help="TTS engine: 'edge-tts' (fast CPU) or 'indic-parler' (local offline)"
    )
    parser.add_argument(
        "--speed", type=str, default="moderate",
        choices=["slow", "moderate", "brisk", "fast"],
        help="Base narration reading pace (default: moderate)"
    )
    parser.add_argument(
        "--expressiveness", type=str, default="moderate",
        choices=["subtle", "moderate", "dramatic"],
        help="Level of emotional variation and intensity (default: moderate)"
    )
    parser.add_argument(
        "--pause-scale", type=float, default=1.0,
        help="Multiplier for punctuation pauses (default: 1.0)"
    )
    parser.add_argument(
        "--output", "-o", type=str, default=None,
        help="Path to output WAV file (auto-routed to output/en or output/ml if omitted)"
    )
    parser.add_argument(
        "--preview", action="store_true",
        help="Preview sentence segmentation, emotion tags, and prosody without synthesizing audio"
    )
    parser.add_argument(
        "--device", type=str, default=None,
        help="Device for local PyTorch models ('cuda:0' or 'cpu')"
    )
    parser.add_argument(
        "--clone-voice", "-c", type=str, default=None,
        help="Path to reference voice audio clip (e.g. input/actress.wav) to clone voice timbre"
    )

    args = parser.parse_args()

    # Determine input text
    if args.text:
        input_text = args.text
    elif args.file:
        input_text = FileManager.read_text(args.file)
    else:
        # Default to english story if available
        default_file = PROJECT_ROOT / "input" / "english" / "english_story.txt"
        if not default_file.exists():
            default_file = PROJECT_ROOT / "english_story.txt"
        if default_file.exists():
            input_text = FileManager.read_text(str(default_file))
        else:
            print("Error: Please provide --file or --text.")
            sys.exit(1)

    # Auto-detect language if not provided
    lang = args.lang or FileManager.detect_language(input_text)

    # Runtime Voice Selection: Map CLI input (1/2/male/female) or prompt interactively
    if args.voice in ("1", "female"):
        voice = "female"
    elif args.voice in ("2", "male"):
        voice = "male"
    elif args.preview:
        # For non-interactive preview, default to female for Malayalam, male for English
        voice = "female" if lang == "ml" else "male"
    else:
        # Prompt interactively at runtime: 1 for Female, 2 for Male
        voice = prompt_voice_selection(lang)

    synthesize_narration(
        text=input_text,
        lang=lang,
        voice=voice,
        engine_type=args.engine,
        speed=args.speed,
        expressiveness=args.expressiveness,
        pause_scale=args.pause_scale,
        output_path=args.output,
        preview_only=args.preview,
        device=args.device,
        clone_voice=args.clone_voice,
    )


if __name__ == "__main__":
    main()
