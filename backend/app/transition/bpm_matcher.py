"""
Feature: BPM compatibility and matching module
Purpose: Decide how to reconcile two songs with different BPMs (leave
         unchanged, adjust one, or meet in the middle) and compute the
         required time-stretch factors, without altering any audio yet.
Main files: app/transition/bpm_matcher.py
How it works: compute the relative BPM difference -> if negligible,
              recommend no change -> otherwise target the average BPM
              and compute each song's required stretch factor -> flag
              if the factor exceeds a safety limit.
Concepts learned: time-stretching vs naive speed change, stretch ratio
                   calculation, documenting a safety limit as
                   provisional rather than absolute.
"""

NEGLIGIBLE_THRESHOLD = 0.02  # 2% : seuil de différence BPM à considérer comme négligeable
MAX_SAFE_STRETCH = 0.06  # ±6% : limite de départ à valider empiriquement


def match_bpm(bpm_a: float, bpm_b: float) -> dict:
    """
    Détermine la stratégie de compatibilité BPM entre deux morceaux.
    Retourne un dict décrivant la stratégie et les facteurs de stretch.
    """
    relative_diff = abs(bpm_a - bpm_b) / max(bpm_a, bpm_b)

    if relative_diff <= NEGLIGIBLE_THRESHOLD:
        return {
            "strategy": "none",
            "target_bpm": bpm_a,
            "stretch_factor_a": 1.0,
            "stretch_factor_b": 1.0,
            "within_safe_limit": True,
        }

    target_bpm = (bpm_a + bpm_b) / 2
    stretch_factor_a = target_bpm / bpm_a
    stretch_factor_b = target_bpm / bpm_b

    max_stretch_needed = max(
        abs(stretch_factor_a - 1.0), abs(stretch_factor_b - 1.0)
    )

    return {
        "strategy": "meet_in_middle",
        "target_bpm": round(target_bpm, 2),
        "stretch_factor_a": round(stretch_factor_a, 4),
        "stretch_factor_b": round(stretch_factor_b, 4),
        "within_safe_limit": max_stretch_needed <= MAX_SAFE_STRETCH,
    }