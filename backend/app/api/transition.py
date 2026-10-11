"""
Feature: Transition endpoints
Purpose: Expose the transition pipeline over HTTP: candidate suggestion,
         BPM matching, ranking of full transitions between two songs,
         and audio generation.
Main files: app/api/transition.py
How it works: locate uploaded files by id -> call the analysis, scoring
              and engine modules -> return JSON (suggest, bpm-match,
              rank) or a .wav file (generate).
Concepts learned: reusing existing modules behind several routes,
                   JSON vs FileResponse, optional request fields that
                   keep earlier behavior unchanged.
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
from app.audio.analyzer import analyze_song
from app.transition.selector import rank_transitions
from app.models.transition import RankedTransition, TransitionRankRequest

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

    output_path = generate_transition(file_a, file_b, UPLOAD_DIR, request.start_a)

    return FileResponse(
        path=output_path,
        media_type="audio/wav",
        filename=output_path.name,
    )

@router.post("/rank", response_model=list[RankedTransition])
async def rank(request: TransitionRankRequest):
    file_a = _find_file(request.file_id_a)
    file_b = _find_file(request.file_id_b)

    analysis_a = analyze_song(file_a, request.file_id_a)
    analysis_b = analyze_song(file_b, request.file_id_b)
    duration_a = sf.info(str(file_a)).duration
    duration_b = sf.info(str(file_b)).duration

    return rank_transitions(analysis_a, analysis_b, duration_a, duration_b)