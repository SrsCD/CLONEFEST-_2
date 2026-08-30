"""Feature #7 — Bug -> Code Intelligence. STATUS: real aggregation logic wired in."""

from fastapi import APIRouter
from app.schemas import CodeIntelligenceResponse
from app.code_intelligence_logic import get_code_intelligence

router = APIRouter()


@router.get("/{component}", response_model=CodeIntelligenceResponse)
def get_component_code_intelligence(component: str):
    result = get_code_intelligence(component)
    return CodeIntelligenceResponse(
        component=component,
        bug_count=result["bug_count"],
        security_bug_count=result["security_bug_count"],
        top_files=result["top_files"],
    )
