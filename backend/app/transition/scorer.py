"""
Feature: Transition candidate scoring module
Purpose: Score each candidate transition point using simple, explainable
         criteria (energy compatibility, position in the song) and rank
         them from best to worst.
Main files: app/transition/scorer.py
How it works: convert each candidate timestamp to its corresponding
              energy-array index, score low-energy points higher, add a
              mild bonus for candidates in the later part of the song,
              then combine both into a single normalized score.
Concepts learned: normalizing heterogeneous scores to a common 0-1
                   scale before combining them, converting a timestamp
                   into a frame index.
"""


def _energy_score(energy: list[float], timestamp: float, duration: float) -> float:
    """
    Score élevé pour une énergie basse à ce timestamp (1.0 = énergie minimale
    du morceau, 0.0 = énergie maximale).
    """
    if not energy:
        return 0.5

    index = int((timestamp / duration) * len(energy))
    index = min(index, len(energy) - 1)

    value = energy[index]
    min_energy = min(energy)
    max_energy = max(energy)

    if max_energy == min_energy:
        return 0.5

    normalized = (value - min_energy) / (max_energy - min_energy)
    return 1.0 - normalized


def _structure_score(timestamp: float, duration: float) -> float:
    """
    Légère préférence pour les candidats situés dans le dernier tiers
    du morceau (hypothèse simplificatrice : refrains/breaks plus
    fréquents vers la fin).
    """
    position_ratio = timestamp / duration
    return min(position_ratio * 1.5, 1.0)


def score_candidates(
    candidates: list[float],
    energy: list[float],
    duration: float,
) -> list[dict]:
    """
    Retourne une liste de dicts {timestamp, score}, triée du meilleur
    au pire score.
    """
    scored = []

    for timestamp in candidates:
        energy_score = _energy_score(energy, timestamp, duration)
        structure_score = _structure_score(timestamp, duration)

        final_score = 0.6 * energy_score + 0.4 * structure_score

        scored.append({"timestamp": timestamp, "score": round(final_score, 3)})

    return sorted(scored, key=lambda c: c["score"], reverse=True)