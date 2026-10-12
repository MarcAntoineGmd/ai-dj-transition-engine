"""
Feature: Rating clip generator
Purpose: Render the audio clip of each transition listed in the dataset
         CSV, named after its transition id, so humans can listen to it
         and rate it in Phase 9.
Main files: app/ml/clips.py
How it works: read the CSV rows -> for each one without a clip yet, run
              the transition engine in a temporary folder with the row's
              songs and start point -> move the result to
              <clips_dir>/<transition_id>.wav -> flag clips whose peak
              is close to full scale.
Concepts learned: reproducing a transition from a dataset row, resumable
                   batch jobs, temporary directories, detecting possible
                   clipping from a clip's peak level.
"""

import csv
import shutil
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

from app.transition.engine import generate_transition

FULL_SCALE = 0.999
MAX_FULL_SCALE_FRACTION = 1e-5  # 0.001 % of samples, calibrated on the test clips

def generate_clips(csv_path: Path, songs_folder: Path, clips_dir: Path) -> dict:
    """
    Genere le clip audio de chaque transition du CSV (ignore ceux deja
    generes). Retourne un resume : generes, deja presents, suspects.
    """
    clips_dir.mkdir(parents=True, exist_ok=True)

    with csv_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    summary = {"generated": 0, "skipped": 0, "possibly_clipped": []}

    for row in rows:
        target = clips_dir / f"{row['transition_id']}.wav"
        if target.exists():
            summary["skipped"] += 1
            continue

        with tempfile.TemporaryDirectory() as tmp:
            produced = generate_transition(
                songs_folder / row["song_a"],
                songs_folder / row["song_b"],
                Path(tmp),
                float(row["start_a"]),
            )
            shutil.move(str(produced), str(target))

        data = sf.read(str(target))[0]
        if float(np.mean(np.abs(data) >= FULL_SCALE)) > MAX_FULL_SCALE_FRACTION:
            summary["possibly_clipped"].append(row["transition_id"])

        summary["generated"] += 1
        print(f"{row['transition_id']} : {row['song_a']} -> {row['song_b']} a {row['start_a']}s")

    return summary