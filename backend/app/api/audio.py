"""
Feature: Audio file upload endpoint
Purpose: Accept an audio file from the client, validate it, store it
         temporarily, and return its basic metadata.
Main files: app/api/audio.py
How it works: validate extension -> read and check size -> save with a
              UUID filename -> read metadata via soundfile -> return JSON.
Concepts learned: UploadFile and multipart/form-data, two-level file
                   validation, UUIDs to avoid filename collisions, path
                   injection prevention.
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile
import soundfile as sf

router = APIRouter()

UPLOAD_DIR = Path("tmp_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".mp3", ".wav"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 Mo


@router.post("/upload")
async def upload_audio(file: UploadFile):
    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Format non supporté : {extension}")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Fichier trop volumineux (max 50 Mo)")

    file_id = str(uuid.uuid4())
    saved_path = UPLOAD_DIR / f"{file_id}{extension}"
    saved_path.write_bytes(contents)

    try:
        info = sf.info(str(saved_path))
    except Exception:
        saved_path.unlink()  # on supprime le fichier invalide
        raise HTTPException(status_code=400, detail="Fichier audio corrompu ou illisible")

    return {
        "id": file_id,
        "filename": file.filename,
        "duration": round(info.duration, 2),
        "sample_rate": info.samplerate,
    }