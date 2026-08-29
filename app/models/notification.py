"""Notifications backend. Person 3 displays these; this just stores them."""
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import TimestampMixin
from app.models.enums import NotificationType

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.bug import Bug
    from app.models.project import Project


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    type: Mapped[NotificationType] = mapped_column(
        SAEnum(NotificationType, name="notification_type"), nullable=False
    )
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Optional links to what triggered the notification
    bug_id: Mapped[Optional[int]] = mapped_column(ForeignKey("bugs.id"), nullable=True)
    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("projects.id"), nullable=True)

    user: Mapped["User"] = relationship(back_populates="notifications")
    bug: Mapped[Optional["Bug"]] = relationship()
    project: Mapped[Optional["Project"]] = relationship()

    def __repr__(self) -> str:
        return f"<Notification id={self.id} user_id={self.user_id} type={self.type}>"
