"""Projects and project membership/roles."""
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import String, Text, Boolean, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import TimestampMixin
from app.models.enums import ProjectRole

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.bug import Bug
    from app.models.component import Component
    from app.models.version import Version
    from app.models.milestone import Milestone
    from app.models.label import Label


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    # Short unique code used in bug references, e.g. "IF" -> IF-142
    key: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    members: Mapped[List["ProjectMember"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    bugs: Mapped[List["Bug"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    components: Mapped[List["Component"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    versions: Mapped[List["Version"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    milestones: Mapped[List["Milestone"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    labels: Mapped[List["Label"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} key={self.key!r}>"


class ProjectMember(Base, TimestampMixin):
    __tablename__ = "project_members"
    __table_args__ = (UniqueConstraint("project_id", "user_id", name="uq_project_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    role: Mapped[ProjectRole] = mapped_column(
        SAEnum(ProjectRole, name="project_role"), default=ProjectRole.REPORTER, nullable=False
    )

    project: Mapped["Project"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="project_memberships")

    def __repr__(self) -> str:
        return f"<ProjectMember project_id={self.project_id} user_id={self.user_id} role={self.role}>"
