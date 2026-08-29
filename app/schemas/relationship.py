from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.models.enums import RelationshipType


class RelationshipCreate(BaseModel):
    related_bug_id: int
    relationship_type: RelationshipType
    note: Optional[str] = None


class RelationshipOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    bug_id: int
    related_bug_id: int
    relationship_type: RelationshipType
    note: Optional[str]


class BugDependencies(BaseModel):
    """What Jeet's dependency-intelligence / blast-radius service reads."""
    bug_id: int
    outgoing: list[RelationshipOut]  # relationships where this bug is the source
    incoming: list[RelationshipOut]  # relationships where this bug is the target
