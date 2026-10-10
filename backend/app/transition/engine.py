"""
Feature: Transition generation orchestrator
Purpose: Run the full transition pipeline (BPM matching, beat-aligned
         segment extraction, time-stretching, equal-power crossfade) on
         two uploaded songs and produce a single playable output file.
Main files: app/transition/engine.py
How it works: detect beats and BPM for both songs -> compute the BPM
              matching strategy -> align extraction points to the
              nearest detected beat -> extract and stretch both
              segments -> crossfade them -> write the result to disk.
Concepts learned: promoting validated script logic into a reusable
                   production module, orchestrating a multi-step DSP
                   pipeline behind one function call.
"""

from pathlib import Path

import soundfile as sf

from app.audio.beat_tracker import detect_beats
from app.transition.bpm_matcher import match_bpm
from app.transition.segment_extractor import extract_segment
from app.transition.time_stretcher import stretch_audio
from app.transition.crossfade import crossfade

TRANSITION_DURATION = 15.0


def _nearest_beat(target_time: float, beat_times: list[float]) -> float:
    return min(beat_times, key=lambda t: abs(t - target_time))


def generate_transition(song_a: Path, song_b: Path, output_dir: Path) -> Path:
    """
    Génère une transition entre song_a et song_b, écrit le résultat
    dans output_dir, et retourne le chemin du fichier produit.
    """
    bpm_a, beat_times_a = detect_beats(song_a)
    bpm_b, beat_times_b = detect_beats(song_b)
    match = match_bpm(bpm_a, bpm_b)

    duration_a = sf.info(str(song_a)).duration
    start_a = _nearest_beat(duration_a - TRANSITION_DURATION, beat_times_a)
    start_b = beat_times_b[0]

    outro_a_path = output_dir / "_outro_a.wav"
    intro_b_path = output_dir / "_intro_b.wav"
    stretched_a_path = output_dir / "_outro_a_stretched.wav"
    stretched_b_path = output_dir / "_intro_b_stretched.wav"

    extract_segment(song_a, start_a, duration_a, outro_a_path)
    extract_segment(song_b, start_b, start_b + TRANSITION_DURATION, intro_b_path)

    stretch_audio(outro_a_path, match["stretch_factor_a"], stretched_a_path)
    stretch_audio(intro_b_path, match["stretch_factor_b"], stretched_b_path)

    y_a, sr = sf.read(str(stretched_a_path))
    y_b, _ = sf.read(str(stretched_b_path))

    result = crossfade(y_a, y_b)

    output_path = output_dir / f"transition_{song_a.stem}_{song_b.stem}.wav"
    sf.write(str(output_path), result, sr)

    for temp_file in [outro_a_path, intro_b_path, stretched_a_path, stretched_b_path]:
        temp_file.unlink()

    return output_path