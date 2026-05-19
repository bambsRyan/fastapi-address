"""Database engine and session dependency."""

from sqlmodel import create_engine, Session
from .core.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})


def get_db():
    """FastAPI dependency that provides a database session per request and closes it when done."""
    with Session(engine) as session:
        yield session
