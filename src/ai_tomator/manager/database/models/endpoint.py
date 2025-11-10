from sqlalchemy.orm import Mapped, mapped_column
from ai_tomator.manager.database.base import Base


class Endpoint(Base):
    __tablename__ = "endpoints"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    engine: Mapped[str] = mapped_column(nullable=False)
    url: Mapped[str | None] = mapped_column(nullable=True)
    token: Mapped[str | None] = mapped_column(nullable=True)

    def to_dict_internal(self):
        return {c.key: getattr(self, c.key) for c in self.__mapper__.columns}

    def to_dict_public(self):
        data = self.to_dict_internal()
        token = data.get("token")
        if token and len(token) > 14:
            data["token"] = f"{token[:3]}............{token[-3:]}"
        elif token and len(token) > 7:
            data["token"] = f"{token[:1]}......{token[-1:]}"
        elif token:
            data["token"] = "......"
        return data
