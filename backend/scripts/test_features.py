"""
Feature: Transition feature vector manual test script
Purpose: Print the feature vector of the best-ranked transitions between
         two real songs and check it is complete, finite and consistent
         with the rule-based energy score.
Main files: scripts/test_features.py
How it works: analyze both songs -> take the top 3 ranked transitions ->
              extract and print their features -> run basic checks.
Concepts learned: sanity-checking features before building a dataset on
                   top of them.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import soundfile as sf

from app.audio.analyzer import analyze_song
from app.ml.features import FEATURE_NAMES, extract_transition_features
from app.transition.selector import rank_transitions

if len(sys.argv) != 3:
    print("Usage: python scripts/test_features.py <song_a> <song_b>")
    sys.exit(1)

song_a = Path(sys.argv[1])
song_b = Path(sys.argv[2])

analysis_a = analyze_song(song_a, "a")
analysis_b = analyze_song(song_b, "b")
duration_a = sf.info(str(song_a)).duration
duration_b = sf.info(str(song_b)).duration

ranking = rank_transitions(analysis_a, analysis_b, duration_a, duration_b)
if not ranking:
    print("Aucun candidat.")
    sys.exit(0)

for r in ranking[:3]:
    features = extract_transition_features(
        analysis_a, analysis_b, r["start_a"], r["start_b"], duration_a, duration_b
    )
    assert list(features) == FEATURE_NAMES, "ordre ou noms de colonnes incorrects"
    assert all(math.isfinite(v) for v in features.values()), "valeur non finie"

    print(f"A a {r['start_a']}s (total regles : {r['total']})")
    for name, value in features.items():
        print(f"   {name}: {value:.3f}")
    gap = abs(features["energy_a_local"] - features["energy_b_local"])
    print(f"   verif : 1 - energy = {1 - features['energy']:.3f}, |a - b| = {gap:.3f}")

print("OK : vecteurs complets et finis")