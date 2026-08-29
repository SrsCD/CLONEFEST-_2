"""
Project components (e.g. "Authentication", "Payments").

`owner_id` matters beyond organization: Jeet's assignment-recommendation
logic (#3 in the AI feature list) and code-intelligence (#7) both key off
component ownership, and the pattern/root-cause feature (#8) aggregates
bug counts per component.
"""
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import TimestampMixin

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User
    from app.models.bug import Bug


class Component(Base, TimestampMixin):
    __tablename__ = "components"
    __table_args__ = (UniqueConstraint("project_id", "name", name="uq_component_project_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    project: Mapped["Project"] = relationship(back_populates="components")
    owner: Mapped[Optional["User"]] = relationship()
    bugs: Mapped[List["Bug"]] = relationship(back_populates="component")

    def __repr__(self) -> str:
        return f"<Component id={self.id} name={self.name!r}>"
