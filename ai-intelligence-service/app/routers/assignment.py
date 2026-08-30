"""Feature #3 — Intelligent Bug Assignment. STATUS: real logic wired in."""

from typing import List
from fastapi import APIRouter
from app.schemas import AssignmentRequest, AssignmentRecommendation
from app.assignment_logic import recommend_assignee

router = APIRouter()


@router.post("/recommend", response_model=List[AssignmentRecommendation])
def recommend_bug_assignee(request: AssignmentRequest):
    bug = request.bug
    combined_text = f"{bug.title} {bug.description}"
    results = recommend_assignee(bug.component or "", combined_text)
    return [
        AssignmentRecommendation(
            developer=r["developer"],
            score=r["score"],
            reasons=r["reasons"],
            current_workload=r["current_workload"],
        )
        for r in results
    ]
