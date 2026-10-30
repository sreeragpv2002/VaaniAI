"""Local browser interface for Malayalam and English narration generation."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import uuid
from urllib.parse import urlparse

from config.settings import OUTPUT_DIR
from main import synthesize_narration


MAX_TEXT_LENGTH = 100_000
TASKS = {}
TASKS_LOCK = threading.Lock()

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#000000">
  <meta name="description" content="VaaniAI creates expressive English and Malayalam narration.">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E%3Crect width='40' height='40' rx='20' fill='%23000'/%3E%3Ccircle cx='20' cy='20' r='18' fill='none' stroke='white' stroke-width='1.5'/%3E%3Cpath d='M20 6 23 16 33 13 26 20 34 25 24 24 22 34 19 25 10 29 15 21 6 17 16 16Z' fill='white'/%3E%3C/svg%3E">
  <title>VAANI — Narration lab</title>
  <style>
    :root { color-scheme: dark; font: 12px/1.45 "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; color: #ddd; background: #000; --accent: #aa88ff; --muted: #858585; --line: #292929; --chip: #1c1c1c; }
    * { box-sizing: border-box; }
    html, body { width: 100%; height: 100%; margin: 0; overflow: hidden; background: #000; }
    body { min-width: 320px; }
    #bg { position: fixed; inset: 0; z-index: 0; width: 100%; height: 100%; pointer-events: none; }
    .ui { position: fixed; z-index: 1; inset: 0; overflow: hidden; pointer-events: none; text-transform: uppercase; }
    .brand { position: absolute; top: 24px; left: 24px; display: flex; align-items: center; gap: 13px; mix-blend-mode: plus-lighter; }
    .brand-mark { width: 40px; height: 40px; flex: 0 0 40px; }
    .brand-name { color: #fff; font-size: 20px; line-height: 1; letter-spacing: .16em; }
    .brand-subtitle { margin-top: 5px; color: var(--muted); font-size: 10px; letter-spacing: .1em; }
    .counter { position: absolute; top: 24px; right: 24px; display: grid; width: 44px; height: 44px; place-items: center; border: 1px solid var(--line); border-radius: 50%; color: #fff; background: #0a0a0a; font-size: 13px; }
    .compose { position: absolute; top: 48%; left: 50%; display: flex; width: min(700px, calc(100vw - 48px)); max-height: calc(100vh - 220px); flex-direction: column; overflow-y: auto; padding: 24px 30px 20px; transform: translate(-50%, -50%); background: transparent; pointer-events: auto; scrollbar-width: none; }
    .compose::-webkit-scrollbar { display: none; }
    .section-kicker { margin: 0 0 9px; color: var(--accent); font-size: 11px; font-weight: 500; letter-spacing: .04em; text-align: center; text-transform: uppercase; }
    .compose-title { margin: 0 0 10px; color: #f1f1f1; font-size: clamp(25px, 2.2vw, 32px); font-weight: 400; letter-spacing: .015em; line-height: 1.2; text-align: center; text-transform: uppercase; }
    .compose-note { max-width: 560px; margin: 0 auto 18px; color: #b8b8b8; font-size: clamp(12px, 1vw, 14px); line-height: 1.75; text-align: center; text-transform: none; }
    label { display: block; margin: 14px 0 7px; color: #c9c9c9; font-size: 11px; letter-spacing: .08em; text-transform: uppercase; }
    .text-wrap { position: relative; }
    textarea, select { width: 100%; border: 1px solid #444; border-radius: 2px; outline: none; color: #ddd; background: #08080888; font: inherit; }
    textarea { display: block; height: 190px; min-height: 145px; max-height: 260px; resize: vertical; padding: 13px 13px 28px; font-size: 12px; line-height: 1.7; text-transform: none; }
    textarea::placeholder { color: #666; }
    .validation { margin: 7px 0 0; color: #ff9a9a; font-size: 10px; line-height: 1.5; }
    textarea:focus, select:focus { border-color: #8b6bcd; background: #08080899; box-shadow: 0 0 0 1px #aa88ff30; }
    .char-count { position: absolute; right: 8px; bottom: 7px; color: #666; font-size: 9px; pointer-events: none; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    select { height: 43px; padding: 0 11px; font-size: 11px; }
    .button { display: flex; width: 100%; min-height: 48px; align-items: center; justify-content: space-between; margin-top: 18px; padding: 12px 14px; border: 1px solid #eee; border-radius: 2px; color: #050505; background: #e6e6e6; font: inherit; font-size: 11px; font-weight: 700; letter-spacing: .07em; text-transform: uppercase; cursor: pointer; transition: color .2s, background .2s, border-color .2s; }
    .button:hover:not(:disabled) { border-color: var(--accent); color: #fff; background: #18151f; }
    .button:disabled { cursor: wait; opacity: .6; }
    .button:focus-visible, .tag:focus-visible, .download:focus-visible { outline: 1px solid var(--accent); outline-offset: 3px; }
    .button svg { width: 16px; height: 16px; }
    .helper { margin: 8px 0 17px; color: #707070; font-size: 9px; line-height: 1.5; }
    #status { margin: 2px 0 17px; padding: 11px 0 13px; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
    .status-head { display: flex; justify-content: space-between; gap: 10px; margin-bottom: 9px; color: #aaa; font-size: 10px; }
    #message { color: #ddd; font-weight: 400; }
    #percent { color: var(--accent); font-variant-numeric: tabular-nums; }
    progress { display: block; width: 100%; height: 2px; border: 0; border-radius: 0; background: #292929; }
    progress::-webkit-progress-bar { background: #292929; }
    progress::-webkit-progress-value { background: var(--accent); transition: width .3s ease; }
    progress::-moz-progress-bar { background: var(--accent); }
    .error { color: #ff8c8c !important; }
    .output-block { margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--line); }
    .output-block h2 { margin: 0 0 8px; color: var(--accent); font-size: 10px; font-weight: 500; }
    .output-block p { margin: 0; color: #888; font-size: 9px; }
    .site-footer { position: absolute; right: 28px; bottom: 17px; left: 28px; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 34px; padding-top: 12px; border-top: 1px solid var(--line); mix-blend-mode: plus-lighter; }
    .footer-block h2 { margin: 0 0 5px; color: var(--accent); font-size: 10px; font-weight: 500; }
    .footer-block p { margin: 0; color: #aaa; font-size: 9px; line-height: 1.55; }
    #result { margin-top: 12px; padding: 12px; border: 1px solid #38313f; background: #08070be8; pointer-events: auto; }
    .result-title { margin: 0 0 10px; color: #e4e4e4; font-size: 10px; font-weight: 400; text-transform: uppercase; }
    .result-title span { color: var(--accent); }
    audio { display: block; width: 100%; height: 34px; margin: 7px 0 10px; }
    .result-bottom { display: flex; align-items: center; justify-content: space-between; gap: 10px; color: #888; font-size: 9px; }
    .download { color: var(--accent); text-decoration: none; }
    .download:hover { opacity: .7; }
    #filePath { margin-top: 8px; overflow-wrap: anywhere; color: #777; font-size: 9px; }
    [hidden] { display: none !important; }
    @media (max-width: 1000px) { .site-footer { gap: 20px; } .footer-block p { font-size: 8px; } }
    @media (max-width: 760px) {
      html, body { height: auto; min-height: 100%; overflow-x: hidden; overflow-y: auto; }
      .ui { position: relative; min-height: 100vh; min-height: 100svh; overflow: visible; padding: 150px 22px 24px; }
      .brand { top: 19px; left: 22px; }
      .counter { top: 19px; right: 22px; }
      .compose { position: relative; top: auto; left: auto; width: 100%; max-width: 600px; max-height: none; overflow: visible; margin: 0 auto; padding: 18px; transform: none; }
      .site-footer { position: relative; inset: auto; grid-template-columns: 1fr; gap: 17px; max-width: 600px; margin: 25px auto 0; padding: 16px 2px 0; }
      .footer-block p { font-size: 9px; }
      #bg { position: fixed; opacity: .55; }
      textarea { min-height: 165px; }
    }
    @media (max-width: 760px) { .compose { top: auto; } .compose-title { font-size: clamp(24px, 6vw, 31px); } }
    @media (max-width: 430px) { .ui { padding: 130px 14px 20px; } .brand { left: 14px; } .counter { right: 14px; } .compose { padding: 16px 13px; } .row { gap: 7px; } select { padding-inline: 5px; } }
    @media (prefers-reduced-motion: reduce) { *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; } }
  </style>
</head>
<body>
<canvas id="bg" aria-hidden="true"></canvas>
<div class="ui">
  <header class="brand">
    <svg class="brand-mark" viewBox="0 0 40 40" fill="none" aria-hidden="true">
      <circle cx="20" cy="20" r="18.5" stroke="white" stroke-width="1.5"/>
      <path d="M20 7.5 22.8 16l8.7-3-5.8 7 7.8 5-9.2-.3L22 33l-2-8.3-8 4.4 4.8-7.5-8.4-3.8 9.1-.9L16 8.5l4 7.4 6-5.6L20 20z" fill="white"/>
    </svg>
    <div><div class="brand-name">VAANI</div><div class="brand-subtitle">Narration lab</div></div>
  </header>
  <div class="counter" aria-label="Studio number">01</div>
  <section class="compose">
    <p class="section-kicker">[ create / 01 ]</p>
    <h1 class="compose-title">Give your words a voice.</h1>
    <p class="compose-note">Paste your story, book chapter, or script. Choose a language and narrator to bring your words to life.</p>
    <form id="form">
      <label for="text">Narration text</label>
      <div class="text-wrap">
        <textarea id="text" maxlength="100000" required placeholder="Type or paste your text here…&#10;&#10;നിങ്ങളുടെ കഥ ഇവിടെ എഴുതൂ…"></textarea>
        <span class="char-count" id="charCount">0 / 100,000</span>
      </div>
      <p class="validation" id="validation" aria-live="polite" hidden></p>
      <div class="row">
        <div><label for="language">Language</label><select id="language"><option value="en">English</option><option value="ml">Malayalam · മലയാളം</option></select></div>
        <div><label for="voice">Voice</label><select id="voice"><option value="female">Female</option><option value="male">Male</option></select></div>
      </div>
      <button class="button" id="generate" type="submit"><span id="buttonLabel">Generate narration</span><svg aria-hidden="true" viewBox="0 0 20 20" fill="none"><path d="M3 10h13m-5-5 5 5-5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
      <p class="helper">Audio is saved as a WAV file when generation finishes.</p>
    </form>
    <section id="status" aria-live="polite" hidden>
      <div class="status-head"><strong id="message">Preparing narration...</strong><span id="percent">0%</span></div>
      <progress id="progress" max="100" value="0"></progress>
    </section>
    <section class="output-block">
      <h2>[ output ]</h2>
      <section id="result" aria-live="polite" hidden>
        <h3 class="result-title"><span>✓</span> Narration ready</h3>
        <audio id="player" controls></audio>
        <div class="result-bottom"><span>Listen here or save a copy</span><a class="download" id="download">Download WAV ↓</a></div>
        <div id="filePath"></div>
      </section>
      <p id="outputHint">Your finished audio and download link will appear here.</p>
    </section>
  </section>
  <footer class="site-footer">
    <section class="footer-block"><h2>[ info ]</h2><p>Expressive spoken narration for English and Malayalam stories.</p></section>
    <section class="footer-block"><h2>[ aims ]</h2><p>Choose a narrator, follow sentence-by-sentence progress, then listen or download.</p></section>
    <section class="footer-block"><h2>[ exploring ]</h2><p>Indian English · Malayalam · Female / male voices · WAV audio</p></section>
  </footer>
</div>
<script>
const form = document.querySelector('#form');
const button = document.querySelector('#generate');
const buttonLabel = document.querySelector('#buttonLabel');
const textInput = document.querySelector('#text');
const statusBox = document.querySelector('#status');
const message = document.querySelector('#message');
const progress = document.querySelector('#progress');
const percent = document.querySelector('#percent');
const result = document.querySelector('#result');
const outputHint = document.querySelector('#outputHint');
const languageInput = document.querySelector('#language');
const validation = document.querySelector('#validation');
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
let isGenerating = false;

function updateInputState() {
  document.querySelector('#charCount').textContent = `${textInput.value.length.toLocaleString()} / 100,000`;
  const malayalamCount = [...textInput.value].filter(char => /[\u0D00-\u0D7F]/.test(char)).length;
  const latinCount = (textInput.value.match(/[A-Za-z]/g) || []).length;
  const looksMalayalam = malayalamCount >= 3 && malayalamCount >= latinCount;
  const mismatch = languageInput.value === 'ml' && textInput.value.trim() && !looksMalayalam;
  validation.textContent = mismatch
    ? 'Malayalam is selected, but this text does not look like Malayalam. Paste Malayalam text or change the language.'
    : '';
  validation.hidden = !mismatch;
  button.disabled = isGenerating || Boolean(mismatch);
}

textInput.addEventListener('input', updateInputState);
languageInput.addEventListener('change', updateInputState);
updateInputState();

form.addEventListener('submit', async event => {
  event.preventDefault();
  isGenerating = true;
  button.disabled = true;
  buttonLabel.textContent = 'Creating narration…';
  statusBox.hidden = false;
  result.hidden = true;
  outputHint.hidden = true;
  message.classList.remove('error');
  message.textContent = 'Starting audio generation...';
  progress.value = 0;
  percent.textContent = '0%';
  try {
    const response = await fetch('/api/generate', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text: textInput.value, lang: document.querySelector('#language').value, voice: document.querySelector('#voice').value})
    });
    const started = await response.json();
    if (!response.ok) throw new Error(started.error || 'Could not start generation.');
    let task;
    do {
      await sleep(700);
      const poll = await fetch(`/api/tasks/${started.id}`);
      task = await poll.json();
      if (!poll.ok) throw new Error(task.error || 'Could not read generation status.');
      message.textContent = task.message;
      progress.value = task.progress;
      percent.textContent = `${task.progress}%`;
    } while (task.status === 'queued' || task.status === 'running');
    if (task.status !== 'complete') throw new Error(task.error || 'Audio generation failed.');
    document.querySelector('#player').src = task.audio_url;
    document.querySelector('#download').href = task.download_url;
    document.querySelector('#filePath').textContent = `Saved to: ${task.output_path}`;
    result.hidden = false;
  } catch (error) {
    message.textContent = error.message;
    message.classList.add('error');
    outputHint.textContent = 'Generation did not finish. Check the message above and try again.';
    outputHint.hidden = false;
  } finally {
    isGenerating = false;
    buttonLabel.textContent = 'Generate narration';
    updateInputState();
  }
});

const canvas = document.querySelector('#bg');
const ctx = canvas.getContext('2d');
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
let width = 0, height = 0, dpr = 1, frame = 0;
let pointer = {x: -1000, y: -1000};
let points = [];
function resize() {
  dpr = Math.min(window.devicePixelRatio || 1, 2);
  width = window.innerWidth;
  height = window.innerHeight;
  canvas.width = Math.round(width * dpr);
  canvas.height = Math.round(height * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  const count = width < 760 ? 850 : 2600;
  points = Array.from({length: count}, () => ({
    u: Math.random() * Math.PI * 2,
    v: Math.random() * Math.PI * 2,
    size: .35 + Math.random() * 1.05,
    tone: Math.random(),
    phase: Math.random() * Math.PI * 2
  }));
  draw();
}
function draw() {
  frame += reduceMotion ? 0 : .006;
  ctx.clearRect(0, 0, width, height);
  ctx.globalCompositeOperation = 'lighter';
  const scale = Math.min(width, height) * (width < 760 ? .43 : .62);
  const cx = width * .5;
  const cy = height * (width < 760 ? .45 : .5);
  const rot = frame * .16;
  for (const p of points) {
    const tube = .22;
    const ring = .62 + tube * Math.cos(p.v);
    let x = ring * Math.cos(p.u);
    let y = ring * Math.sin(p.u);
    let z = tube * Math.sin(p.v);
    const rx = y * Math.sin(.31) + z * Math.cos(.31);
    z = y * Math.cos(.31) - z * Math.sin(.31);
    y = rx;
    const xx = x * Math.cos(rot) - z * Math.sin(rot);
    z = x * Math.sin(rot) + z * Math.cos(rot);
    const depth = 1 / (1 - z * .22);
    let px = cx + xx * scale * depth;
    let py = cy + y * scale * depth;
    const dx = px - pointer.x, dy = py - pointer.y;
    const distance = Math.hypot(dx, dy);
    if (distance < 125 && distance > 0) {
      const push = (1 - distance / 125) * 17;
      px += dx / distance * push;
      py += dy / distance * push;
    }
    const alpha = .18 + Math.max(0, Math.min(1, (z + .75) / 1.7)) * .5;
    const sparkle = .88 + Math.sin(frame * 2 + p.phase) * .12;
    ctx.globalAlpha = alpha * sparkle;
    ctx.fillStyle = p.tone > .975 ? '#b59aff' : (p.tone > .82 ? '#a4a0b5' : '#d2d2d2');
    const size = p.size * (z > 0 ? 1.15 : .82);
    ctx.fillRect(px, py, size, size);
  }
  ctx.globalAlpha = 1;
  ctx.globalCompositeOperation = 'source-over';
  if (!reduceMotion) requestAnimationFrame(draw);
}
window.addEventListener('resize', resize);
window.addEventListener('pointermove', event => {
  pointer = {x: event.clientX, y: event.clientY};
  if (reduceMotion) draw();
}, {passive: true});
resize();
</script>
</body>
</html>"""


def validate_generation_request(payload):
    if not isinstance(payload, dict):
        raise ValueError("Request must be a JSON object.")
    text = payload.get("text")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Enter some text to narrate.")
    if len(text) > MAX_TEXT_LENGTH:
        raise ValueError(f"Text must be {MAX_TEXT_LENGTH:,} characters or fewer.")
    lang = payload.get("lang")
    if lang not in {"en", "ml"}:
        raise ValueError("Choose English or Malayalam.")
    if lang == "ml" and not is_malayalam_text(text):
        raise ValueError("Malayalam is selected, but the text does not look like Malayalam.")
    voice = payload.get("voice")
    if voice not in {"male", "female"}:
        raise ValueError("Choose a male or female voice.")
    return {"text": text.strip(), "lang": lang, "voice": voice}


def is_malayalam_text(text):
    malayalam_count = sum("\u0D00" <= char <= "\u0D7F" for char in text)
    latin_count = sum(char.isascii() and char.isalpha() for char in text)
    return malayalam_count >= 3 and malayalam_count >= latin_count


def run_generation(task_id, request_data):
    output_path = OUTPUT_DIR / "web" / f"narration_{task_id}.wav"

    def report_progress(current, total, message):
        with TASKS_LOCK:
            task = TASKS[task_id]
            task.update(
                current=current,
                total=total,
                progress=round(current * 100 / total) if total else 0,
                message=message,
            )

    with TASKS_LOCK:
        TASKS[task_id]["status"] = "running"
        TASKS[task_id]["message"] = "Preparing narration..."

    try:
        result_path = synthesize_narration(
            text=request_data["text"],
            lang=request_data["lang"],
            voice=request_data["voice"],
            engine_type="edge-tts",
            output_path=str(output_path),
            progress_callback=report_progress,
        )
        with TASKS_LOCK:
            TASKS[task_id].update(
                status="complete",
                progress=100,
                message="Audio is ready",
                output_path=result_path,
            )
    except Exception as exc:
        with TASKS_LOCK:
            TASKS[task_id].update(
                status="failed",
                message="Audio generation failed",
                error=str(exc)[:500],
            )


class VaaniHandler(BaseHTTPRequestHandler):
    def _send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            body = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        parts = path.strip("/").split("/")
        if len(parts) == 3 and parts[:2] == ["api", "tasks"]:
            with TASKS_LOCK:
                task = TASKS.get(parts[2])
                response = dict(task) if task else None
            if response is None:
                self._send_json(404, {"error": "Generation task not found."})
                return
            response["audio_url"] = f"/audio/{parts[2]}"
            response["download_url"] = f"/download/{parts[2]}"
            self._send_json(200, response)
            return

        if len(parts) == 2 and parts[0] in {"audio", "download"}:
            with TASKS_LOCK:
                task = TASKS.get(parts[1])
                file_path = Path(task["output_path"]) if task and task.get("status") == "complete" else None
            if not file_path or not file_path.is_file():
                self._send_json(404, {"error": "Generated audio not found."})
                return
            disposition = "inline" if parts[0] == "audio" else "attachment"
            self.send_response(200)
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(file_path.stat().st_size))
            self.send_header("Content-Disposition", f'{disposition}; filename="{file_path.name}"')
            self.end_headers()
            with file_path.open("rb") as audio_file:
                while chunk := audio_file.read(1024 * 1024):
                    self.wfile.write(chunk)
            return

        self._send_json(404, {"error": "Page not found."})

    def do_POST(self):
        if urlparse(self.path).path != "/api/generate":
            self._send_json(404, {"error": "Endpoint not found."})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size <= 0 or size > MAX_TEXT_LENGTH * 4:
                raise ValueError("Request is empty or too large.")
            request_data = validate_generation_request(json.loads(self.rfile.read(size)))
        except (ValueError, json.JSONDecodeError) as exc:
            self._send_json(400, {"error": str(exc)})
            return

        with TASKS_LOCK:
            if any(task["status"] in {"queued", "running"} for task in TASKS.values()):
                self._send_json(409, {"error": "A narration is already being generated. Please wait for it to finish."})
                return
            task_id = uuid.uuid4().hex
            TASKS[task_id] = {
                "status": "queued",
                "progress": 0,
                "current": 0,
                "total": 0,
                "message": "Waiting to start...",
            }
            threading.Thread(
                target=run_generation,
                args=(task_id, request_data),
                daemon=True,
            ).start()
        self._send_json(202, {"id": task_id})


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 8000), VaaniHandler)
    print("VaaniAI is ready at http://127.0.0.1:8000 (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping VaaniAI...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
