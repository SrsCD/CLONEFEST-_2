"""User accounts. Auth endpoints (Phase 3) issue JWTs against this table."""
from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import TimestampMixin

if TYPE_CHECKING:
    from app.models.project import Project, ProjectMember
    from app.models.bug import Bug
    from app.models.comment import Comment
    from app.models.notification import Notification


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Free-text list Jeet's assignment-recommendation logic can read for
    # expertise scoring, e.g. ["auth", "payments", "react"].
    skills: Mapped[str] = mapped_column(String(500), default="", nullable=False)

    # Relationships
    project_memberships: Mapped[List["ProjectMember"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    reported_bugs: Mapped[List["Bug"]] = relationship(
        back_populates="reporter", foreign_keys="Bug.reporter_id"
    )
    assigned_bugs: Mapped[List["Bug"]] = relationship(
        back_populates="assignee", foreign_keys="Bug.assignee_id"
    )
    comments: Mapped[List["Comment"]] = relationship(back_populates="author")
    notifications: Mapped[List["Notification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"
