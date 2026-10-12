"""
Feature: Rating clip generation script
Purpose: Generate the audio clip of every transition in the dataset CSV
         so it can be rated by listeners.
Main files: scripts/generate_clips.py
How it works: parse the options -> call generate_clips() -> print a
              summary and the clips worth listening to for distortion.
Concepts learned: running a long batch job that can be stopped and
                   restarted without redoing finished work.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ml.clips import generate_clips

ML_DIR = Path(__file__).resolve().parents[2] / "ml"

parser = argparse.ArgumentParser(description="Genere les clips audio des transitions a noter.")
parser.add_argument("songs_folder", type=Path, help="dossier contenant les morceaux du CSV")
parser.add_argument("--csv", type=Path, default=ML_DIR / "data" / "transitions.csv")
parser.add_argument("--clips-dir", type=Path, default=ML_DIR / "data" / "clips")
args = parser.parse_args()

if not args.songs_folder.is_dir():
    print(f"Dossier introuvable : {args.songs_folder}")
    sys.exit(1)
if not args.csv.exists():
    print(f"CSV introuvable : {args.csv}")
    sys.exit(1)

summary = generate_clips(args.csv, args.songs_folder, args.clips_dir)
print(f"{summary['generated']} clips generes, {summary['skipped']} deja presents")
if summary["possibly_clipped"]:
    print("Pic proche de la saturation (a ecouter) : " + ", ".join(summary["possibly_clipped"]))