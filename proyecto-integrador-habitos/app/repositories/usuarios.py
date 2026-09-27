"""Real usuario repository for database persistence.

This layer is the ONLY layer authorized to read/write the database.
No business logic here - only CRUD operations.
"""

from sqlalchemy.orm import Session
from app.models import Usuario


class UsuariosRepository:
    """Real repository for usuario persistence via SQLAlchemy."""

    def __init__(self, session: Session):
        """Initialize with database session.

        Args:
            session: SQLAlchemy Session for DB operations
        """
        self.session = session

    def save_usuario(self, usuario: Usuario) -> Usuario:
        """Save (insert or update) usuario to database.

        Args:
            usuario: Usuario ORM object

        Returns:
            Saved usuario with ID assigned
        """
        self.session.add(usuario)
        self.session.commit()
        self.session.refresh(usuario)  # Refresh to get assigned ID
        return usuario

    def get_usuario_by_email(self, email: str) -> Usuario | None:
        """Retrieve usuario by email (Constraint: email is UNIQUE).

        Args:
            email: Email address to search

        Returns:
            Usuario if found, None otherwise
        """
        return self.session.query(Usuario).filter(Usuario.email == email).first()

    def get_usuario_by_id(self, id: int) -> Usuario | None:
        """Retrieve usuario by ID (Primary key lookup).

        Args:
            id: Usuario ID

        Returns:
            Usuario if found, None otherwise
        """
        return self.session.query(Usuario).filter(Usuario.id == id).first()


# Default instance for dependency injection
usuarios_repository = UsuariosRepository
