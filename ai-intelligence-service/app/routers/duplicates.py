"""Feature #2 — Explainable Duplicate Detection. STATUS: real TF-IDF logic wired in."""

from typing import List
from fastapi import APIRouter
from app.schemas import DuplicateCheckRequest, DuplicateMatch
from app.duplicate_logic import find_duplicates

router = APIRouter()


@router.post("/check", response_model=List[DuplicateMatch])
def check_duplicates(request: DuplicateCheckRequest):
    bug = request.bug
    matches = find_duplicates(bug.title, bug.description)
    return [
        DuplicateMatch(bug_id=m["bug_id"], similarity=m["similarity"], reasons=m["reasons"])
        for m in matches
    ]
