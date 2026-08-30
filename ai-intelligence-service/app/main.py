"""
AI & Developer Intelligence Service (Person 2's backend)

This is a standalone FastAPI microservice. It does NOT share a database
with Person 1's Core Bug System. It receives bug data via API calls
(from Person 1 or Person 4's integration layer) and returns AI-derived
intelligence: classifications, duplicate scores, assignment recommendations,
dependency graphs, patterns, risk predictions, genealogy, and blast radius.

Run locally with:
    uvicorn app.main:app --reload --port 8001
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import (
    triage,
    duplicates,
    assignment,
    dependencies,
    stagnation,
    code_intelligence,
    patterns,
    risk,
    genealogy,
    blast_radius,
)

app = FastAPI(
    title="BugOff - AI & Developer Intelligence Service",
    description="Explainable AI microservice for bug triage, duplicate detection, "
                 "assignment, dependency analysis, pattern detection, and risk prediction.",
    version="0.1.0",
)

# Allow the frontend (Person 3) and integration layer (Person 4) to call this
# service directly during development. Tighten this before deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ai-intelligence"}


# Each feature lives in its own router file under app/routers/.
# Prefixes match the API surface agreed in the scope doc.
app.include_router(triage.router, prefix="/triage", tags=["Triage"])
app.include_router(duplicates.router, prefix="/duplicates", tags=["Duplicates"])
app.include_router(assignment.router, prefix="/assignment", tags=["Assignment"])
app.include_router(dependencies.router, prefix="/dependencies", tags=["Dependencies"])
app.include_router(stagnation.router, prefix="/stagnation", tags=["Stagnation"])
app.include_router(code_intelligence.router, prefix="/code-intelligence", tags=["Code Intelligence"])
app.include_router(patterns.router, prefix="/patterns", tags=["Patterns"])
app.include_router(risk.router, prefix="/risk", tags=["Risk (local-only)"])
app.include_router(genealogy.router, prefix="/genealogy", tags=["Genealogy"])
app.include_router(blast_radius.router, prefix="/blast-radius", tags=["Blast Radius"])
