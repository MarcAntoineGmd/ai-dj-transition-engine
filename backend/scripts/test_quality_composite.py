"""
Feature: Composite transition quality manual test script
Purpose: Score several candidate start points in song A against the
         start of song B, to see which sub-scores vary between
         candidates and which depend only on the song pair.
Main files: scripts/test_quality_composite.py
How it works: analyze both songs -> take the engine's default start
              point plus the top 3 scored candidates of A -> print the
              composite score and breakdown for each.
Concepts learned: separating pair-level scores (BPM, key, spectral)
                   from point-level scores (beat, energy).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import soundfile as sf

from app.audio.analyzer import analyze_song
from app.transition.candidate_generator import generate_candidates
from app.transition.quality_scorer import transition_quality
from app.transition.scorer import score_candidates

if len(sys.argv) != 3:
    print("Usage: python scripts/test_quality_composite.py <song_a> <song_b>")
    sys.exit(1)

song_a = Path(sys.argv[1])
song_b = Path(sys.argv[2])

analysis_a = analyze_song(song_a, "a")
analysis_b = analyze_song(song_b, "b")
duration_a = sf.info(str(song_a)).duration
duration_b = sf.info(str(song_b)).duration

t_b = analysis_b.beat_times[0]

default_a = min(analysis_a.beat_times, key=lambda t: abs(t - (duration_a - 15.0)))
candidates = generate_candidates(analysis_a.beat_times, duration_a)
top = score_candidates(candidates, analysis_a.energy, duration_a)[:3]

points = [("fin du morceau (défaut moteur)", default_a)]
points += [(f"candidat #{i + 1}", c["timestamp"]) for i, c in enumerate(top)]

for label, t_a in points:
    result = transition_quality(analysis_a, analysis_b, t_a, t_b, duration_a, duration_b)
    print(f"{label} : A à {t_a:.2f}s, B à {t_b:.2f}s -> total {result['total']}")
    print(f"   détail : {result['scores']}")