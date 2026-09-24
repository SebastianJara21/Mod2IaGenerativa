"""Database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import os
from typing import Generator

# Get database URL from environment (SQLite for dev, PostgreSQL for prod)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gastos.db")

# Create engine with appropriate settings per database type
if DATABASE_URL.startswith("sqlite"):
    # SQLite specific: needed for in-memory testing and file-based dev
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    # PostgreSQL or other databases
    engine = create_engine(
        DATABASE_URL,
        echo=False
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency injection for database sessions.

    Yields a SQLAlchemy session for a request and closes it afterwards.
    Used in FastAPI dependency injection (Artículo II.3 - DIP pattern).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
