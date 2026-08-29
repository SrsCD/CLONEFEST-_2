"""
SQLAlchemy engine, session factory, and declarative Base.

Every model in app/models/ imports Base from here.
Every route that touches the DB depends on get_db() for a session.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator

from app.config import settings

# pool_pre_ping avoids "server closed the connection" errors on long-idle
# connections, common with local Postgres during dev.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency — yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
