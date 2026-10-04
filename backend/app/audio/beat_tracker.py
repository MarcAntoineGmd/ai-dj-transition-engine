"""
Feature: BPM/beat detection module
Purpose: Extract the tempo and beat positions from an audio file, in a
         reusable way the API can call.
Main files: app/audio/beat_tracker.py
How it works: load audio -> librosa.beat.beat_track -> convert to native
              Python types.
Concepts learned: separating business logic from entry points, JSON
                   serialization vs NumPy types, Python packages (__init__.py).
"""

from pathlib import Path

import librosa

"""
Analyze an audio file and return the estimated tempo (BPM) and the times of detected beats.
"""
def detect_beats(file_path: str | Path) -> tuple[float, list[float]]:
    y, sr = librosa.load(str(file_path), sr=None)

    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    tempo_value = float(tempo.item()) if hasattr(tempo, "item") else float(tempo)

    return tempo_value, beat_times.tolist()