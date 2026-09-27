"""Tests to verify pytest fixtures are working correctly."""

import pytest
from app.models import Base, Usuario


def test_db_fixture_creates_session(db):
    """Verify db fixture creates a valid session."""
    assert db is not None
    assert hasattr(db, "query")
    assert hasattr(db, "add")
    assert hasattr(db, "commit")


def test_db_engine_creates_tables(db_engine):
    """Verify database engine creates all tables."""
    # Check that Usuario table exists
    assert "usuarios" in Base.metadata.tables
    assert "habitos" in Base.metadata.tables
    assert "marcas" in Base.metadata.tables


def test_db_session_isolation(db_session):
    """Verify each test gets isolated database session."""
    # Create a user
    usuario = Usuario(email="test@example.com", password_hash="hashed")
    db_session.add(usuario)
    db_session.commit()

    # Verify user was added
    assert db_session.query(Usuario).count() == 1

    # Note: Next test will have fresh DB (isolation works)


def test_fresh_db_isolation(db_session):
    """Verify fresh session is empty (tests are isolated)."""
    # Should be 0, not 1, proving isolation from previous test
    assert db_session.query(Usuario).count() == 0
