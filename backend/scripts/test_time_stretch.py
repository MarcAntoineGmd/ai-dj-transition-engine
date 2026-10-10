"""
Feature: Time-stretching manual test script
Purpose: Apply a known stretch factor to a real audio file and export
         it, to manually verify the result sounds correct (speed
         changed, pitch unchanged, no major artifacts).
Main files: scripts/test_time_stretch.py
How it works: take a file path and a factor from the command line ->
              call stretch_audio() -> report before/after duration.
Concepts learned: validating a DSP transformation by ear, not just by
                   checking that the code runs without error.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import soundfile as sf

from app.transition.time_stretcher import stretch_audio

if len(sys.argv) != 3:
    print("Usage: python scripts/test_time_stretch.py <fichier_audio> <facteur>")
    print("Exemple : python scripts/test_time_stretch.py tmp_uploads/test.mp3 1.1")
    sys.exit(1)

audio_path = Path(sys.argv[1])
factor = float(sys.argv[2])

if not audio_path.exists():
    print(f"Fichier introuvable : {audio_path}")
    sys.exit(1)

output_path = audio_path.parent / f"{audio_path.stem}_stretched_{factor}.wav"

original_duration = sf.info(str(audio_path)).duration
stretch_audio(audio_path, factor, output_path)
new_duration = sf.info(str(output_path)).duration

print(f"Fichier original : {audio_path.name} ({original_duration:.2f}s)")
print(f"Facteur appliqué : {factor}")
print(f"Fichier stretché : {output_path.name} ({new_duration:.2f}s)")
print(f"Durée attendue : {original_duration / factor:.2f}s")