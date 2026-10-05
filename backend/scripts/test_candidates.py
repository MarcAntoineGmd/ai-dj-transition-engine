"""
Feature: Transition candidate generation manual test script
Purpose: Verify that generate_candidates() produces a sane, reasonably
         sized list of candidate timestamps for a real audio file.
Main files: scripts/test_candidates.py
How it works: take a file path from the command line -> run beat
              detection -> run candidate generation -> print the
              results.
Concepts learned: isolating business logic from a throwaway CLI script.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import soundfile as sf

from app.audio.beat_tracker import detect_beats
from app.transition.candidate_generator import generate_candidates
from app.audio.feature_extractor import extract_features
from app.transition.scorer import score_candidates

if len(sys.argv) != 2:
    print("Usage: python scripts/test_candidates.py <chemin_vers_fichier_audio>")
    sys.exit(1)

audio_path = Path(sys.argv[1])
if not audio_path.exists():
    print(f"Fichier introuvable : {audio_path}")
    sys.exit(1)

bpm, beat_times = detect_beats(audio_path)
duration = sf.info(str(audio_path)).duration
candidates = generate_candidates(beat_times, duration)
features = extract_features(audio_path)
scored = score_candidates(candidates, features["energy"], duration)

print(f"Fichier : {audio_path.name}")
print(f"Durée : {duration:.1f}s")
print(f"Nombre de beats : {len(beat_times)}")
print(f"Nombre de candidats générés : {len(candidates)}")
print("Top 5 candidats (triés par score) :")
for c in scored[:5]:
    print(f"  {c['timestamp']:.2f}s — score {c['score']}")