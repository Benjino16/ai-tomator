from sqlalchemy.orm import Mapped, mapped_column

class RunDataMixin:
    engine: Mapped[str] = mapped_column(nullable=False)
    endpoint: Mapped[str] = mapped_column(nullable=False)
    file_reader: Mapped[str] = mapped_column(nullable=False)
    prompt: Mapped[str] = mapped_column(nullable=False)
    model: Mapped[str] = mapped_column(nullable=False)
    temperature: Mapped[float] = mapped_column(nullable=False)
