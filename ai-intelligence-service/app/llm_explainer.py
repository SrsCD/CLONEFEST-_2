"""
LLM-based explanation polish layer (feature #1's "XAI" polish).

IMPORTANT: this file does NOT decide severity/priority/category.
Those decisions are made by app/triage_logic.py using real, checkable
rules. This file only takes those already-decided facts + reasons and
asks Claude to turn them into a well-written natural-language sentence.

If no API key is configured, or the API call fails for any reason
(including insufficient credit), this falls back to a plain (but still
accurate) joined-reasons string. This fallback matters for demo
reliability — the feature must never break just because a network
call or billing issue occurred.
"""

import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

try:
    from anthropic import Anthropic
    _client = Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None
except Exception:
    _client = None


def polish_explanation(severity: str, priority: str, category: str, reasons: list[str]) -> str:
    """
    Turns a list of raw rule-based reasons into one polished sentence.
    Falls back to a plain joined string if no API key or on any error.
    """
    fallback = f"Classified as {severity} ({priority}, {category}) because: " + "; ".join(reasons)

    if _client is None:
        return fallback

    reasons_text = "\n".join(f"- {r}" for r in reasons)
    prompt = (
        f"A bug tracking system classified a bug as follows:\n"
        f"Severity: {severity}\nPriority: {priority}\nCategory: {category}\n\n"
        f"The classification was based on these detected signals:\n{reasons_text}\n\n"
        f"Write ONE short, clear sentence explaining why this bug got this "
        f"classification. Only use the facts given above, do not invent new "
        f"reasons. Do not repeat the severity/priority/category labels verbatim, "
        f"just explain the reasoning naturally."
    )

    try:
        response = _client.messages.create(
            model="claude-sonnet-5",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception:
        return fallback
