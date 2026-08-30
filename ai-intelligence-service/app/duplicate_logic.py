"""
Explainable Duplicate Detection (#2) — real bugs, TF-IDF + cosine similarity.

Fetches real bugs from Person 1's BugOff backend instead of a hardcoded
mock list. The similarity/explanation logic itself is unchanged.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.bugoff_client import list_bugs

DEFAULT_PROJECT_ID = 1


def find_duplicates(new_title: str, new_description: str, threshold: float = 0.3, project_id: int = DEFAULT_PROJECT_ID):
    existing_bugs = list_bugs(project_id=project_id)
    if not existing_bugs:
        return []

    new_text = f"{new_title} {new_description}"
    corpus = [new_text] + [f"{b['title']} {b['description']}" for b in existing_bugs]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)

    new_vector = tfidf_matrix[0:1]
    existing_vectors = tfidf_matrix[1:]
    similarities = cosine_similarity(new_vector, existing_vectors)[0]

    new_words = set(vectorizer.build_analyzer()(new_text))

    results = []
    for i, score in enumerate(similarities):
        if score >= threshold:
            bug = existing_bugs[i]
            bug_words = set(vectorizer.build_analyzer()(f"{bug['title']} {bug['description']}"))
            shared_words = sorted(new_words & bug_words)
            reasons = [f"Shared term: '{w}'" for w in shared_words[:5]] or ["Overall text similarity"]
            results.append({"bug_id": bug["id"], "similarity": round(float(score), 2), "reasons": reasons})

    results.sort(key=lambda r: r["similarity"], reverse=True)
    return results
