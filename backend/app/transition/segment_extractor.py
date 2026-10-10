"""
Feature: Audio segment extraction module
Purpose: Extract a precise time-range portion of an audio file (e.g.
         the last 15 seconds), as a standalone exportable clip.
Main files: app/transition/segment_extractor.py
How it works: load audio -> convert start/end times in seconds to
              sample indices -> slice the array -> write the result.
Concepts learned: converting time (seconds) to sample indices, NumPy
                   array slicing applied to audio.
"""

from pathlib import Path

import librosa
import soundfile as sf


def extract_segment(
    file_path: str | Path,
    start: float,
    end: float,
    output_path: str | Path,
) -> None:
    """
    Extrait la portion [start, end] (en secondes) d'un fichier audio
    et l'écrit dans output_path.
    """
    y, sr = librosa.load(str(file_path), sr=None)

    start_sample = int(start * sr)
    end_sample = int(end * sr)

    segment = y[start_sample:end_sample]

    sf.write(str(output_path), segment, sr)