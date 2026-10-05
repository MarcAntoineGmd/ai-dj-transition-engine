"""
Feature: Musical key detection module
Purpose: Estimate the musical key (e.g. "A minor") of an audio file using
         chroma features and Krumhansl-Schmuckler key profiles.
Main files: app/audio/key_detector.py
How it works: compute chroma -> average it over time -> correlate against
              24 reference key profiles (12 notes x major/minor) -> return
              the best-matching key.
Concepts learned: Krumhansl-Schmuckler key profiles, Pearson correlation
                   for pattern matching, why key detection isn't built
                   into librosa directly.
"""

from pathlib import Path

import librosa
import numpy as np

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Reference key profiles from Krumhansl & Kessler (1982), normalized to sum to 1.
MAJOR_PROFILE = np.array(
    [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
)
MINOR_PROFILE = np.array(
    [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
)


def detect_key(file_path: str | Path) -> str:
    """
    Estimate the musical key of an audio file.
    """
    y, sr = librosa.load(str(file_path), sr=None)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = chroma.mean(axis=1)

    best_score = -2.0  # minimum possible Pearson correlation is -1.0
    best_key = "Unknown"

    for i in range(12):
        major_rotated = np.roll(MAJOR_PROFILE, i)
        minor_rotated = np.roll(MINOR_PROFILE, i)

        major_score = np.corrcoef(chroma_mean, major_rotated)[0, 1]
        minor_score = np.corrcoef(chroma_mean, minor_rotated)[0, 1]

        if major_score > best_score:
            best_score = major_score
            best_key = f"{NOTE_NAMES[i]} major"

        if minor_score > best_score:
            best_score = minor_score
            best_key = f"{NOTE_NAMES[i]} minor"

    return best_key