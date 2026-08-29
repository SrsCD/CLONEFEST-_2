"""
FastAPI application entrypoint.

Run locally with:
    uvicorn app.main:app --reload --port 8000

Swagger docs will be at http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(
    title="BugOff — Core Backend",
    description=(
        "Core bug-tracking backend for BugOff: users, projects, bugs, "
        "lifecycle, comments, attachments, history, search, labels, "
        "relationships, notifications, and statistics."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi.responses import RedirectResponse


@app.get("/", include_in_schema=False)
def root():
    """Bare root just points you to the interactive docs — nothing else lives here."""
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["meta"])
def health_check():
    """Basic liveness check — useful for Person 4's integration layer."""
    return {"status": "ok", "environment": settings.ENVIRONMENT}


# Routers get included here in later phases, e.g.:
# from app.routers import users, projects, bugs
# app.include_router(users.router)
# app.include_router(projects.router)
# app.include_router(bugs.router)

from app.routers import (
    auth, users, projects, components, versions, milestones,
    bugs, labels, notifications, stats,
)  # noqa: E402

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(components.router)
app.include_router(versions.router)
app.include_router(milestones.router)
app.include_router(bugs.router)
app.include_router(labels.router)
app.include_router(notifications.router)
app.include_router(stats.router)
