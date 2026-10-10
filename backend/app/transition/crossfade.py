"""
Feature: Equal-power crossfade module
Purpose: Blend two audio segments (the end of song A, the start of song
         B) into a single smooth transition using an equal-power fade
         curve.
Main files: app/transition/crossfade.py
How it works: truncate both segments to the same length -> build a
              quarter-cosine fade-out curve for A and fade-in curve for
              B -> sum the two weighted signals.
Concepts learned: linear vs equal-power crossfade curves, why summing
                   two NumPy arrays requires matching lengths.
"""

import numpy as np


def crossfade(segment_a: np.ndarray, segment_b: np.ndarray) -> np.ndarray:
    """
    Combine segment_a (fade-out) et segment_b (fade-in) en un crossfade
    equal-power. Les deux segments sont tronqués à la longueur du plus
    court avant combinaison.
    """
    length = min(len(segment_a), len(segment_b))
    a = segment_a[:length]
    b = segment_b[:length]

    t = np.linspace(0, np.pi / 2, length)
    fade_out = np.cos(t)
    fade_in = np.sin(t)

    return a * fade_out + b * fade_in