"""
Predictive Bug Detection (#9) — heuristic version, stretch goal.

Per the scope doc, this is meant to run LOCALLY and only send derived
metadata out, never source code. This heuristic version checks if a
changed file has a history of causing bugs, using the same
bug-count-per-component data as Bug -> Code Intelligence (#7).

A full version would parse actual git diffs and compare against a
trained model of past regressions; for a hackathon, "this file has
caused N bugs before" is a defensible, explainable stand-in.
"""

from app.code_intelligence_logic import get_code_intelligence, MOCK_FILES

RISK_FILE_THRESHOLD_HIGH = 2   # bugs in this file's component to call it High risk
RISK_FILE_THRESHOLD_MEDIUM = 1


def predict_risk(component: str, files_changed: list[str]):
    intel = get_code_intelligence(component)
    bug_count = intel["bug_count"]
    known_risky_files = intel["top_files"]

    matched_files = [f for f in files_changed if f in known_risky_files]

    if bug_count >= RISK_FILE_THRESHOLD_HIGH and matched_files:
        risk_level = "High"
        recommendation = (
            f"This change touches file(s) with a history of causing bugs in "
            f"'{component}' ({bug_count} historical bugs). Recommend thorough "
            f"testing before merge, especially around: {', '.join(matched_files)}."
        )
    elif bug_count >= RISK_FILE_THRESHOLD_MEDIUM and matched_files:
        risk_level = "Medium"
        recommendation = (
            f"This change touches a file with some bug history in '{component}'. "
            f"Consider extra review for: {', '.join(matched_files)}."
        )
    else:
        risk_level = "Low"
        recommendation = "No strong historical risk signals found for these files."

    similar_past_changes = [
        f"{component} had {bug_count} historical bug(s) linked to files: {', '.join(known_risky_files)}"
    ] if known_risky_files else []

    return {
        "risk_level": risk_level,
        "similar_past_changes": similar_past_changes,
        "recommendation": recommendation,
    }
