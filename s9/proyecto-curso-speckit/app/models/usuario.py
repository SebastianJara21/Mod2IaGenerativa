"""Usuario ORM model for authentication and user management.

Per Artículo III (Persistence): SQLAlchemy ORM model with database constraints.
Per Artículo IV (Security): hashed_password stored, never plain text.
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from datetime import datetime
from app.database import Base


class Usuario(Base):
    """User account model.

    Represents a registered user with email and hashed password.
    Email is unique (users cannot share email addresses).
    Timestamps track creation and last update (audit trail).
    """
    __tablename__ = "usuarios"

    # Fields per data-model.md
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Usuario(id={self.id}, email={self.email})>"
