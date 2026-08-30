"""
Real HTTP client for Person 1's BugOff Core Backend.

This replaces the MOCK_BUGS/MOCK_DEVELOPERS/MOCK_EDGES dictionaries used
during early development. It logs in once as a dedicated service account
("ai_intelligence_bot"), caches the token, and re-logs-in automatically
if a call comes back unauthorized (token expired).

Field mapping: their API returns component_name/reporter_username
alongside numeric IDs. We map those to the `component`/`reporter` names
our internal logic (triage_logic.py etc.) already expects.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

BUGOFF_API_URL = os.getenv("BUGOFF_API_URL", "")
BUGOFF_BOT_USERNAME = os.getenv("BUGOFF_BOT_USERNAME", "")
BUGOFF_BOT_PASSWORD = os.getenv("BUGOFF_BOT_PASSWORD", "")

HEADERS_BASE = {"ngrok-skip-browser-warning": "true"}

_cached_token = None


def _login():
    global _cached_token
    response = requests.post(
        f"{BUGOFF_API_URL}/auth/login",
        headers=HEADERS_BASE,
        data={"username": BUGOFF_BOT_USERNAME, "password": BUGOFF_BOT_PASSWORD},
        timeout=10,
    )
    response.raise_for_status()
    _cached_token = response.json()["access_token"]
    return _cached_token


def _auth_headers():
    global _cached_token
    if _cached_token is None:
        _login()
    return {**HEADERS_BASE, "Authorization": f"Bearer {_cached_token}"}


def _get(path: str):
    """GET with automatic re-login on 401 (expired token)."""
    global _cached_token
    response = requests.get(f"{BUGOFF_API_URL}{path}", headers=_auth_headers(), timeout=10)
    if response.status_code == 401:
        _login()
        response = requests.get(f"{BUGOFF_API_URL}{path}", headers=_auth_headers(), timeout=10)
    response.raise_for_status()
    return response.json()


def get_bug(bug_id: int):
    """
    Fetches a real bug and maps it to the shape our internal logic expects:
    {id, title, description, component, reporter}
    """
    data = _get(f"/bugs/{bug_id}")
    return {
        "id": data["id"],
        "title": data["title"],
        "description": data["description"],
        "component": data.get("component_name", ""),
        "reporter": data.get("reporter_username", ""),
        "is_security": data.get("is_security", False),
    }


def get_bug_dependencies(bug_id: int):
    """Returns real {bug_id, outgoing: [...], incoming: [...]} from BugOff."""
    return _get(f"/bugs/{bug_id}/dependencies")


def get_user(user_id: int):
    """Returns real user data including skills."""
    return _get(f"/users/{user_id}")


def list_bugs(project_id: int = None):
    """Lists real bugs, optionally filtered by project."""
    path = "/bugs"
    if project_id is not None:
        path += f"?project_id={project_id}"
    return _get(path)


def get_bug_raw(bug_id: int):
    """Returns the full raw bug record (unmapped), including project_id."""
    return _get(f"/bugs/{bug_id}")
