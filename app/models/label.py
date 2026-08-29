"""Labels/tags and the many-to-many link to bugs."""
from typing import List, TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Table, Column, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import TimestampMixin

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.bug import Bug

# Plain association table — a label carries no extra data about the
# bug<->label link itself, so no need for a mapped class here.
bug_labels = Table(
    "bug_labels",
    Base.metadata,
    Column("bug_id", Integer, ForeignKey("bugs.id"), primary_key=True),
    Column("label_id", Integer, ForeignKey("labels.id"), primary_key=True),
)


class Label(Base, TimestampMixin):
    __tablename__ = "labels"
    __table_args__ = (UniqueConstraint("project_id", "name", name="uq_label_project_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    color: Mapped[str] = mapped_column(String(7), default="#808080", nullable=False)  # hex color

    project: Mapped["Project"] = relationship(back_populates="labels")
    bugs: Mapped[List["Bug"]] = relationship(secondary=bug_labels, back_populates="labels")

    def __repr__(self) -> str:
        return f"<Label id={self.id} name={self.name!r}>"
