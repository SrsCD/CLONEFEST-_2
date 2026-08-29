"""
Bug history / audit log.

One row per meaningful change. Stored generically (field_name +
old_value + new_value as strings) so a single table covers every kind
of change instead of needing a column per possible field. Person 3
renders this as the activity feed; Person 4 tests it; Jeet's stagnation
logic reads created_at gaps and action_type from here.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import utcnow
from app.models.enums import HistoryActionType

if TYPE_CHECKING:
    from app.models.bug import Bug
    from app.models.user import User


class BugHistory(Base):
    __tablename__ = "bug_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    bug_id: Mapped[int] = mapped_column(ForeignKey("bugs.id"), nullable=False, index=True)
    changed_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    action_type: Mapped[HistoryActionType] = mapped_column(
        SAEnum(HistoryActionType, name="history_action_type"), nullable=False
    )
    field_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    bug: Mapped["Bug"] = relationship(back_populates="history")
    changed_by: Mapped["User"] = relationship()

    def __repr__(self) -> str:
        return f"<BugHistory bug_id={self.bug_id} action={self.action_type}>"
