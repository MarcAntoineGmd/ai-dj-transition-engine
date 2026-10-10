"""
Feature: Full transition pipeline manual test script
Purpose: Chain segment extraction, time-stretching, and crossfade on
         two real songs to produce an actual playable transition clip.
Main files: scripts/test_crossfade.py
How it works: take two file paths from the command line -> extract the
              outro of A and intro of B -> stretch both toward a common
              target BPM -> crossfade them -> export the result.
Concepts learned: combining several single-purpose modules into one
                   working pipeline, a first end-to-end DSP result.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import soundfile as sf

from app.audio.beat_tracker import detect_beats
from app.transition.bpm_matcher import match_bpm
from app.transition.segment_extractor import extract_segment
from app.transition.time_stretcher import stretch_audio
from app.transition.crossfade import crossfade

def _nearest_beat(target_time: float, beat_times: list[float]) -> float:
    """Retourne le beat détecté le plus proche de target_time."""
    return min(beat_times, key=lambda t: abs(t - target_time))

if len(sys.argv) != 3:
    print("Usage: python scripts/test_crossfade.py <song_a> <song_b>")
    sys.exit(1)

song_a = Path(sys.argv[1])
song_b = Path(sys.argv[2])

TRANSITION_DURATION = 15.0  # secondes

bpm_a, _ = detect_beats(song_a)
bpm_b, _ = detect_beats(song_b)
match = match_bpm(bpm_a, bpm_b)

print(f"BPM A: {bpm_a:.2f}, BPM B: {bpm_b:.2f}")
print(f"Stratégie: {match['strategy']}, within_safe_limit: {match['within_safe_limit']}")

from app.transition.candidate_generator import generate_candidates

duration_a = sf.info(str(song_a)).duration
_, beat_times_a = detect_beats(song_a)
_, beat_times_b = detect_beats(song_b)

# Point de départ aligné sur un beat, proche de "15s avant la fin"
start_a = _nearest_beat(duration_a - TRANSITION_DURATION, beat_times_a)
# Point de départ aligné sur le premier vrai beat de B (pas 0.0 arbitraire)
start_b = beat_times_b[0]

outro_a_path = song_a.parent / "outro_a.wav"
intro_b_path = song_b.parent / "intro_b.wav"

extract_segment(song_a, start_a, duration_a, outro_a_path)
extract_segment(song_b, start_b, start_b + TRANSITION_DURATION, intro_b_path)

stretched_a_path = song_a.parent / "outro_a_stretched.wav"
stretched_b_path = song_b.parent / "intro_b_stretched.wav"

stretch_audio(outro_a_path, match["stretch_factor_a"], stretched_a_path)
stretch_audio(intro_b_path, match["stretch_factor_b"], stretched_b_path)

y_a, sr = sf.read(str(stretched_a_path))
y_b, _ = sf.read(str(stretched_b_path))

result = crossfade(y_a, y_b)

output_path = song_a.parent / "transition_result.wav"
sf.write(str(output_path), result, sr)

print(f"Transition exportée : {output_path}")