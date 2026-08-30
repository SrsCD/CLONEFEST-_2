"""
Derived-data tables owned by the AI Intelligence Service.

These store OUR outputs, not Person 1's core bug data. Bug records
themselves are fetched from Person 1's system, not duplicated here
(beyond caching an embedding vector for speed, if needed later).
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func

from app.database import Base


class SimilarityScore(Base):
    """Cached result of a duplicate-detection comparison between two bugs."""
    __tablename__ = "similarity_scores"

    id = Column(Integer, primary_key=True, index=True)
    bug_id = Column(Integer, index=True, nullable=False)
    candidate_bug_id = Column(Integer, index=True, nullable=False)
    similarity = Column(Float, nullable=False)
    reasons = Column(Text)  # JSON-encoded list of reason strings
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PatternCluster(Base):
    """A detected recurring-problem pattern (feature #8)."""
    __tablename__ = "pattern_clusters"

    id = Column(Integer, primary_key=True, index=True)
    pattern_name = Column(String, nullable=False)
    root_area = Column(String)  # e.g. "/auth/token_manager"
    historical_bug_count = Column(Integer, default=0)
    security_bug_count = Column(Integer, default=0)
    reopened_bug_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GenealogyLink(Base):
    """Links a closed bug to a newer bug believed to share a root cause (feature #10)."""
    __tablename__ = "genealogy_links"

    id = Column(Integer, primary_key=True, index=True)
    original_bug_id = Column(Integer, index=True, nullable=False)
    recurrence_bug_id = Column(Integer, index=True, nullable=False)
    shared_root_cause = Column(String)
    confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
