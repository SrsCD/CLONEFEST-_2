"""
Rule-based classification logic for Explainable Bug Triage (Feature #1).

HYBRID APPROACH:
1. Check direct signals first (e.g. is_security flag from the source
   system) — these are human-confirmed judgments, more reliable than
   any text inference.
2. Try exact keyword matching (fast, zero ambiguity).
3. If no keywords match, fall back to semantic similarity so real-world
   bugs with different wording still get classified correctly.

All three paths are fully explainable — no black box anywhere.
"""

from app.semantic_logic import classify_category_semantic, classify_severity_semantic


def classify_severity(text: str, is_security: bool = False) -> tuple[str, list[str]]:
    if is_security:
        return "Critical", ["Marked as a security issue (is_security=true) by the source system"]

    text_lower = text.lower()
    reasons = []

    critical_keywords = ["security", "vulnerability", "breach", "exploit", "crash", "data loss"]
    high_keywords = ["broken", "fails", "error", "unauthorized"]
    low_keywords = ["slow", "minor", "cosmetic", "typo"]

    for word in critical_keywords:
        if word in text_lower:
            reasons.append(f"Contains critical keyword: '{word}'")
    if reasons:
        return "Critical", reasons

    for word in high_keywords:
        if word in text_lower:
            reasons.append(f"Contains high-severity keyword: '{word}'")
    if reasons:
        return "High", reasons

    for word in low_keywords:
        if word in text_lower:
            reasons.append(f"Contains low-severity keyword: '{word}'")
    if reasons:
        return "Low", reasons

    return classify_severity_semantic(text)


def classify_category(text: str) -> tuple[str, list[str]]:
    text_lower = text.lower()

    categories = {
        "Authentication": ["login", "auth", "password", "token", "session"],
        "Database": ["database", "query", "sql", "migration", "record"],
        "Security": ["security", "vulnerability", "exploit", "breach", "injection"],
        "UI/UX": ["button", "layout", "css", "display", "ui", "design"],
        "Performance": ["slow", "timeout", "lag", "memory", "performance"],
    }

    for category, keywords in categories.items():
        matched = [kw for kw in keywords if kw in text_lower]
        if matched:
            reasons = [f"Matched '{kw}' -> {category}" for kw in matched]
            return category, reasons

    return classify_category_semantic(text)


def classify_priority(severity: str, text: str) -> tuple[str, list[str]]:
    text_lower = text.lower()
    reasons = []

    urgent_keywords = ["production", "blocking", "urgent", "outage"]
    matched_urgent = [kw for kw in urgent_keywords if kw in text_lower]

    if matched_urgent:
        reasons = [f"Contains urgency keyword: '{kw}'" for kw in matched_urgent]
        return "P0", reasons

    severity_to_priority = {
        "Critical": "P1",
        "High": "P2",
        "Medium": "P3",
        "Low": "P4",
    }
    priority = severity_to_priority.get(severity, "P3")
    reasons.append(f"Priority derived from severity level: {severity}")
    return priority, reasons
