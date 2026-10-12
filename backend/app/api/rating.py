"""
Feature: Rating collection endpoints
Purpose: Serve transition audio clips to human raters one at a time and
         record their 1 to 5 ratings in a CSV file (Phase 9).
Main files: app/api/rating.py, app/models/rating.py
How it works: list the available clips -> serve a random clip the rater
              has not rated yet (blind: no scores or song names) ->
              append each rating to an append-only CSV, last rating
              wins.
Concepts learned: blind data collection, append-only storage, input
                   validation on identifiers, environment variables for
                   configuration, locking concurrent writes.
"""

import csv
import os
import random
import re
import threading
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.models.rating import NextClip, RATER_PATTERN, RatingProgress, RatingRequest

router = APIRouter()

_ML_DATA = Path(__file__).resolve().parents[3] / "ml" / "data"
CLIPS_DIR = Path(os.environ.get("CLIPS_DIR", _ML_DATA / "clips"))
RATINGS_FILE = Path(os.environ.get("RATINGS_FILE", _ML_DATA / "ratings.csv"))

RATING_COLUMNS = ["transition_id", "rater", "rating", "timestamp"]
_ID_PATTERN = re.compile(r"t\d+")
_write_lock = threading.Lock()


def _clip_ids() -> list[str]:
    return sorted(p.stem for p in CLIPS_DIR.glob("*.wav") if _ID_PATTERN.fullmatch(p.stem))


def _rated_ids(rater: str) -> set[str]:
    if not RATINGS_FILE.exists():
        return set()
    with RATINGS_FILE.open(newline="", encoding="utf-8") as f:
        return {row["transition_id"] for row in csv.DictReader(f) if row["rater"] == rater}


def _progress(rater: str) -> RatingProgress:
    ids = set(_clip_ids())
    return RatingProgress(rated=len(_rated_ids(rater) & ids), total=len(ids))


@router.get("/next", response_model=NextClip)
def next_clip(rater: str = Query(min_length=1, max_length=40, pattern=RATER_PATTERN)):
    rater = rater.lower()
    ids = _clip_ids()
    rated = _rated_ids(rater)
    remaining = [i for i in ids if i not in rated]
    return NextClip(
        transition_id=random.choice(remaining) if remaining else None,
        rated=len(rated & set(ids)),
        total=len(ids),
    )


@router.get("/clip/{transition_id}")
def get_clip(transition_id: str):
    if not _ID_PATTERN.fullmatch(transition_id):
        raise HTTPException(status_code=400, detail="Identifiant invalide")
    path = CLIPS_DIR / f"{transition_id}.wav"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Clip introuvable")
    return FileResponse(path, media_type="audio/wav")


@router.post("", response_model=RatingProgress)
def submit_rating(request: RatingRequest):
    if request.transition_id not in _clip_ids():
        raise HTTPException(status_code=404, detail="Clip introuvable")

    rater = request.rater.lower()
    row = {
        "transition_id": request.transition_id,
        "rater": rater,
        "rating": request.rating,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    with _write_lock:
        RATINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        is_new = not RATINGS_FILE.exists()
        with RATINGS_FILE.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=RATING_COLUMNS)
            if is_new:
                writer.writeheader()
            writer.writerow(row)

    return _progress(rater)