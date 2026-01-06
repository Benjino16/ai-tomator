from sqlalchemy import Text, ForeignKey, func, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from ai_tomator.manager.database.models.user import User
from ai_tomator.manager.database.base import Base


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())

    users: Mapped[list["User"]] = relationship(
        back_populates="group"
    )
