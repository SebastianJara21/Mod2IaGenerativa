"""Usuario ORM model for user authentication."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base


class Usuario(Base):
    """User account model.

    Attributes:
        id: Primary key, auto-increment
        email: Unique email address (EmailStr validated by Pydantic)
        password_hash: Hashed password (bcrypt output, ~60 chars)
        created_at: Account creation timestamp (UTC)
    """

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(254), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Usuario(id={self.id}, email={self.email})>"
