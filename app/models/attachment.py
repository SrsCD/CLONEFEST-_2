"""
Attachments (screenshots, logs, docs) linked to a bug.

Stores metadata + a file path/URL — actual file storage strategy
(local disk vs. S3-style bucket) is a Phase-6 decision, this model
just needs a stable `storage_path` string either way.
"""
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import TimestampMixin

if TYPE_CHECKING:
    from app.models.bug import Bug
    from app.models.user import User


class Attachment(Base, TimestampMixin):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    bug_id: Mapped[int] = mapped_column(ForeignKey("bugs.id"), nullable=False, index=True)
    uploaded_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)

    bug: Mapped["Bug"] = relationship(back_populates="attachments")
    uploaded_by: Mapped["User"] = relationship()

    def __repr__(self) -> str:
        return f"<Attachment id={self.id} filename={self.filename!r}>"
