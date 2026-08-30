"""
Feature #9 — Predictive Bug Detection (heuristic, stretch goal).

IMPORTANT: designed to run LOCALLY. Only derived risk metadata should
ever leave the company's environment, never raw source code/diffs.
"""

from fastapi import APIRouter
from app.schemas import RiskPredictRequest, RiskPredictResponse
from app.risk_logic import predict_risk

router = APIRouter()


@router.post("/predict", response_model=RiskPredictResponse)
def predict_bug_risk(request: RiskPredictRequest):
    result = predict_risk(request.component, request.files_changed)
    return RiskPredictResponse(
        risk_level=result["risk_level"],
        similar_past_changes=result["similar_past_changes"],
        recommendation=result["recommendation"],
    )
