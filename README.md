# 🎙️ Audio Transcriber — Project Docs

## What This Project Does
Record audio from your browser → send it to a local Python server → Whisper AI transcribes it → text appears on screen. Supports **any language** automatically.

---

## Project Structure

```
Model testing/
├── recorder.html   # Frontend (browser UI)
├── server.py       # Backend (Flask + Whisper)
└── README.md       # This file
```

---

## How It Works (Step by Step)

### 1. `recorder.html` — The Frontend
- Browser asks for **microphone permission**
- Uses **MediaRecorder API** to record your voice as a `.webm` audio blob
- On stop, sends the audio to `http://localhost:5001/transcribe` via a `POST` request using `FormData`
- Displays the returned transcription text and detected language on screen

### 2. `server.py` — The Backend

```python
model = whisper.load_model("base")
```
- Loads OpenAI's **Whisper** model (`base` size) into memory when server starts
- Whisper is a deep learning model trained on 680,000 hours of multilingual audio

```python
@app.route("/transcribe", methods=["POST"])
def transcribe():
```
- Flask listens for POST requests at `/transcribe`

```python
tmp = tempfile.NamedTemporaryFile(suffix=".webm", delete=False)
tmp.close()
audio.save(tmp.name)
```
- Creates a **temporary file** on disk to store the received audio
- File is closed before saving (required on Windows to avoid file lock errors)

```python
result = model.transcribe(tmp.name, task="transcribe", language=None)
os.unlink(tmp.name)
```
- Whisper transcribes the audio file
- `language=None` → Whisper **auto-detects** the spoken language (Hindi, English, Spanish, etc.)
- `task="transcribe"` → returns text in the **original language** (not translated)
- Temp file is deleted after transcription

```python
return jsonify({"text": result["text"], "language": result["language"]})
```
- Returns the transcribed text + detected language code (e.g. `hi`, `en`, `es`) back to the browser

---

## Language Support
Whisper supports **99 languages** including:

| Language | Code |
|----------|------|
| Hindi    | hi   |
| English  | en   |
| Spanish  | es   |
| French   | fr   |
| Arabic   | ar   |
| Japanese | ja   |
| German   | de   |
| ...and 92 more | — |

No configuration needed — it detects automatically.

---

## Whisper Model Sizes

| Model  | Size  | Speed  | Accuracy |
|--------|-------|--------|----------|
| tiny   | 75MB  | Fast   | Low      |
| base   | 145MB | Medium | Medium   |
| small  | 465MB | Slow   | Good     |
| medium | 1.5GB | Slower | Better   |
| large  | 2.9GB | Slowest| Best     |

Currently using `base`. Change in `server.py` line:
```python
model = whisper.load_model("base")  # change to "small", "medium", etc.
```

---

## How to Run

**1. Install dependencies:**
```bash
pip install flask flask-cors openai-whisper
```

**2. Start the server:**
```bash
python server.py
```

**3. Open `recorder.html` in Chrome**

---

## Common Errors

| Error | Fix |
|-------|-----|
| `WinError 32` file locked | Already fixed — temp file is closed before use |
| `Could not connect to server` | Make sure `python server.py` is running |
| `debug=True` warning | Fine for local use, disable for production |
