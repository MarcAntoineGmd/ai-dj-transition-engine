"""
Feature: Dataset generation script
Purpose: Build the CSV of sampled transitions to be rated by humans,
         from a local folder of songs.
Main files: scripts/build_dataset.py
How it works: parse the command-line options -> refuse to overwrite an
              existing file unless --force -> build and write the rows.
Concepts learned: argparse for a script with several options, protecting
                   a file that will later contain human work.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ml.dataset import build_rows, list_songs, write_csv

DEFAULT_OUTPUT = Path(__file__).resolve().parents[2] / "ml" / "data" / "transitions.csv"

parser = argparse.ArgumentParser(description="Genere un jeu de donnees de transitions a noter.")
parser.add_argument("songs_folder", type=Path, help="dossier contenant les morceaux (.mp3/.wav)")
parser.add_argument("-n", "--count", type=int, default=100, help="nombre de transitions voulues")
parser.add_argument("--seed", type=int, default=42, help="graine aleatoire (reproductibilite)")
parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="fichier CSV de sortie")
parser.add_argument("--force", action="store_true", help="ecrase le fichier existant (efface les notes)")
args = parser.parse_args()

if not args.songs_folder.is_dir():
    print(f"Dossier introuvable : {args.songs_folder}")
    sys.exit(1)

if args.output.exists() and not args.force:
    print(f"{args.output} existe deja. Il contiendra des notes : utilise --force pour l'ecraser.")
    sys.exit(1)

songs = list_songs(args.songs_folder)
if len(songs) < 2:
    print("Il faut au moins 2 morceaux.")
    sys.exit(1)

rows = build_rows(songs, args.count, args.seed)
write_csv(rows, args.output)
print(f"{len(rows)} transitions ecrites dans {args.output} ({len(songs)} morceaux)")