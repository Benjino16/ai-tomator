# database/base.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


def get_session(db_path: str = "sqlite:///ai_tomator.db"):
    if db_path.startswith("sqlite:///:memory:"):
        # Special handling for in-memory DB
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(db_path, connect_args={"check_same_thread": False})

    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)
