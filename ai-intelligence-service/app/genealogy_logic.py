"""
Bug Genealogy (#10) — real bugs, same TF-IDF engine as duplicate detection.

Compares an EXISTING real bug against all OTHER real bugs in the same
project to find ones it may share a root cause with.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.bugoff_client import list_bugs, get_bug_raw
from app.triage_logic import classify_category

GENEALOGY_THRESHOLD = 0.2


def get_genealogy(bug_id: int):
    raw = get_bug_raw(bug_id)
    project_id = raw["project_id"]
    all_bugs = list_bugs(project_id=project_id)

    target_bug = next((b for b in all_bugs if b["id"] == bug_id), None)
    if target_bug is None:
        return {"related_closed_bugs": [], "shared_root_cause": "Unknown bug ID"}

    other_bugs = [b for b in all_bugs if b["id"] != bug_id]
    if not other_bugs:
        return {"related_closed_bugs": [], "shared_root_cause": "No other bugs to compare against"}

    target_text = f"{target_bug['title']} {target_bug['description']}"
    corpus = [target_text] + [f"{b['title']} {b['description']}" for b in other_bugs]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]

    related_ids = [
        other_bugs[i]["id"]
        for i, score in enumerate(similarities)
        if score >= GENEALOGY_THRESHOLD
    ]

    if related_ids:
        category, _ = classify_category(target_text)
        shared_root_cause = f"Recurring {category} issue"
    else:
        shared_root_cause = "No related historical bugs found"

    return {"related_closed_bugs": related_ids, "shared_root_cause": shared_root_cause}
