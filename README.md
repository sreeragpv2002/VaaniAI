# Expressive Text-to-Speech Narration System (English & Malayalam)

A modular, production-ready Text-to-Speech (TTS) narration system designed for **audiobooks, stories, and long-form reading** in both **English (Indian English style)** and **Malayalam**.

---

## 🌟 Core Architecture & Principles

### 1. Consistent Base Voice (No Voice Switching)
- Throughout an entire chapter or book, the **exact same base voice** is maintained.
- **English:**
  - `male`: `en-IN-PrabhatNeural` (Edge-TTS) / `Thoma` (Indic-Parler)
  - `female`: `en-IN-NeerjaNeural` (Edge-TTS) / `Mary` (Indic-Parler)
- **Malayalam:**
  - `male`: `ml-IN-MidhunNeural` (Edge-TTS) / `Harish` (Indic-Parler)
  - `female`: `ml-IN-SobhanaNeural` (Edge-TTS) / `Anjali` (Indic-Parler)
- Character dialogue and narration are spoken by the **same narrator**, with only pitch, pace, intensity, pauses, and emotional coloring varying naturally according to context.

### 2. Emotion & Vocal Expression Tags
Supports explicit inline tags:
- **Emotion:** `[weak]`, `[angry]`, `[bored]`, `[menacing]`, `[playful]`, `[tired]`, `[excited]`
- **Vocalizations:** `[clears throat]`, `[coughing]`, `[chuckling]`, `[sighing]`, `[sniffling]`, `[yawning]`, `[laughing]`, `[sharp exhale]`, `[scoffing]`, `[humming]`, `[panting]`, `[gasping]`
- **Delivery:** `[whispering]`, `[singing]`, `[slowly]`, `[softly]`, `[pause]`, `[voice breaking]`
- **Character Voice:** `[sleepy drowsy voice]`

> **Important:** Tags are automatically **extracted and stripped** from the spoken text so they are **never spoken aloud**. They are mapped directly into acoustic prosody and conditioning prompts.

### 3. Automatic Context & Sentence Analysis
If no explicit tags are present, the system automatically analyzes:
- Sentence semantics, emotional sentiment, and dialogue attributions (*sighed*, *shouted*, *നിലവിളിച്ചു*, *ചിരിച്ചു*).
- Punctuation-aware pauses:
  - Period (`.`): ~350ms
  - Question (`?`): ~450ms with upward intonation
  - Exclamation (`!`): ~450ms with punchy cadence
  - Ellipsis (`...`): ~850ms dramatic suspense pause
  - Clause / Comma (`,`): ~200ms breathing pause
- Anti-leak smoothing: Prevents intense character anger from spilling into subsequent calm landscape descriptions.

### 4. Audio Quality & Engineering
- **Anti-click Hann Window Tapering:** 12ms cosine fading prevents clicks and phase pops at chunk boundaries.
- **Punctuation-Based Gap Insertion:** Dynamic silence injection between chunks.
- **Volume Normalization:** Peak & RMS normalization to -1.5 dBFS prevents distortion and clipping.

---

## 📁 Project Structure

```text
MalayalamTTS/
├── main.py                  # Primary CLI and orchestration entrypoint
├── requirements.txt         # Dependencies
├── README.md                # System documentation
├── .env.example             # Configuration defaults
│
├── config/
│   ├── settings.py          # Global path and audio settings
│   ├── english_config.py    # English voices, abbreviations, pause timings
│   └── malayalam_config.py  # Malayalam voices, abbreviations, pause timings
│
├── src/
│   ├── text_processing/
│   │   ├── text_normalizer.py     # Tag stripping, Unicode NFC, quote normalization
│   │   ├── punctuation_handler.py # Punctuation classification & pause calculation
│   │   └── sentence_splitter.py   # Paragraph and sentence boundary segmentation
│   │
│   ├── emotion/
│   │   ├── tag_mapper.py          # Registry of emotion/vocalization tags to prosody
│   │   ├── emotion_analyzer.py    # Multilingual emotion lexicons (EN & ML)
│   │   └── context_analyzer.py    # Contextual decay and prosody derivation
│   │
│   ├── languages/
│   │   ├── english.py             # Indian English pipeline coordinator
│   │   └── malayalam.py           # Malayalam pipeline coordinator
│   │
│   ├── audio/
│   │   ├── tts_engine.py          # Edge-TTS and Indic-Parler-TTS engines
│   │   ├── audio_processor.py     # Fade-in/out smoothing and volume normalization
│   │   └── audio_merger.py        # Segment concatenation and WAV export
│   │
│   └── utils/
│       ├── file_manager.py        # Path resolution and language detection
│       └── logger.py              # Formatted terminal progress output
│
├── input/
│   ├── english/                   # English text files (e.g., english_story.txt)
│   └── malayalam/                 # Malayalam text files (e.g., malayalam_story.txt)
│
├── output/
│   ├── english/                   # Exported English audio WAVs
│   └── malayalam/                 # Exported Malayalam audio WAVs
│
└── tests/
    ├── test_emotions.py           # Tag parsing, prosody mapping & tag stripping tests
    ├── test_english.py            # English sentence boundary and consistency tests
    └── test_malayalam.py          # Malayalam script, dialogue and consistency tests
```

---

## 🚀 Quickstart & Usage

### 1. Instant Preview Mode (Inspect tags, emotions, and prosody without waiting)
```powershell
# English Story Preview
.\.venv\Scripts\python.exe main.py --file input/english/english_story.txt --lang en --preview

# Malayalam Story Preview
.\.venv\Scripts\python.exe main.py --file input/malayalam/malayalam_story.txt --lang ml --preview
```

### 2. Runtime Interactive Voice Selection (Choose 1 or 2)
When running without specifying `--voice`, the system prompts you interactively at runtime:

```powershell
.\.venv\Scripts\python.exe main.py --file input/malayalam/malayalam_story.txt --lang ml
```
Terminal prompt:
```text
=================================================================
 SELECT NARRATOR VOICE FOR MALAYALAM
=================================================================
  [1] Female Voice - Sobhana / Anjali (Authentic Kerala storytelling style)
  [2] Male Voice   - Midhun / Harish
-----------------------------------------------------------------
Enter choice [1 for Female, 2 for Male] (Default: 1): 
```
- Type **`1`** for **Female** voice (`Sobhana` / `Neerja`)
- Type **`2`** for **Male** voice (`Midhun` / `Prabhat`)

You can also pass `1` or `2` directly via the `--voice` flag:
```powershell
# Select Female voice using '1'
.\.venv\Scripts\python.exe main.py --file input/malayalam/malayalam_story.txt --lang ml --voice 1

# Select Male voice using '2'
.\.venv\Scripts\python.exe main.py --file input/english/english_story.txt --lang en --voice 2
```

### 4. Customizing Pace, Expressiveness, and Pause Multiplier
```powershell
.\.venv\Scripts\python.exe main.py --file input/english/english_story.txt --speed moderate --expressiveness dramatic --pause-scale 1.2
```

### 5. Running with Local Offline AI4Bharat Indic-Parler Model
```powershell
.\.venv\Scripts\python.exe main.py --file input/english/english_story.txt --engine indic-parler --voice male
```

### 6. Synthesize Direct Text with Tags
```powershell
.\.venv\Scripts\python.exe main.py --text "[whispering] 'Stay low,' she warned. [excited] 'We made it across!'" --voice female
```

---

## 🧪 Running Unit Tests

Run the test suite to verify tag parsing, sentence boundary handling, and audio prosody:

```powershell
.\.venv\Scripts\python.exe tests/test_emotions.py
.\.venv\Scripts\python.exe tests/test_english.py
.\.venv\Scripts\python.exe tests/test_malayalam.py
```
