"""
Bug Stagnation Intelligence (#5) — real bug data.

Uses real created_at/updated_at timestamps, assignee, and reproduction
steps from Person 1's BugOff backend. Reopen count and blocker checks
reuse the real dependency graph (dependency_logic.py).

HONEST NOTE: full reopen-count tracking would need parsing bug history
events; for now we treat "reopen" detection as a documented future
enhancement and default that signal to 0 rather than guessing.
"""

from datetime import datetime, timezone
from app.bugoff_client import get_bug_raw
from app.dependency_logic import get_dependencies

STAGNATION_AGE_THRESHOLD_DAYS = 3      # lowered from 14 for demo-scale fresh bugs
NO_ACTIVITY_THRESHOLD_DAYS = 3


def _days_since(timestamp_str: str) -> float:
    ts = datetime.fromisoformat(timestamp_str)
    now = datetime.now(timezone.utc)
    return (now - ts).total_seconds() / 86400


def get_stagnation(bug_id: int):
    raw = get_bug_raw(bug_id)

    days_open = _days_since(raw["created_at"])
    days_since_activity = _days_since(raw["updated_at"])

    if days_open < STAGNATION_AGE_THRESHOLD_DAYS:
        return {
            "is_stagnant": False,
            "reasons": [f"Bug is only {days_open:.1f} days old; too early to flag as stagnant"],
        }

    reasons = []

    if not raw.get("assignee_username"):
        reasons.append("No assignee has been set")

    if days_since_activity >= NO_ACTIVITY_THRESHOLD_DAYS:
        reasons.append(f"No activity for {days_since_activity:.1f} days")

    if not raw.get("reproduction_steps"):
        reasons.append("Missing reproduction steps")

    deps = get_dependencies(bug_id)
    if deps["blockers"]:
        reasons.append(f"Waiting on unresolved blocker(s): {deps['blockers']}")

    is_stagnant = len(reasons) > 0
    if not is_stagnant:
        reasons = ["Bug is old but shows no other stagnation signals"]

    return {"is_stagnant": is_stagnant, "reasons": reasons}
