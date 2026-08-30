"""
Intelligent Bug Assignment (#3) — real project members, real skills.

Scores real project members by component ownership and skill-keyword
overlap. Workload is context only, never the primary signal.
"""

from app.bugoff_client import _get

DEFAULT_PROJECT_ID = 1


def recommend_assignee(component: str, text: str, project_id: int = DEFAULT_PROJECT_ID):
    text_lower = text.lower()
    members = _get(f"/projects/{project_id}/members")
    components = _get(f"/projects/{project_id}/components")

    component_owner_id = next(
        (c["owner_id"] for c in components if c.get("name") == component and c.get("owner_id")),
        None,
    )

    results = []
    for member in members:
        user = member["user"]
        score = 0.0
        reasons = []

        if component_owner_id and user["id"] == component_owner_id:
            score += 3
            reasons.append(f"Owns component: '{component}'")

        skills = [s.strip().lower() for s in (user.get("skills") or "").split(",") if s.strip()]
        matched_skills = [s for s in skills if s in text_lower]
        if matched_skills:
            score += 2 * len(matched_skills)
            reasons.extend([f"Has relevant skill: '{s}'" for s in matched_skills])

        if score > 0:
            results.append({
                "developer": user["username"],
                "score": round(score, 1),
                "reasons": reasons,
                "current_workload": 0,  # real workload count needs bug-count-by-assignee query
            })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results
