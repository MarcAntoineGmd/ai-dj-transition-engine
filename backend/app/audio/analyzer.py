"""
Feature: Song analysis orchestrator
Purpose: Run beat detection, feature extraction and key detection on an
         audio file, and assemble the results into a single SongAnalysis
         object.
Main files: app/audio/analyzer.py
How it works: call detect_beats(), extract_features() and detect_key()
              on the same file, then combine their outputs into one
              SongAnalysis instance.
Concepts learned: orchestration pattern (one function coordinating
                   several independent modules).
"""

from pathlib import Path

from app.audio.beat_tracker import detect_beats
from app.audio.feature_extractor import extract_features
from app.audio.key_detector import detect_key
from app.models.song_analysis import SongAnalysis, SpectralFeatures


def analyze_song(file_path: str | Path, song_id: str) -> SongAnalysis:
    bpm, beat_times = detect_beats(file_path)
    features = extract_features(file_path)
    key = detect_key(file_path)

    return SongAnalysis(
        id=song_id,
        bpm=bpm,
        key=key,
        beat_times=beat_times,
        energy=features["energy"],
        spectral_features=SpectralFeatures(
            spectral_centroid_mean=features["spectral_centroid_mean"],
            spectral_bandwidth_mean=features["spectral_bandwidth_mean"],
            chroma_mean=features["chroma_mean"],
            mfcc_mean=features["mfcc_mean"],
        ),
    )