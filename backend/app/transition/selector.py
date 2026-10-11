"""
Feature: Transition candidate ranking
Purpose: Rank the plausible start points in song A by the composite
         quality of a transition into the start of song B, so the best
         one can be chosen automatically.
Main files: app/transition/selector.py
How it works: generate beat-aligned candidates in A -> keep those in the
              final third that leave room for a full transition ->
              score each against the first beat of B -> sort by
              composite score.
Concepts learned: pre-filtering candidates with a documented heuristic
                   before scoring, reusing existing modules instead of
                   duplicating their logic.
"""

from app.models.song_analysis import SongAnalysis
from app.transition.candidate_generator import generate_candidates
from app.transition.engine import TRANSITION_DURATION
from app.transition.quality_scorer import transition_quality

LATE_SECTION_RATIO = 1 / 3  # on ne considère que le dernier tiers de A
MIN_ROOM_RATIO = 0.9  # on accepte une transition d'au moins 90 % de la durée cible


def rank_transitions(
    analysis_a: SongAnalysis,
    analysis_b: SongAnalysis,
    duration_a: float,
    duration_b: float,
) -> list[dict]:
    """
    Retourne les transitions candidates (départ dans A, arrivée au premier
    beat de B) triées du meilleur au pire score composite.
    """
    if not analysis_a.beat_times or not analysis_b.beat_times:
        return []

    start_b = analysis_b.beat_times[0]
    earliest_a = duration_a * (1 - LATE_SECTION_RATIO)

    candidates = generate_candidates(
        analysis_a.beat_times,
        duration_a,
        min_margin=TRANSITION_DURATION * MIN_ROOM_RATIO,
    )

    ranked = []
    for start_a in candidates:
        if start_a < earliest_a:
            continue
        result = transition_quality(
            analysis_a, analysis_b, start_a, start_b, duration_a, duration_b
        )
        ranked.append({
            "start_a": round(start_a, 2),
            "start_b": round(start_b, 2),
            "total": result["total"],
            "scores": result["scores"],
        })

    return sorted(ranked, key=lambda r: r["total"], reverse=True)