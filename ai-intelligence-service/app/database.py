"""
Our own database for DERIVED data only:
  - similarity scores we've computed
  - pattern clusters we've detected
  - genealogy links we've inferred

We do NOT write into Person 1's core bug DB. We read bug data from them
via API (or webhook/poll — TBD with Person 1) and store our own
intelligence outputs here.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    # Import models here so they register with Base before create_all runs.
    from app import models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
