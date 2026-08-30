"""Feature #8 — Pattern / Root-Cause Intelligence. STATUS: real aggregation logic wired in."""

from typing import List
from fastapi import APIRouter
from app.schemas import PatternResponse
from app.pattern_logic import detect_patterns

router = APIRouter()


@router.get("", response_model=List[PatternResponse])
def get_patterns():
    patterns = detect_patterns()
    return [PatternResponse(**p) for p in patterns]
