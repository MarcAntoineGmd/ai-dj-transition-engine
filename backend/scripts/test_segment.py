"""
Feature: Segment extraction manual test script
Purpose: Extract a known time range from a real audio file and export
         it, to manually verify the boundaries sound correct.
Main files: scripts/test_segment.py
How it works: take a file path, start and end times from the command
              line -> call extract_segment() -> report the resulting
              duration.
Concepts learned: validating audio slicing by checking both the
                   resulting duration and by ear.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import soundfile as sf

from app.transition.segment_extractor import extract_segment

if len(sys.argv) != 4:
    print("Usage: python scripts/test_segment.py <fichier_audio> <start> <end>")
    print("Exemple : python scripts/test_segment.py tmp_uploads/test.mp3 10 25")
    sys.exit(1)

audio_path = Path(sys.argv[1])
start = float(sys.argv[2])
end = float(sys.argv[3])

if not audio_path.exists():
    print(f"Fichier introuvable : {audio_path}")
    sys.exit(1)

output_path = audio_path.parent / f"{audio_path.stem}_segment_{start}_{end}.wav"

extract_segment(audio_path, start, end, output_path)
new_duration = sf.info(str(output_path)).duration

print(f"Segment extrait : {start}s - {end}s")
print(f"Durée attendue : {end - start}s")
print(f"Durée obtenue : {new_duration:.2f}s")
print(f"Fichier : {output_path.name}")