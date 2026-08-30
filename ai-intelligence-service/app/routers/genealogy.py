"""Feature #10 — Bug Genealogy. STATUS: real similarity logic wired in (shares engine with #2)."""

from fastapi import APIRouter
from app.schemas import GenealogyResponse
from app.genealogy_logic import get_genealogy

router = APIRouter()


@router.get("/{bug_id}", response_model=GenealogyResponse)
def get_bug_genealogy(bug_id: int):
    result = get_genealogy(bug_id)
    return GenealogyResponse(
        bug_id=bug_id,
        related_closed_bugs=result["related_closed_bugs"],
        shared_root_cause=result["shared_root_cause"],
    )
