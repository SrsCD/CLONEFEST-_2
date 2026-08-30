"""
Pydantic models = the actual contract Person 3 (frontend) and Person 4
(integration layer) will code against. Keep these stable once shared;
breaking changes here break their code too.

NOTE: BugInput fields below are our best guess pending Person 1 confirming
the real schema. Flag any mismatch back to the team once confirmed.
"""

from typing import List, Optional
from pydantic import BaseModel


# ---- Shared input shape --------------------------------------------------

class BugInput(BaseModel):
    """Minimum fields we need from Person 1 to run triage/duplicates.
    TODO(Person2): confirm exact field names with Person 1."""
    id: Optional[int] = None
    title: str
    description: str
    component: Optional[str] = None
    reporter: Optional[str] = None
    is_security: Optional[bool] = False


# ---- 1. Explainable Triage ------------------------------------------------

class TriageRequest(BaseModel):
    bug: BugInput


class TriageResponse(BaseModel):
    severity: str
    priority: str
    category: str
    component: str
    explanation: List[str]


# ---- 2. Explainable Duplicate Detection -----------------------------------

class DuplicateCheckRequest(BaseModel):
    bug: BugInput


class DuplicateMatch(BaseModel):
    bug_id: int
    similarity: float
    reasons: List[str]


# ---- 3. Intelligent Bug Assignment ----------------------------------------

class AssignmentRequest(BaseModel):
    bug: BugInput


class AssignmentRecommendation(BaseModel):
    developer: str
    score: float
    reasons: List[str]
    current_workload: int


# ---- 4. Dependency Intelligence / 11. Blast Radius ------------------------

class DependencyResponse(BaseModel):
    bug_id: int
    blockers: List[int]
    blocked_count: int
    critical_path: List[int]


class BlastRadiusResponse(BaseModel):
    bug_id: int
    components: List[str]
    workflows: List[str]
    affected_bugs: List[int]
    severity_estimate: str


# ---- 5. Stagnation Intelligence -------------------------------------------

class StagnationResponse(BaseModel):
    bug_id: int
    is_stagnant: bool
    reasons: List[str]


# ---- 7. Bug -> Code Intelligence ------------------------------------------

class CodeIntelligenceResponse(BaseModel):
    component: str
    bug_count: int
    security_bug_count: int
    top_files: List[str]


# ---- 8. Pattern / Root-Cause Intelligence ---------------------------------

class PatternResponse(BaseModel):
    pattern: str
    root_area: str
    historical_bugs: int
    security_bugs: int
    reopened_bugs: int


# ---- 9. Predictive Risk (local only) --------------------------------------

class RiskPredictRequest(BaseModel):
    component: str
    files_changed: List[str]
    diff_summary: Optional[str] = None


class RiskPredictResponse(BaseModel):
    risk_level: str
    similar_past_changes: List[str]
    recommendation: str


# ---- 10. Genealogy ----------------------------------------------------------

class GenealogyResponse(BaseModel):
    bug_id: int
    related_closed_bugs: List[int]
    shared_root_cause: str
