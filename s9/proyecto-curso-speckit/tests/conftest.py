"""Pytest configuration and shared fixtures for all tests."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient


@pytest.fixture
def test_engine():
    """Create an in-memory SQLite engine for tests.

    Uses StaticPool to ensure all connections share the same SQLite database.
    Without this, each new connection opens a separate empty in-memory DB.
    """
    from app.database import Base
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_session(test_engine):
    """Create a test database session."""
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def client(test_session: Session, test_engine, monkeypatch):
    """FastAPI TestClient with test database."""
    import app.database
    from app.database import Base, get_db

    # Permanently patch the engine for this test
    monkeypatch.setattr("app.database.engine", test_engine)

    # Ensure tables are created on the test engine
    Base.metadata.create_all(bind=test_engine)

    from app.main import create_app
    app_instance = create_app()

    # Override get_db to use test session
    def override_get_db():
        yield test_session

    app_instance.dependency_overrides[get_db] = override_get_db
    return TestClient(app_instance)
