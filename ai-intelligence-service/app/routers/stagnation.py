"""Feature #5 — Bug Stagnation Intelligence. STATUS: real logic wired in."""

from fastapi import APIRouter
from app.schemas import StagnationResponse
from app.stagnation_logic import get_stagnation

router = APIRouter()


@router.get("/{bug_id}", response_model=StagnationResponse)
def get_bug_stagnation(bug_id: int):
    result = get_stagnation(bug_id)
    return StagnationResponse(
        bug_id=bug_id,
        is_stagnant=result["is_stagnant"],
        reasons=result["reasons"],
    )
