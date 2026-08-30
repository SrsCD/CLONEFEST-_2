"""
Bug -> Code Intelligence (#7) — real bug counts, mock file data.

Bug counts and security-bug counts per component now come from real
bugs via Person 1's API. HONEST GAP: BugOff's schema has no commit/file
linkage yet, so "top_files" remains a documented placeholder until that
data exists on their side.
"""

from app.bugoff_client import list_bugs

DEFAULT_PROJECT_ID = 1  # single demo project for this hackathon

MOCK_FILES = {
    "Authentication": ["/auth/token_manager.py", "/auth/session.py", "/auth/login.py"],
    "Frontend UI": ["/frontend/components/Chart.jsx", "/frontend/styles/theme.css"],
    "Database": ["/db/query_engine.py", "/db/migrations.py"],
}


def get_code_intelligence(component: str, project_id: int = DEFAULT_PROJECT_ID):
    bugs = list_bugs(project_id=project_id)
    bugs_in_component = [b for b in bugs if b.get("component_name") == component]

    bug_count = len(bugs_in_component)
    security_bug_count = sum(1 for b in bugs_in_component if b.get("is_security"))

    top_files = MOCK_FILES.get(component, [])

    return {
        "bug_count": bug_count,
        "security_bug_count": security_bug_count,
        "top_files": top_files,
    }
