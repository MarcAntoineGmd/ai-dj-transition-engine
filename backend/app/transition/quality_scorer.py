"""
Feature: Transition quality scoring (sub-scores and composite)
Purpose: Measure how good a transition between two songs would be, using
         explainable 0-1 sub-scores (beat, BPM, key, energy, spectral)
         combined into one weighted composite score.
Main files: app/transition/quality_scorer.py
How it works: each sub-score is a pure function normalized to [0, 1];
              transition_quality() combines them with experimental
              weights and returns both the total and the breakdown.
Concepts learned: Camelot wheel and circular distance, beat-grid
                   regularity via coefficient of variation, weighted
                   score composition, documenting weights as provisional.
"""

import statistics

from app.models.song_analysis import SongAnalysis, SpectralFeatures
from app.transition.bpm_matcher import MAX_SAFE_STRETCH, match_bpm

# Poids expérimentaux (plan original, section 13) : à tester et documenter
WEIGHTS = {
    "beat": 0.30,
    "bpm": 0.20,
    "key": 0.15,
    "energy": 0.20,
    "spectral": 0.15,
}

ENERGY_WINDOW_SECONDS = 15.0  # même durée que la transition générée
BEAT_WINDOW_COUNT = 8  # nombre de beats voisins examinés
MAX_BEAT_CV = 0.15  # coefficient de variation où le score de beat tombe à 0

# Notes en notation dièse, cohérente avec key_detector.py
_MAJOR_TO_CAMELOT = {
    "B": 1, "F#": 2, "C#": 3, "G#": 4, "D#": 5, "A#": 6,
    "F": 7, "C": 8, "G": 9, "D": 10, "A": 11, "E": 12,
}
_MINOR_TO_CAMELOT = {
    "G#": 1, "D#": 2, "A#": 3, "F": 4, "C": 5, "G": 6,
    "D": 7, "A": 8, "E": 9, "B": 10, "F#": 11, "C#": 12,
}


def _to_camelot(key: str) -> tuple[int, str]:
    """Convertit "F# major" en (2, "B"), "D# minor" en (2, "A")."""
    note, mode = key.split()
    if mode == "major":
        return _MAJOR_TO_CAMELOT[note], "B"
    return _MINOR_TO_CAMELOT[note], "A"


def bpm_score(bpm_a: float, bpm_b: float) -> float:
    """
    1.0 si aucun stretch n'est nécessaire, décroît linéairement avec le
    stretch maximal requis, et atteint 0.0 à deux fois la limite de
    sécurité (soit 12%).
    """
    match = match_bpm(bpm_a, bpm_b)
    max_stretch = max(
        abs(match["stretch_factor_a"] - 1.0),
        abs(match["stretch_factor_b"] - 1.0),
    )
    return max(0.0, 1.0 - max_stretch / (2 * MAX_SAFE_STRETCH))


def key_score(key_a: str, key_b: str) -> float:
    """
    Compatibilité harmonique via la roue de Camelot.
    Même tonalité : 1.0 | relatives (même numéro) : 0.9
    Voisines même mode : 0.8 | voisines mode différent : 0.5
    Au-delà : décroît de 0.4 (distance 2) jusqu'à 0.0 (distance 6).
    """
    number_a, letter_a = _to_camelot(key_a)
    number_b, letter_b = _to_camelot(key_b)

    distance = min((number_a - number_b) % 12, (number_b - number_a) % 12)
    same_mode = letter_a == letter_b

    if distance == 0:
        return 1.0 if same_mode else 0.9
    if distance == 1:
        return 0.8 if same_mode else 0.5
    return max(0.0, 0.4 - 0.1 * (distance - 2))


def local_energy(
    energy: list[float], timestamp: float, duration: float, window: float
) -> float:
    """Énergie moyenne sur [timestamp, timestamp + window], normalisée par le max du morceau."""
    if not energy or duration <= 0 or max(energy) == 0:
        return 0.0

    n = len(energy)
    start = min(int(timestamp / duration * n), n - 1)
    end_time = min(timestamp + window, duration)
    end = min(max(int(end_time / duration * n), start + 1), n)

    segment = energy[start:end]
    return (sum(segment) / len(segment)) / max(energy)


def energy_score(
    energy_a: list[float], t_a: float, duration_a: float,
    energy_b: list[float], t_b: float, duration_b: float,
) -> float:
    """1.0 si l'intensité relative des deux morceaux est identique sur la fenêtre de transition."""
    local_a = local_energy(energy_a, t_a, duration_a, ENERGY_WINDOW_SECONDS)
    local_b = local_energy(energy_b, t_b, duration_b, ENERGY_WINDOW_SECONDS)
    return 1.0 - abs(local_a - local_b)


def _relative_similarity(x: float, y: float) -> float:
    if max(x, y) == 0:
        return 1.0
    return 1.0 - abs(x - y) / max(x, y)


def spectral_score(features_a: SpectralFeatures, features_b: SpectralFeatures) -> float:
    """
    Similarité de timbre global : moyenne des similarités relatives du
    centroid et de la bandwidth (valeurs moyennes sur tout le morceau).
    """
    centroid = _relative_similarity(
        features_a.spectral_centroid_mean, features_b.spectral_centroid_mean
    )
    bandwidth = _relative_similarity(
        features_a.spectral_bandwidth_mean, features_b.spectral_bandwidth_mean
    )
    return (centroid + bandwidth) / 2


def _beat_regularity(beat_times: list[float], timestamp: float) -> float:
    """
    Régularité de la grille de beats autour de timestamp : 1.0 si les
    intervalles entre beats voisins sont constants, 0.0 si très instables.
    """
    if len(beat_times) < 3:
        return 0.0

    nearest = sorted(sorted(beat_times, key=lambda t: abs(t - timestamp))[:BEAT_WINDOW_COUNT])
    intervals = [b - a for a, b in zip(nearest, nearest[1:])]

    mean_interval = statistics.mean(intervals)
    if mean_interval <= 0:
        return 0.0

    cv = statistics.pstdev(intervals) / mean_interval
    return max(0.0, 1.0 - cv / MAX_BEAT_CV)


def beat_score(
    beat_times_a: list[float], t_a: float,
    beat_times_b: list[float], t_b: float,
) -> float:
    """Une transition n'est aussi fiable que sa grille la plus instable : on prend le minimum."""
    return min(_beat_regularity(beat_times_a, t_a), _beat_regularity(beat_times_b, t_b))


def transition_quality(
    analysis_a: SongAnalysis, analysis_b: SongAnalysis,
    t_a: float, t_b: float,
    duration_a: float, duration_b: float,
) -> dict:
    """Score composite pondéré d'une transition partant de t_a (A) vers t_b (B), avec le détail."""
    scores = {
        "beat": beat_score(analysis_a.beat_times, t_a, analysis_b.beat_times, t_b),
        "bpm": bpm_score(analysis_a.bpm, analysis_b.bpm),
        "key": key_score(analysis_a.key, analysis_b.key),
        "energy": energy_score(
            analysis_a.energy, t_a, duration_a,
            analysis_b.energy, t_b, duration_b,
        ),
        "spectral": spectral_score(
            analysis_a.spectral_features, analysis_b.spectral_features
        ),
    }
    total = sum(WEIGHTS[name] * value for name, value in scores.items())

    return {
        "total": round(total, 3),
        "scores": {name: round(value, 3) for name, value in scores.items()},
    }