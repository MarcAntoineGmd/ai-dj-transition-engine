"""
Feature: Transition candidate point generator
Purpose: Generate a shortlist of plausible transition timestamps from a
         song's detected beats, rather than treating every single beat
         as a candidate.
Main files: app/transition/candidate_generator.py
How it works: take every Nth beat (approximating one candidate per
              musical bar) and discard candidates too close to the
              start or end of the song.
Concepts learned: beat vs downbeat, why naive "one candidate per beat"
                   is wasteful, safety margins for transition duration.
"""

BEATS_PER_BAR = 4  # hypothèse simplificatrice : mesures à 4 temps
MIN_MARGIN_SECONDS = 8.0  # marge minimale au début/fin du morceau


def generate_candidates(
    beat_times: list[float],
    duration: float,
    beats_per_bar: int = BEATS_PER_BAR,
    min_margin: float = MIN_MARGIN_SECONDS,
) -> list[float]:
    """
    Retourne une liste de timestamps candidats pour une transition,
    en prenant un beat tous les `beats_per_bar`, et en excluant ceux
    trop proches du début/de la fin du morceau.
    """
    bar_starts = beat_times[::beats_per_bar]

    candidates = [
        t for t in bar_starts
        if min_margin <= t <= (duration - min_margin)
    ]

    return candidates