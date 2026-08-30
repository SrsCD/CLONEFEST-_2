# AI & Developer Intelligence Service (Person 2)

Standalone FastAPI microservice implementing the 10 AI-driven features
owned by Person 2 in the Bugzilla-reconstruction hackathon project.

## Setup (VS Code)

```bash
cd ai-intelligence-service
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Then open http://127.0.0.1:8001/docs for interactive Swagger UI —
this is also what you can share with Person 3/4 to explore the contract.

## Project layout

```
app/
  main.py               # FastAPI app, mounts all routers
  config.py             # env-driven settings
  database.py           # our OWN derived-data DB (not Person 1's core DB)
  models.py             # SQLAlchemy tables: similarity scores, patterns, genealogy
  schemas.py            # Pydantic request/response contracts (share with Person 3/4)
  routers/
    triage.py            # #1  Explainable Bug Triage
    duplicates.py         # #2  Explainable Duplicate Detection
    assignment.py         # #3  Intelligent Bug Assignment
    dependencies.py       # #4  Dependency Intelligence
    stagnation.py         # #5  Bug Stagnation Intelligence
    code_intelligence.py  # #7  Bug -> Code Intelligence
    patterns.py           # #8  Pattern / Root-Cause Intelligence
    risk.py               # #9  Predictive Bug Detection (local-only)
    genealogy.py          # #10 Bug Genealogy
    blast_radius.py       # #11 Bug Blast Radius
```

Note: Security Bug Mode (#6) has no dedicated router — Person 1 owns the
access-control gate. Our contribution (CVSS/severity scoring) will be
folded into the `triage` response once built.

## Status

Every route currently returns a clearly-labeled **STUB** response so
Person 3 (frontend) and Person 4 (integration) can build against a
stable contract immediately. Real logic is added feature-by-feature,
starting with Triage (#1).

## Open items to confirm with Person 1

- Exact field names on a bug record (title, description, component,
  file paths touched, commit SHAs, reopen count, assignee history,
  timestamps).
- How this service receives new/updated bug data: webhook push,
  polling their API, or shared read access.
- Confirm Person 1 owns the ACL/visibility gate for Security Bug Mode;
  we only supply scoring metadata into it.
