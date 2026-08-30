"""
Feature #1 — Explainable Bug Triage.

STATUS: real rule-based classification (with direct is_security signal)
+ semantic fallback.
"""

from fastapi import APIRouter
from app.schemas import TriageRequest, TriageResponse
from app.triage_logic import classify_severity, classify_category, classify_priority

router = APIRouter()


@router.post("/classify", response_model=TriageResponse)
def classify_bug(request: TriageRequest):
    bug = request.bug
    combined_text = f"{bug.title} {bug.description}"

    severity, severity_reasons = classify_severity(combined_text, is_security=bug.is_security or False)
    category, category_reasons = classify_category(combined_text)
    priority, priority_reasons = classify_priority(severity, combined_text)

    explanation = severity_reasons + category_reasons + priority_reasons

    return TriageResponse(
        severity=severity,
        priority=priority,
        category=category,
        component=bug.component or category,
        explanation=explanation,
    )
