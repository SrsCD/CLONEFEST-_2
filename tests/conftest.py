"""
Shared pytest fixtures.

Each test gets a fresh, isolated in-memory SQLite database (via a
StaticPool-backed connection so the same in-memory DB persists across
the FastAPI dependency-injected sessions within one test). This makes
tests order-independent and safe to run in parallel.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app import models  # noqa: F401 — ensures all tables are registered


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def register_and_login(client, username="alice", email=None):
    email = email or f"{username}@example.com"
    client.post("/auth/register", json={
        "username": username, "email": email, "password": "password123", "full_name": username.title(),
    })
    token = client.post("/auth/login", data={"username": username, "password": "password123"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
