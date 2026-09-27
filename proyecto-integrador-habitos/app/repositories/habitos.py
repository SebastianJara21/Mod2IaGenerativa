"""Habitos repository - persistence layer (CRUD operations only, no business logic)."""

from sqlalchemy.orm import Session
from app.models import Habito, Marca


class HabitosRepository:
    """Repository for Habito and Marca persistence."""

    def __init__(self, session: Session):
        self.session = session

    def save_habito(self, habito: Habito) -> Habito:
        """Create and persist new Habito."""
        self.session.add(habito)
        self.session.commit()
        self.session.refresh(habito)
        return habito

    def get_habito_by_id(self, id: int) -> Habito | None:
        """Get Habito by ID."""
        return self.session.query(Habito).filter(Habito.id == id).first()

    def get_habitos_by_usuario(self, usuario_id: int) -> list[Habito]:
        """Get all Habitos for a user."""
        return self.session.query(Habito).filter(Habito.usuario_id == usuario_id).all()

    def save_marca(self, marca: Marca) -> Marca:
        """Create and persist new Marca (habit completion mark)."""
        self.session.add(marca)
        self.session.commit()
        self.session.refresh(marca)
        return marca

    def get_marca_by_habito_and_fecha(self, habito_id: int, fecha) -> Marca | None:
        """Get Marca for specific habito and fecha (to check if already marked)."""
        return self.session.query(Marca).filter(
            Marca.habito_id == habito_id,
            Marca.fecha == fecha
        ).first()

    def delete_habito(self, habito_id: int) -> None:
        """Delete Habito by ID (cascades to Marcas via FK)."""
        # First delete all associated Marcas (manual cascade for SQLite compatibility)
        self.session.query(Marca).filter(Marca.habito_id == habito_id).delete()

        # Then delete the Habito
        habito = self.session.query(Habito).filter(Habito.id == habito_id).first()
        if habito:
            self.session.delete(habito)

        self.session.commit()
