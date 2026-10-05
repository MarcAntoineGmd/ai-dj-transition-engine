# AI DJ Transition Engine

An AI-powered DJ application that analyzes two songs and generates intelligent, beat-aligned transitions.

## Tech Stack

* Frontend: React, TypeScript, Vite
* Backend: Python, FastAPI
* Audio Processing: librosa, NumPy, SciPy, soundfile
* Machine Learning: PyTorch
* Testing: pytest, Vitest
* Infrastructure: Docker, GitHub Actions

## Project Structure

```text
ai-dj-transition-engine/
├── frontend/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── audio/
│   │   ├── models/
│   │   └── main.py
│   ├── scripts/
│   └── tests/
├── ml/
├── docs/
├── scripts/
├── docker-compose.yml
├── README.md
├── .gitignore
└── LICENSE
```

## Running the Backend

From the `backend` directory:

```bash
cd backend
```

Activate the Python virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload --port 8000
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## API Endpoints

### `GET /health`

Returns server status.

```json
{ "status": "ok" }
```

### `POST /api/audio/upload`

Uploads an audio file (`.mp3` or `.wav`, max 50 MB) and returns its metadata.

```json
{
  "id": "generated-uuid",
  "filename": "song.mp3",
  "duration": 214.3,
  "sample_rate": 44100
}
```

### `POST /api/audio/analyze/{file_id}`

Runs full audio analysis on a previously uploaded file: beat detection, key estimation, and spectral/energy feature extraction.

```json
{
  "id": "generated-uuid",
  "bpm": 92.29,
  "key": "F# major",
  "beat_times": [0.058, 0.72, 1.37, ...],
  "energy": [0.0, 0.03, 0.08, ...],
  "spectral_features": {
    "spectral_centroid_mean": 1736.9,
    "spectral_bandwidth_mean": 2533.1,
    "chroma_mean": [0.428, 0.416, ...],
    "mfcc_mean": [-232.06, 174.95, ...]
  }
}
```

**Known limitation:** key detection (Krumhansl-Schmuckler chroma correlation) can confuse a key with its relative major/minor (e.g. F# major vs D# minor), since both share the same 7 notes. Noted for revisiting during transition quality scoring (Phase 7) if it proves impactful.

## Audio Analysis Modules

* `app/audio/beat_tracker.py` — BPM and beat position detection via `librosa.beat.beat_track`
* `app/audio/feature_extractor.py` — RMS energy, spectral centroid/bandwidth, chroma, MFCC
* `app/audio/key_detector.py` — musical key estimation via Krumhansl-Schmuckler chroma correlation
* `app/audio/analyzer.py` — orchestrates the three modules above into a single `SongAnalysis` result

A manual validation script is available for testing analysis modules outside the API:

```bash
python scripts\test_bpm.py tmp_uploads\<filename>
```

## Running the Frontend

From the `frontend` directory:

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at:

```text
http://localhost:5173
```

Uploading a file automatically triggers analysis and displays BPM, key, and average energy.

## Development Status

- Phase 0 — Project setup and basic frontend/backend communication.
- Phase 1 — Audio file upload and validation.
- Phase 2 — Audio analysis (BPM, beats, key, energy, spectral features) and frontend display.
- Phase 3 — Visualization (waveform, energy curve, beat markers) — up next.
