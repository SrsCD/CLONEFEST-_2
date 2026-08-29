"""Project milestones (e.g. "Beta launch")."""
from datetime import date
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import String, Date, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import TimestampMixin

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.bug import Bug


class Milestone(Base, TimestampMixin):
    __tablename__ = "milestones"
    __table_args__ = (UniqueConstraint("project_id", "name", name="uq_milestone_project_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    project: Mapped["Project"] = relationship(back_populates="milestones")
    bugs: Mapped[List["Bug"]] = relationship(back_populates="milestone")

    def __repr__(self) -> str:
        return f"<Milestone id={self.id} name={self.name!r}>"
