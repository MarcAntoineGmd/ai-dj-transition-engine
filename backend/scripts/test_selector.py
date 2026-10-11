"""
Feature: Transition ranking manual test script
Purpose: Rank all candidate transitions between two real songs and
         print the best ones, to check the ranking is sensible.
Main files: scripts/test_selector.py
How it works: analyze both songs -> rank_transitions() -> print the
              count, the top 5 and the worst candidate.
Concepts learned: validating a selection step by inspecting both ends
                   of the ranking, not only the winner.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import soundfile as sf

from app.audio.analyzer import analyze_song
from app.transition.selector import rank_transitions

if len(sys.argv) != 3:
    print("Usage: python scripts/test_selector.py <song_a> <song_b>")
    sys.exit(1)

song_a = Path(sys.argv[1])
song_b = Path(sys.argv[2])

analysis_a = analyze_song(song_a, "a")
analysis_b = analyze_song(song_b, "b")
duration_a = sf.info(str(song_a)).duration
duration_b = sf.info(str(song_b)).duration

ranking = rank_transitions(analysis_a, analysis_b, duration_a, duration_b)

if not ranking:
    print("Aucun candidat (morceau trop court ou aucun beat détecté).")
    sys.exit(0)

print(f"{len(ranking)} transitions candidates évaluées")
print("Top 5 :")
for r in ranking[:5]:
    print(f"  A à {r['start_a']}s -> total {r['total']}  {r['scores']}")
worst = ranking[-1]
print(f"Pire : A à {worst['start_a']}s -> total {worst['total']}  {worst['scores']}")