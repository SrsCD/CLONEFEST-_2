"""Feature #4 — Dependency Intelligence. STATUS: real graph logic wired in."""

from fastapi import APIRouter
from app.schemas import DependencyResponse
from app.dependency_logic import get_dependencies

router = APIRouter()


@router.get("/{bug_id}", response_model=DependencyResponse)
def get_bug_dependencies(bug_id: int):
    result = get_dependencies(bug_id)
    return DependencyResponse(
        bug_id=bug_id,
        blockers=result["blockers"],
        blocked_count=result["blocked_count"],
        critical_path=result["critical_path"],
    )
