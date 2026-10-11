"""
Feature: Quality sub-score manual test script
Purpose: Verify bpm_score() and key_score() on hand-picked cases,
         including edge cases and the relative major/minor ambiguity.
Main files: scripts/test_quality_scorer.py
How it works: run both functions on fixed test pairs and print the
              results next to the expected values.
Concepts learned: testing pure scoring functions with known expected
                   outputs before combining them.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.transition.quality_scorer import bpm_score, key_score

print("--- bpm_score ---")
bpm_cases = [
    (124.0, 124.0, "~1.0 (aucun stretch)"),
    (124.0, 125.0, "~1.0 (écart négligeable)"),
    (124.0, 128.0, "~0.87"),
    (90.0, 140.0, "0.0 (hors limite)"),
]
for a, b, expected in bpm_cases:
    print(f"{a} vs {b} -> {bpm_score(a, b):.3f}  (attendu {expected})")

print("--- key_score ---")
key_cases = [
    ("F# major", "F# major", "1.0 (identique)"),
    ("F# major", "D# minor", "0.9 (relatives)"),
    ("C major", "G major", "0.8 (voisines, même mode)"),
    ("C major", "D minor", "0.5 (voisines, mode différent)"),
    ("C major", "F# major", "0.0 (opposées)"),
    ("B major", "A# major", "0.8 (bouclage 1 <-> 12 : 1B vs 6B ? à vérifier)"),
]
for a, b, expected in key_cases:
    print(f"{a} vs {b} -> {key_score(a, b):.2f}  (attendu {expected})")