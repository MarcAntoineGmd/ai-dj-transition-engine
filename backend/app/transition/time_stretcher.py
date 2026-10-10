"""
Feature: Audio time-stretching module
Purpose: Change the playback speed/duration of an audio file by a given
         factor without altering its pitch, and export the result.
Main files: app/transition/time_stretcher.py
How it works: load audio -> apply librosa's phase vocoder time-stretch
              -> write the result to a new file via soundfile.
Concepts learned: phase vocoder time-stretching, librosa's rate
                   convention (rate > 1.0 speeds up / shortens duration),
                   writing audio arrays to disk with soundfile.
"""

from pathlib import Path

import librosa
import soundfile as sf


def stretch_audio(file_path: str | Path, factor: float, output_path: str | Path) -> None:
    """
    Applique un time-stretch de `factor` à l'audio et écrit le résultat
    dans `output_path`. factor > 1.0 accélère (raccourcit la durée),
    factor < 1.0 ralentit (allonge la durée) — même convention que
    app.transition.bpm_matcher.
    """
    y, sr = librosa.load(str(file_path), sr=None)

    stretched = librosa.effects.time_stretch(y, rate=factor)

    sf.write(str(output_path), stretched, sr)