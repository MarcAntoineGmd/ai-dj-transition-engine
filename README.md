# AI DJ Transition Engine

An AI-powered DJ application that analyzes two songs and generates intelligent, beat-aligned transitions.

## How It Works

1. Upload two songs and analyze each one (BPM, beats, key, energy, spectral features).
2. Rank the candidate transition points in the first song by the quality of a transition into the second song.
3. Generate the transition audio: tempo matching, beat-aligned extraction, time-stretching and an equal-power crossfade.
4. Download the resulting `.wav` file.

The whole pipeline is available through the API. The frontend currently covers upload, analysis and visualization; ranking and generation will be added to the interface later.

## Tech Stack

* Frontend: React, TypeScript, Vite, Tailwind CSS v4, WaveSurfer.js
* Backend: Python, FastAPI
* Audio Processing: librosa, NumPy, SciPy, soundfile
* Machine Learning (planned): PyTorch
* Testing (planned): pytest, Vitest
* Infrastructure (planned): Docker, GitHub Actions

## Project Structure

```text
ai-dj-transition-engine/
├── frontend/
│   └── src/
│       └── components/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── audio/
│   │   ├── models/
│   │   ├── transition/
│   │   └── main.py
│   ├── scripts/
│   ├── tmp_uploads/        (created at runtime, keep out of version control)
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

### `POST /api/transition/suggest/{file_id}`

Generates and scores candidate transition points for a previously uploaded file. Candidates are one per musical bar (every 4th beat), at least 8 seconds away from either end of the song, and are scored on energy (lower is better) and position in the song.

```json
[
  { "timestamp": 114.25, "score": 0.866 },
  { "timestamp": 88.46, "score": 0.826 }
]
```

### `POST /api/transition/bpm-match`

Determines the BPM compatibility strategy between two uploaded songs.

Request body:

```json
{ "file_id_a": "...", "file_id_b": "..." }
```

Response:

```json
{
  "strategy": "meet_in_middle",
  "target_bpm": 103.56,
  "stretch_factor_a": 0.9018,
  "stretch_factor_b": 1.1222,
  "within_safe_limit": false
}
```

`within_safe_limit` is advisory only: the endpoint does not block the result when the required stretch exceeds the ±6% safety margin. That decision is left to the caller.

### `POST /api/transition/rank`

Ranks candidate transition start points in song A by the composite quality of a transition into song B. Candidates are limited to the final third of song A and must leave at least 90% of the 15-second transition length. The transition always enters song B at its first detected beat. Returns an empty list when no candidate exists.

Request body:

```json
{ "file_id_a": "...", "file_id_b": "..." }
```

Response (best first):

```json
[
  {
    "start_a": 109.09,
    "start_b": 1.04,
    "total": 0.543,
    "scores": {
      "beat": 0.916,
      "bpm": 0.0,
      "key": 0.1,
      "energy": 0.747,
      "spectral": 0.691
    }
  }
]
```

All scores are between 0 and 1: `beat` (local regularity of the beat grid), `bpm` (stretch needed to match tempos), `key` (Camelot wheel compatibility), `energy` (match of relative intensity) and `spectral` (timbre similarity).

### `POST /api/transition/generate`

Generates the transition audio between two uploaded songs and returns it as a `.wav` download. The pipeline detects beats and BPM, computes the tempo-matching strategy, extracts a 15-second segment from each song starting on a detected beat, time-stretches both segments toward the target tempo, and blends them with an equal-power crossfade.

Request body:

```json
{ "file_id_a": "...", "file_id_b": "...", "start_a": 106.5 }
```

`start_a` is optional (in seconds) and is snapped to the nearest detected beat. When omitted, the transition starts about 15 seconds before the end of song A. The result is saved as `transition_<id_a>_<id_b>.wav` in `backend/tmp_uploads/` and overwritten by repeated calls with the same pair. Intermediate files are deleted after each run.

## Audio Analysis Modules

* `app/audio/beat_tracker.py`: BPM and beat position detection via `librosa.beat.beat_track`
* `app/audio/feature_extractor.py`: RMS energy, spectral centroid/bandwidth, chroma, MFCC
* `app/audio/key_detector.py`: musical key estimation via Krumhansl-Schmuckler chroma correlation
* `app/audio/analyzer.py`: orchestrates the three modules above into a single `SongAnalysis` result

## Transition Modules

* `app/transition/candidate_generator.py`: beat-aligned candidate points (one per bar, with safety margins)
* `app/transition/scorer.py`: scores candidate points within one song (energy and position)
* `app/transition/bpm_matcher.py`: tempo-matching strategy and stretch factors
* `app/transition/time_stretcher.py`: pitch-preserving time-stretch (phase vocoder)
* `app/transition/segment_extractor.py`: extracts a time range from an audio file
* `app/transition/crossfade.py`: equal-power crossfade
* `app/transition/engine.py`: full pipeline producing the transition audio
* `app/transition/quality_scorer.py`: composite quality score (beat, BPM, key, energy, spectral)
* `app/transition/selector.py`: ranks candidate transitions between two songs

The composite quality score combines five sub-scores with experimental weights: beat 0.30, BPM 0.20, key 0.15, energy 0.20, spectral 0.15.

## Manual Test Scripts

Analysis and transition modules can be checked outside the API. Run these from the `backend` directory with the virtual environment activated:

```powershell
python scripts\test_bpm.py tmp_uploads\<file>                              # BPM, key, beats, spectral features
python scripts\test_candidates.py tmp_uploads\<file>                       # candidate points in one song
python scripts\test_bpm_matching.py                                        # BPM matching on fixed test pairs
python scripts\test_time_stretch.py tmp_uploads\<file> 1.1                 # time-stretch by a factor
python scripts\test_segment.py tmp_uploads\<file> 10 25                    # extract a segment (seconds)
python scripts\test_crossfade.py tmp_uploads\<a> tmp_uploads\<b>           # full transition on two files
python scripts\test_quality_scorer.py                                      # BPM and key sub-scores
python scripts\test_quality_composite.py tmp_uploads\<a> tmp_uploads\<b>   # composite score per start point
python scripts\test_selector.py tmp_uploads\<a> tmp_uploads\<b>            # candidate ranking
```

Some scripts write intermediate `.wav` files next to the input file.

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

Uploading a file automatically triggers analysis and displays the waveform with beat markers, BPM, key, average energy and an energy curve.

## Frontend Components

* `AudioUpload.tsx`: handles file selection, upload, and triggering analysis
* `AnalysisResults.tsx`: displays the waveform (with beat markers), the BPM/key/energy summary, and the energy curve
* `WaveformPlayer.tsx`: WaveSurfer.js wrapper with play/pause and beat markers
* `EnergyChart.tsx`: simple SVG energy curve

## Audio and Copyright

The application is meant to be used with audio you have the right to process. Do not commit copyrighted songs to this repository: uploaded and generated files are stored in `backend/tmp_uploads/`, which should stay out of version control. Use royalty-free, self-created or properly licensed audio for any public demo.

## Known Limitations

* Key detection (Krumhansl-Schmuckler chroma correlation) can confuse a key with its relative major/minor (e.g. F# major vs D# minor), since both share the same seven notes. The Camelot-based key score treats relative keys as highly compatible (0.9), which limits the impact, but scores against neighboring keys can still differ (e.g. 0.8 vs 0.5).
* Candidate generation assumes 4 beats per bar and there is no true downbeat detection, so the rhythmic phase of two songs can still be misaligned even when start points are snapped to beats.
* Structure scoring is a position-based heuristic, not verse/chorus detection.
* Time-stretching uses a phase vocoder, which audibly degrades quality as the stretch grows. The ±6% safe limit is provisional.
* Composite score weights are experimental and not yet validated against human ratings.
* The spectral score compares song-level averages, not the transition region.
* BPM and key scores depend on detected values, so tempo-octave errors (half or double tempo) can affect them.
* Ranking only varies the start point in song A; the entry point in song B is always its first detected beat.
* Songs are re-analyzed on every `rank` and `generate` call (no caching yet).

## Future Work

* Machine learning ranking model trained on human-rated transitions, compared against the rule-based composite score.
* Longer, multi-passage transitions: compare the key of several candidate segments and shift pitch gradually from one song's key to the other's.
* More transition styles beyond the crossfade, inspired by real DJ sets: loop-based builds, stutter cuts alternating between the two songs, and AI-generated variations.
* Automatic playlist ordering by key compatibility between consecutive songs, with a priority order.
* True downbeat detection and selection of the entry point in song B.
* Ranking and generation in the frontend, analysis caching, and performance benchmarks.

## Development Status

* Phase 0: Project setup and basic frontend/backend communication.
* Phase 1: Audio file upload and validation.
* Phase 2: Audio analysis (BPM, beats, key, energy, spectral features) and frontend display.
* Phase 3: Visualization (waveform with beat markers, energy curve). Frontend styling left for later.
* Phase 4: Transition point detection (candidate generation and scoring).
* Phase 5: BPM compatibility between two songs.
* Phase 6: Transition engine (beat-aligned extraction, time-stretch, equal-power crossfade).
* Phase 7: Transition quality scoring (composite score and candidate ranking).
* Phase 8: Machine learning (problem definition and feature export). Up next.
