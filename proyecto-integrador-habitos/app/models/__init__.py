"""ORM models for database persistence."""

from app.database import Base

# Import models to register them with declarative_base
from app.models.usuario import Usuario  # noqa: F401
from app.models.habito import Habito, Marca  # noqa: F401

__all__ = ["Base", "Usuario", "Habito", "Marca"]
