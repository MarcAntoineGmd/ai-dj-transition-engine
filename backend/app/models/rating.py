"""
Feature: Rating data models
Purpose: Define and validate the payloads of the rating endpoints
         (a submitted rating, the progress of a rater, the next clip).
Main files: app/models/rating.py
How it works: Pydantic models; rater names are restricted to letters,
              digits, underscore and hyphen; ratings to integers 1-5.
Concepts learned: whitelist validation of user-supplied identifiers,
                   sharing one validation pattern between body and query
                   parameters.
"""

from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

RATER_PATTERN = r"^[A-Za-z0-9_-]+$"

RaterName = Annotated[
    str, StringConstraints(min_length=1, max_length=40, pattern=RATER_PATTERN)
]


class RatingRequest(BaseModel):
    transition_id: str
    rater: RaterName
    rating: int = Field(ge=1, le=5)


class RatingProgress(BaseModel):
    rated: int
    total: int


class NextClip(RatingProgress):
    transition_id: str | None