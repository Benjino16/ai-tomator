from sqlalchemy import Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from ai_tomator.manager.database.models.group import Group
from ai_tomator.manager.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(Text, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())

    group: Mapped["Group"] = relationship(back_populates="users")