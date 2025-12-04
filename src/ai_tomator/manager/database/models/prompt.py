from sqlalchemy.orm import Mapped, mapped_column
from ai_tomator.manager.database.base import Base


class Prompt(Base):
    __tablename__ = "prompts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    prompt: Mapped[str] = mapped_column(nullable=False)

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__mapper__.columns}
