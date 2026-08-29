"""
The Bug model — the core of the entire system.

Field list matches the spec exactly: title, description, reporter,
assignee, severity, priority, status, component, version, milestone,
labels, environment, reproduction steps, expected/actual behaviour,
due date, plus is_security for feature #6 (Security Bug Mode) and
resolved_at/closed_at timestamps for stagnation/statistics logic.
"""
from datetime import date, datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import String, Text, Date, DateTime, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import TimestampMixin
from app.models.enums import BugSeverity, BugPriority, BugStatus
from app.models.label import bug_labels

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User
    from app.models.component import Component
    from app.models.version import Version
    from app.models.milestone import Milestone
    from app.models.label import Label
    from app.models.comment import Comment
    from app.models.attachment import Attachment
    from app.models.history import BugHistory
    from app.models.relationship import BugRelationship


class Bug(Base, TimestampMixin):
    __tablename__ = "bugs"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    assignee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    severity: Mapped[BugSeverity] = mapped_column(
        SAEnum(BugSeverity, name="bug_severity"), default=BugSeverity.MEDIUM, nullable=False
    )
    priority: Mapped[BugPriority] = mapped_column(
        SAEnum(BugPriority, name="bug_priority"), default=BugPriority.P2, nullable=False
    )
    status: Mapped[BugStatus] = mapped_column(
        SAEnum(BugStatus, name="bug_status"), default=BugStatus.NEW, nullable=False, index=True
    )

    component_id: Mapped[Optional[int]] = mapped_column(ForeignKey("components.id"), nullable=True)
    version_id: Mapped[Optional[int]] = mapped_column(ForeignKey("versions.id"), nullable=True)
    milestone_id: Mapped[Optional[int]] = mapped_column(ForeignKey("milestones.id"), nullable=True)

    environment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reproduction_steps: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_behavior: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    actual_behavior: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Feature #6 — Security Bug Mode gate. This backend enforces the
    # visibility restriction; Jeet's service supplies CVSS-style metadata
    # via its own triage endpoint on top of this flag.
    is_security: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="bugs")
    reporter: Mapped["User"] = relationship(back_populates="reported_bugs", foreign_keys=[reporter_id])
    assignee: Mapped[Optional["User"]] = relationship(
        back_populates="assigned_bugs", foreign_keys=[assignee_id]
    )
    component: Mapped[Optional["Component"]] = relationship(back_populates="bugs")
    version: Mapped[Optional["Version"]] = relationship(back_populates="bugs")
    milestone: Mapped[Optional["Milestone"]] = relationship(back_populates="bugs")
    labels: Mapped[List["Label"]] = relationship(secondary=bug_labels, back_populates="bugs")

    comments: Mapped[List["Comment"]] = relationship(
        back_populates="bug", cascade="all, delete-orphan", order_by="Comment.created_at"
    )
    attachments: Mapped[List["Attachment"]] = relationship(
        back_populates="bug", cascade="all, delete-orphan"
    )
    history: Mapped[List["BugHistory"]] = relationship(
        back_populates="bug", cascade="all, delete-orphan", order_by="BugHistory.created_at"
    )

    # Relationships where THIS bug is the source (e.g. this bug "blocks" another)
    outgoing_relationships: Mapped[List["BugRelationship"]] = relationship(
        back_populates="bug",
        foreign_keys="BugRelationship.bug_id",
        cascade="all, delete-orphan",
    )
    # Relationships where this bug is the target (e.g. another bug "blocks" this one)
    incoming_relationships: Mapped[List["BugRelationship"]] = relationship(
        back_populates="related_bug",
        foreign_keys="BugRelationship.related_bug_id",
    )

    def __repr__(self) -> str:
        return f"<Bug id={self.id} title={self.title!r} status={self.status}>"

    # --- Computed convenience properties ---
    # Jeet's AI service (triage/classification, assignment) works on text,
    # not foreign-key IDs — these expose the resolved names alongside the
    # raw *_id fields so his service doesn't need a second lookup call.
    @property
    def reporter_username(self) -> Optional[str]:
        return self.reporter.username if self.reporter else None

    @property
    def assignee_username(self) -> Optional[str]:
        return self.assignee.username if self.assignee else None

    @property
    def component_name(self) -> Optional[str]:
        return self.component.name if self.component else None
