"""
Feature: Transition candidate data model
Purpose: Define the structure of a single scored transition candidate,
         so FastAPI can validate and document the suggestion endpoint's
         response.
Main files: app/models/transition.py
How it works: a Pydantic BaseModel with a timestamp and its score.
Concepts learned: reusing the Pydantic modeling pattern established for
                   SongAnalysis.
"""

from pydantic import BaseModel


class TransitionCandidate(BaseModel):
    timestamp: float
    score: float

class BpmMatchRequest(BaseModel):
    file_id_a: str
    file_id_b: str

class BpmMatchResult(BaseModel):
    strategy: str
    target_bpm: float
    stretch_factor_a: float
    stretch_factor_b: float
    within_safe_limit: bool