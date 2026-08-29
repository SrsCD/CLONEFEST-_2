"""Comments on bugs."""
from typing import TYPE_CHECKING

from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import TimestampMixin

if TYPE_CHECKING:
    from app.models.bug import Bug
    from app.models.user import User


class Comment(Base, TimestampMixin):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    bug_id: Mapped[int] = mapped_column(ForeignKey("bugs.id"), nullable=False, index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    bug: Mapped["Bug"] = relationship(back_populates="comments")
    author: Mapped["User"] = relationship(back_populates="comments")

    def __repr__(self) -> str:
        return f"<Comment id={self.id} bug_id={self.bug_id} author_id={self.author_id}>"
