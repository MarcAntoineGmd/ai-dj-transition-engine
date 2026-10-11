"""
Feature: Transition feature vector for machine learning
Purpose: Turn a candidate transition (song A at t_a into song B at t_b)
         into a fixed-length dictionary of numbers that a model can
         learn from.
Main files: app/ml/features.py
How it works: reuse the five rule-based sub-scores (beat, BPM, key,
              energy, spectral) and add four measurements they do not
              capture (local energy of each song, position in song A,
              available transition length).
Concepts learned: feature vectors, keeping the feature count small for
                   a small dataset, reusing rule-based scores as
                   features, a fixed column order shared by the dataset
                   and the model.
"""

from app.models.song_analysis import SongAnalysis
from app.transition.engine import TRANSITION_DURATION
from app.transition.quality_scorer import (
    ENERGY_WINDOW_SECONDS,
    beat_score,
    bpm_score,
    energy_score,
    key_score,
    local_energy,
    spectral_score,
)

# Canonical column order, shared by the dataset and the model
FEATURE_NAMES = [
    "beat",
    "bpm",
    "key",
    "energy",
    "spectral",
    "energy_a_local",
    "energy_b_local",
    "start_ratio_a",
    "transition_seconds",
]


def extract_transition_features(
    analysis_a: SongAnalysis,
    analysis_b: SongAnalysis,
    t_a: float,
    t_b: float,
    duration_a: float,
    duration_b: float,
) -> dict[str, float]:
    """
    Retourne le vecteur de caracteristiques (dict nomme, ordre FEATURE_NAMES)
    d'une transition partant de t_a dans A vers t_b dans B.
    """
    features = {
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
        "energy_a_local": local_energy(
            analysis_a.energy, t_a, duration_a, ENERGY_WINDOW_SECONDS
        ),
        "energy_b_local": local_energy(
            analysis_b.energy, t_b, duration_b, ENERGY_WINDOW_SECONDS
        ),
        "start_ratio_a": t_a / duration_a,
        "transition_seconds": min(
            TRANSITION_DURATION, duration_a - t_a, duration_b - t_b
        ),
    }
    return {name: float(features[name]) for name in FEATURE_NAMES}