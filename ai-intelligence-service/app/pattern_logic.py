"""
Pattern / Root-Cause Intelligence (#8) — real bugs, real aggregation.

Aggregates category classifications and is_security flags across all
real bugs in the project to detect recurring root causes.
"""

from app.bugoff_client import list_bugs
from app.triage_logic import classify_category

DEFAULT_PROJECT_ID = 1

ROOT_AREA_MAP = {
    "Authentication": "/auth/token_manager",
    "Database": "/db/query_engine",
    "Security": "/security/access_control",
    "UI/UX": "/frontend/components",
    "Performance": "/core/perf_utils",
    "General": "/misc",
}

PATTERN_MIN_BUGS = 2


def detect_patterns(project_id: int = DEFAULT_PROJECT_ID):
    bugs = list_bugs(project_id=project_id)
    category_bugs = {}

    for bug in bugs:
        text = f"{bug['title']} {bug['description']}"
        category, _ = classify_category(text)
        category_bugs.setdefault(category, []).append(bug)

    patterns = []
    for category, cat_bugs in category_bugs.items():
        if len(cat_bugs) < PATTERN_MIN_BUGS:
            continue

        security_count = sum(1 for b in cat_bugs if b.get("is_security"))
        # Reopen tracking not yet available from real bug history data.
        reopened_count = 0

        patterns.append({
            "pattern": f"Recurring problem detected in {category}",
            "root_area": ROOT_AREA_MAP.get(category, "/unknown"),
            "historical_bugs": len(cat_bugs),
            "security_bugs": security_count,
            "reopened_bugs": reopened_count,
        })

    return patterns
