"""
Feature: BPM detection manual test script
Purpose: Quickly verify that app.audio.beat_tracker produces sane BPM
         and beat results on a real audio file, outside the API.
Main files: scripts/test_bpm.py
How it works: take a file path from the command line -> call
              detect_beats() -> print the results.
Concepts learned: isolating business logic from a throwaway CLI script.
"""

import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))  # pour importer "app"

from app.audio.beat_tracker import detect_beats
from app.audio.feature_extractor import extract_features

if len(sys.argv) != 2:
    print("Usage: python scripts/test_bpm.py <chemin_vers_fichier_audio>")
    sys.exit(1)

audio_path = Path(sys.argv[1])
if not audio_path.exists():
    print(f"Fichier introuvable : {audio_path}")
    sys.exit(1)

bpm, beat_times = detect_beats(audio_path)
features = extract_features(audio_path)

print(f"Fichier : {audio_path.name}")
print(f"BPM estimé : {bpm:.2f}")
print(f"Nombre de beats détectés : {len(beat_times)}")
print(f"5 premiers beats (secondes) : {beat_times[:5]}")
print(f"Centroid spectral moyen : {features['spectral_centroid_mean']:.1f} Hz")
print(f"Bandwidth spectral moyen : {features['spectral_bandwidth_mean']:.1f} Hz")
print(f"Énergie (RMS) — min/max/moyenne : {min(features['energy']):.4f} / {max(features['energy']):.4f} / {np.mean(features['energy']):.4f}")
print(f"Chroma moyen (12 valeurs) : {[round(v, 3) for v in features['chroma_mean']]}")
print(f"MFCC moyen (13 valeurs) : {[round(v, 2) for v in features['mfcc_mean']]}")