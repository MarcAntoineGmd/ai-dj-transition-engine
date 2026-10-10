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
from app.transition.bpm_matcher import match_bpm
from app.models.transition import BpmMatchRequest, BpmMatchResult

from fastapi.responses import FileResponse

from app.transition.engine import generate_transition
from app.models.transition import TransitionGenerateRequest

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

def _find_file(file_id: str) -> Path:
    matches = list(UPLOAD_DIR.glob(f"{file_id}.*"))
    if not matches:
        raise HTTPException(status_code=404, detail=f"Fichier introuvable : {file_id}")
    return matches[0]


@router.post("/bpm-match", response_model=BpmMatchResult)
async def bpm_match(request: BpmMatchRequest):
    file_a = _find_file(request.file_id_a)
    file_b = _find_file(request.file_id_b)

    bpm_a, _ = detect_beats(file_a)
    bpm_b, _ = detect_beats(file_b)

    return match_bpm(bpm_a, bpm_b)

@router.post("/generate")
async def generate(request: TransitionGenerateRequest):
    file_a = _find_file(request.file_id_a)
    file_b = _find_file(request.file_id_b)

    output_path = generate_transition(file_a, file_b, UPLOAD_DIR)

    return FileResponse(
        path=output_path,
        media_type="audio/wav",
        filename=output_path.name,
    )