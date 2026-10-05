"""
Feature: Transition suggestion endpoint
Purpose: Expose the candidate generation and scoring pipeline over
         HTTP, returning the best transition points for a given
         uploaded song.
Main files: app/api/transition.py
How it works: locate the uploaded file by id -> run beat detection and
              feature extraction -> generate candidates -> score and
              sort them -> return as a list of TransitionCandidate.
Concepts learned: reusing existing analysis modules behind a new route
                   rather than duplicating logic.
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException
import soundfile as sf

from app.audio.beat_tracker import detect_beats
from app.audio.feature_extractor import extract_features
from app.transition.candidate_generator import generate_candidates
from app.transition.scorer import score_candidates
from app.models.transition import TransitionCandidate

router = APIRouter()

UPLOAD_DIR = Path("tmp_uploads")


@router.post("/suggest/{file_id}", response_model=list[TransitionCandidate])
async def suggest_transitions(file_id: str):
    matches = list(UPLOAD_DIR.glob(f"{file_id}.*"))
    if not matches:
        raise HTTPException(status_code=404, detail="Fichier introuvable")

    file_path = matches[0]
    duration = sf.info(str(file_path)).duration

    _, beat_times = detect_beats(file_path)
    features = extract_features(file_path)

    candidates = generate_candidates(beat_times, duration)
    scored = score_candidates(candidates, features["energy"], duration)

    return scored