"""
Feature: Spectral and energy feature extraction module
Purpose: Compute energy (RMS) and spectral features (centroid, bandwidth,
         chroma, MFCC) from an audio file, in a reusable way the API can
         call.
Main files: app/audio/feature_extractor.py
How it works: load audio -> compute RMS energy over time -> compute
              spectral centroid/bandwidth -> compute chroma and MFCC ->
              convert everything to native Python lists.
Concepts learned: RMS energy, spectral centroid/bandwidth, chroma
                   features, MFCCs, converting NumPy arrays to JSON-safe
                   lists.
"""

from pathlib import Path

import librosa
import numpy as np


def extract_features(file_path: str | Path) -> dict:
    """
    Analyse un fichier audio et retourne un dict de features :
    energy, spectral_centroid, spectral_bandwidth, chroma_mean, mfcc_mean.
    """
    y, sr = librosa.load(str(file_path), sr=None)

    rms = librosa.feature.rms(y=y)[0]
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

    return {
        "energy": rms.tolist(),
        "spectral_centroid_mean": float(np.mean(centroid)),
        "spectral_bandwidth_mean": float(np.mean(bandwidth)),
        "chroma_mean": chroma.mean(axis=1).tolist(),
        "mfcc_mean": mfcc.mean(axis=1).tolist(),
    }