"""
Feature: Transition dataset builder
Purpose: Sample transitions between a collection of songs and export
         them as CSV rows (identifiers, feature vector, empty human
         rating) ready to be rated in Phase 9.
Main files: app/ml/dataset.py
How it works: analyze each song once -> repeatedly pick two different
              songs and one random valid start point -> extract the
              feature vector -> write all rows to a CSV file.
Concepts learned: random sampling versus top-ranked sampling (selection
                   bias), one row per transition fully describing how
                   to reproduce it, a stable column order.
"""

import csv
import random
from pathlib import Path

import soundfile as sf

from app.audio.analyzer import analyze_song
from app.ml.features import FEATURE_NAMES, extract_transition_features
from app.transition.selector import rank_transitions

AUDIO_EXTENSIONS = {".mp3", ".wav"}

COLUMNS = [
    "transition_id", "song_a", "song_b", "start_a", "start_b",
    *FEATURE_NAMES,
    "rating",
]


def list_songs(folder: Path) -> list[Path]:
    """Retourne les fichiers audio du dossier, tries par nom."""
    return sorted(p for p in folder.iterdir() if p.suffix.lower() in AUDIO_EXTENSIONS)


def build_rows(song_paths: list[Path], n_transitions: int, seed: int = 42) -> list[dict]:
    """
    Echantillonne jusqu'a n_transitions transitions entre morceaux
    differents. Chaque morceau n'est analyse qu'une fois.
    """
    rng = random.Random(seed)

    songs = {}
    for path in song_paths:
        print(f"Analyse de {path.name}...")
        songs[path.name] = (analyze_song(path, path.stem), sf.info(str(path)).duration)

    names = list(songs)
    rows = []
    seen = set()
    attempts = 0

    while len(rows) < n_transitions and attempts < n_transitions * 20:
        attempts += 1
        name_a, name_b = rng.sample(names, 2)
        analysis_a, duration_a = songs[name_a]
        analysis_b, duration_b = songs[name_b]

        candidates = rank_transitions(analysis_a, analysis_b, duration_a, duration_b)
        if not candidates:
            continue

        choice = rng.choice(candidates)
        key = (name_a, name_b, choice["start_a"])
        if key in seen:
            continue
        seen.add(key)

        features = extract_transition_features(
            analysis_a, analysis_b,
            choice["start_a"], choice["start_b"],
            duration_a, duration_b,
        )
        rows.append({
            "transition_id": f"t{len(rows) + 1:04d}",
            "song_a": name_a,
            "song_b": name_b,
            "start_a": choice["start_a"],
            "start_b": choice["start_b"],
            **features,
            "rating": "",
        })

    return rows


def write_csv(rows: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {k: round(v, 6) if isinstance(v, float) else v for k, v in row.items()}
            )