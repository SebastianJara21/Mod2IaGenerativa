"""Habito and Marca ORM models for habit tracking."""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from app.database import Base


class Habito(Base):
    """Personal habit (goal) model.

    Attributes:
        id: Primary key, auto-increment
        usuario_id: Foreign key to Usuario (owner)
        nombre: Habit name/description (1-255 chars)
        frecuencia_objetivo: Target frequency in days per week (1-7, CHECK constraint)
        created_at: Habit creation timestamp (UTC)
    """

    __tablename__ = "habitos"
    __table_args__ = (
        CheckConstraint("frecuencia_objetivo >= 1 AND frecuencia_objetivo <= 7"),
    )

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    nombre = Column(String(255), nullable=False)
    frecuencia_objetivo = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Habito(id={self.id}, nombre={self.nombre}, usuario_id={self.usuario_id})>"


class Marca(Base):
    """Habit completion mark (proof of habit done on a specific date).

    Attributes:
        id: Primary key, auto-increment
        habito_id: Foreign key to Habito
        usuario_id: Foreign key to Usuario (denormalized for ownership queries)
        fecha: Date of completion (YYYY-MM-DD, no time)
        created_at: Server timestamp when mark was recorded (UTC)

    Constraints:
        - UNIQUE(habito_id, fecha): Cannot mark same habit twice on same day
    """

    __tablename__ = "marcas"
    __table_args__ = (
        UniqueConstraint("habito_id", "fecha", name="uq_habito_fecha"),
    )

    id = Column(Integer, primary_key=True, index=True)
    habito_id = Column(Integer, ForeignKey("habitos.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    fecha = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Marca(id={self.id}, habito_id={self.habito_id}, fecha={self.fecha})>"
