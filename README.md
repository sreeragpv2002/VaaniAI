# VaaniAI — English and Malayalam Narration

VaaniAI turns stories and other long-form text into spoken audio in English (Indian English voices) and Malayalam. It includes a small local browser interface and a command-line interface.

## What it does

- Enter or paste text, choose English or Malayalam, and select a female or male narrator.
- When Malayalam is selected, the UI checks that the text contains Malayalam script and blocks generation if it appears to be English; the server enforces the same check.
- Split text into sentences and analyze punctuation, dialogue, and common emotional cues.
- Use inline delivery tags such as `[whispering]`, `[excited]`, `[slowly]`, and `[pause]`. Tags are removed from the text sent to speech synthesis.
- Add pauses between sentences, smooth audio segment edges, normalize peak level, and export WAV.
- Track sentence-by-sentence generation progress in the browser UI, listen to the result, see its saved path, or download the WAV.
- Use Edge TTS in the browser app and CLI. The CLI also supports the optional local Indic-Parler engine and optional OpenVoice conversion.

Emotion and delivery are approximate. Edge TTS changes supported rate, pitch, and volume settings; Indic-Parler uses descriptive prompts. Vocalization tags do not create separate sound effects such as a cough or laugh, and neither engine guarantees an exact performance or timbre.

## Browser interface

The interface uses a dark, monochrome, monospace layout with a purple accent and a lightweight animated particle backdrop. The centered narration form is transparent so the enlarged particle ring remains visible behind it, with project information in a responsive footer. It is plain HTML, CSS, and JavaScript served by Python's standard library; no Node.js or frontend package install is needed. The web interface currently generates with Edge TTS.

The app binds to `127.0.0.1` on port `8000` and saves generated files under `output/web/`.

## Technology

| Part | Technology |
| --- | --- |
| Application and CLI | Python |
| Browser UI and local server | HTML, CSS, JavaScript, Python `http.server` |
| Text and emotion processing | Project's Python sentence, punctuation, and emotion modules |
| Default speech engine | Edge TTS (`edge-tts`) |
| MP3 decoding | FFmpeg bundled by `imageio-ffmpeg` |
| Audio processing | NumPy and SoundFile |
| Optional local speech engine | AI4Bharat Indic-Parler-TTS, PyTorch, Transformers |
| Optional voice conversion | OpenVoice CLI |

## Requirements

### Required for the browser UI and default Edge TTS engine

- Python 3.10 or newer is recommended.
- Internet access is required while Edge TTS generates speech.
- Install the core Python packages from `requirements.txt`.

### Optional

- `requirements-parler.txt`: PyTorch, Transformers, and Indic-Parler-TTS for the local Parler engine. The model is downloaded the first time it is used; device and memory needs depend on the selected model and machine.
- `requirements-voice-cloning.txt`: OpenVoice CLI for voice conversion through the CLI's `--clone-voice` option.
- `requirements-dev.txt`: Pytest for running tests.

## Setup on Windows

From the project folder in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Start the browser app

```powershell
.\.venv\Scripts\python.exe app.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Paste or type text, choose a language and voice, and click **Generate narration**. Keep the terminal open while the app is running; press `Ctrl+C` there to stop it.

### Use the CLI

Preview segmentation and emotion analysis without generating audio:

```powershell
.\.venv\Scripts\python.exe main.py --file input/english/english_story.txt --lang en --preview
.\.venv\Scripts\python.exe main.py --file input/malayalam/malayalam_story.txt --lang ml --preview
```

Generate speech from a file or direct text:

```powershell
.\.venv\Scripts\python.exe main.py --file input/malayalam/malayalam_story.txt --lang ml --voice female
.\.venv\Scripts\python.exe main.py --text "[whispering] Stay close." --lang en --voice male
```

Select `--voice female` or `--voice male`. If omitted in an interactive terminal, the CLI prompts for a voice. Use `--output path.wav` to choose an output file. Run `main.py --help` for all CLI options.

### Install optional CLI engines

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-parler.txt
.\.venv\Scripts\python.exe -m pip install -r requirements-voice-cloning.txt
```

Parler example:

```powershell
.\.venv\Scripts\python.exe main.py --file input/english/english_story.txt --lang en --engine indic-parler --voice male
```

Voice conversion example:

```powershell
.\.venv\Scripts\python.exe main.py --file input/english/english_story.txt --lang en --voice female --clone-voice input/actress.wav
```

Use a reference recording you have permission to use.

## Project layout

```text
MalayalamTTS/
├── app.py                         # Local browser app
├── main.py                        # CLI and synthesis orchestration
├── requirements.txt               # Core dependencies
├── requirements-parler.txt        # Optional local Parler dependencies
├── requirements-voice-cloning.txt # Optional voice conversion dependency
├── requirements-dev.txt           # Test dependency
├── config/                        # Voice, language, and audio settings
├── input/                         # Example English and Malayalam text
├── output/                        # Generated WAV files (ignored by Git)
├── src/
│   ├── audio/                     # Synthesis engines and audio processing
│   ├── emotion/                   # Tag mapping and emotion analysis
│   ├── languages/                 # English and Malayalam pipelines
│   ├── text_processing/           # Normalization and sentence splitting
│   └── utils/                     # File management and logging
└── tests/                         # Unit tests
```

## Run tests

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```
