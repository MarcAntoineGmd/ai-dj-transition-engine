"""
Feature: BPM matching manual test script
Purpose: Verify match_bpm() behaves sensibly across a range of BPM pairs,
         including edge cases (identical BPM, small gap, large gap).
Main files: scripts/test_bpm_matching.py
How it works: run match_bpm() on a fixed set of test pairs and print
              the resulting strategy for each.
Concepts learned: testing a pure function with hand-picked edge cases
                   before wiring it into the API.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.transition.bpm_matcher import match_bpm

test_pairs = [
    (124.0, 124.0), # identique
    (124.0, 125.0), # écart négligeable
    (124.0, 128.0), # écart modéré (cas Phase 5 du plan original)
    (90.0, 140.0), # écart énorme, hors limite de sécurité attendue
    (92.29, 92.29), # BPM réel du fichier de test, identique
]

for bpm_a, bpm_b in test_pairs:
    result = match_bpm(bpm_a, bpm_b)
    print(f"{bpm_a} BPM vs {bpm_b} BPM -> {result}")