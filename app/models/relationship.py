"""
Bug-to-bug relationships: duplicate_of, blocks, blocked_by, related_to,
depends_on.

Person 2 (this backend) owns storing/managing these. Jeet's service
reads them for dependency intelligence (#4) and blast-radius (#11) —
that's the exact "even a simple blocks: [bug_ids] field is enough"
requirement from his PROGRESS.md, satisfied by this table plus the
GET /bugs/{id}/dependencies endpoint (Phase 9).
"""
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, Enum as SAEnum, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import TimestampMixin
from app.models.enums import RelationshipType

if TYPE_CHECKING:
    from app.models.bug import Bug
    from app.models.user import User


class BugRelationship(Base, TimestampMixin):
    __tablename__ = "bug_relationships"
    __table_args__ = (
        UniqueConstraint(
            "bug_id", "related_bug_id", "relationship_type", name="uq_bug_relationship"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    bug_id: Mapped[int] = mapped_column(ForeignKey("bugs.id"), nullable=False, index=True)
    related_bug_id: Mapped[int] = mapped_column(ForeignKey("bugs.id"), nullable=False, index=True)
    relationship_type: Mapped[RelationshipType] = mapped_column(
        SAEnum(RelationshipType, name="bug_relationship_type"), nullable=False
    )
    created_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    bug: Mapped["Bug"] = relationship(
        back_populates="outgoing_relationships", foreign_keys=[bug_id]
    )
    related_bug: Mapped["Bug"] = relationship(
        back_populates="incoming_relationships", foreign_keys=[related_bug_id]
    )
    created_by: Mapped[Optional["User"]] = relationship()

    def __repr__(self) -> str:
        return f"<BugRelationship {self.bug_id} -{self.relationship_type}-> {self.related_bug_id}>"
