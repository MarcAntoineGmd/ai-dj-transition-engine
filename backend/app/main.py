"""
Feature: FastAPI application entry point
Purpose: Create the FastAPI app instance and register all API routers.
Main files: app/main.py
How it works: instantiate FastAPI -> configure CORS -> include routers
              (e.g. audio) -> expose /health.
Concepts learned: CORS between frontend and backend origins, router
                   registration with include_router.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.audio import router as audio_router

app = FastAPI()

app.include_router(audio_router, prefix="/api/audio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}
