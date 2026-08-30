"""
Central place for environment-driven settings.

TODO(Person2): once Person 1 confirms the schema, add here:
  - CORE_BUG_SYSTEM_URL   (if we poll/pull from Person 1's API)
  - CORE_BUG_SYSTEM_WEBHOOK_SECRET (if Person 1 pushes events to us)
"""

import os

# Our own derived-data DB (NOT Person 1's core bug DB).
# SQLite is fine for hackathon speed; swap DATABASE_URL for Postgres if needed.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_intelligence.db")

# Set this once we wire up real LLM-based explanations (XAI layer).
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Toggle: while Person 1's real data isn't wired up yet, routers return
# clearly-labeled mock data so Person 3/4 can build against a stable contract.
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "true").lower() == "true"
