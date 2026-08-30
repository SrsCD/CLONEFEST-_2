"""
Semantic classification fallback using free, local sentence embeddings.

This does NOT call any external API — the model runs entirely on your
machine after the first download. It's used as a FALLBACK: exact
keyword matches (in triage_logic.py) are tried first because they're
faster and unambiguous. Only when no keyword matches, we fall back to
semantic similarity so real-world bug reports that use different
wording still get classified correctly.

First run will download the model (~80MB) automatically, then it's cached.
"""

from sentence_transformers import SentenceTransformer, util

_model = SentenceTransformer("all-MiniLM-L6-v2")

# Reference examples per category — the new bug is compared against these.
CATEGORY_EXAMPLES = {
    "Authentication": [
        "User cannot log into their account",
        "Password reset is not working",
        "Session expires unexpectedly",
        "Unable to sign in with correct credentials",
    ],
    "Database": [
        "Query returns incorrect results",
        "Database migration failed",
        "Records are not saving correctly",
        "Data corruption in the database",
    ],
    "Security": [
        "Potential security vulnerability found",
        "Unauthorized access to restricted data",
        "SQL injection possible in this endpoint",
        "Sensitive data exposed publicly",
    ],
    "UI/UX": [
        "Button is misaligned on the page",
        "Layout looks broken on mobile",
        "Design is inconsistent across pages",
        "Text is overlapping on the screen",
    ],
    "Performance": [
        "Page takes too long to load",
        "Application is running slowly",
        "High memory usage causing lag",
        "Requests are timing out",
    ],
}

# Reference examples per severity level.
SEVERITY_EXAMPLES = {
    "Critical": [
        "System crashes and data is lost",
        "Security breach exposing user data",
        "Complete outage, nothing works",
    ],
    "High": [
        "Major feature is completely broken",
        "Users cannot complete an important action",
        "Frequent errors affecting many users",
    ],
    "Low": [
        "Minor visual glitch, barely noticeable",
        "Small typo in the interface",
        "Cosmetic issue with no functional impact",
    ],
}

# Pre-compute embeddings for all reference examples once at startup.
_category_embeddings = {
    cat: _model.encode(examples, convert_to_tensor=True)
    for cat, examples in CATEGORY_EXAMPLES.items()
}
_severity_embeddings = {
    sev: _model.encode(examples, convert_to_tensor=True)
    for sev, examples in SEVERITY_EXAMPLES.items()
}

SIMILARITY_THRESHOLD = 0.45


def classify_category_semantic(text: str):
    text_embedding = _model.encode(text, convert_to_tensor=True)

    best_category = None
    best_score = -1.0
    best_example = None

    for category, embeddings in _category_embeddings.items():
        scores = util.cos_sim(text_embedding, embeddings)[0]
        max_score = float(scores.max())
        if max_score > best_score:
            best_score = max_score
            best_category = category
            best_example = CATEGORY_EXAMPLES[category][int(scores.argmax())]

    if best_score >= SIMILARITY_THRESHOLD:
        reasons = [
            f"Semantically similar to typical '{best_category}' bug: "
            f"\"{best_example}\" (similarity {best_score:.2f})"
        ]
        return best_category, reasons

    return "General", [f"No strong semantic match found (best score {best_score:.2f})"]


def classify_severity_semantic(text: str):
    text_embedding = _model.encode(text, convert_to_tensor=True)

    best_severity = None
    best_score = -1.0
    best_example = None

    for severity, embeddings in _severity_embeddings.items():
        scores = util.cos_sim(text_embedding, embeddings)[0]
        max_score = float(scores.max())
        if max_score > best_score:
            best_score = max_score
            best_severity = severity
            best_example = SEVERITY_EXAMPLES[severity][int(scores.argmax())]

    if best_score >= SIMILARITY_THRESHOLD:
        reasons = [
            f"Semantically similar to typical '{best_severity}' bug: "
            f"\"{best_example}\" (similarity {best_score:.2f})"
        ]
        return best_severity, reasons

    return "Medium", [f"No strong semantic match found (best score {best_score:.2f}); defaulting to Medium"]
