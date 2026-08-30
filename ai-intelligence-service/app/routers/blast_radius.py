"""Feature #11 — Bug Blast Radius. STATUS: real graph logic wired in (shares graph with #4)."""

from fastapi import APIRouter
from app.schemas import BlastRadiusResponse
from app.dependency_logic import get_blast_radius

router = APIRouter()


@router.get("/{bug_id}", response_model=BlastRadiusResponse)
def get_bug_blast_radius(bug_id: int):
    result = get_blast_radius(bug_id)
    return BlastRadiusResponse(
        bug_id=bug_id,
        components=result["components"],
        workflows=result["workflows"],
        affected_bugs=result["affected_bugs"],
        severity_estimate=result["severity_estimate"],
    )
