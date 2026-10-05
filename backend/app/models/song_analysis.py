"""
Feature: SongAnalysis data model
Purpose: Define the structure of a complete audio analysis result (BPM,
         beats, key, duration, energy, spectral features) so FastAPI can
         validate and document it automatically.
Main files: app/models/song_analysis.py
How it works: a Pydantic BaseModel describing every field returned by
              the analysis pipeline.
Concepts learned: Pydantic models for request/response validation and
                   automatic OpenAPI documentation.
"""

from pydantic import BaseModel


class SpectralFeatures(BaseModel):
    spectral_centroid_mean: float
    spectral_bandwidth_mean: float
    chroma_mean: list[float]
    mfcc_mean: list[float]


class SongAnalysis(BaseModel):
    id: str
    bpm: float
    key: str
    beat_times: list[float]
    energy: list[float]
    spectral_features: SpectralFeatures