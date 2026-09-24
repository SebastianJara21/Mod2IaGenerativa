"""Usuario repository: database persistence layer.

Per Artículo I (Layers): repositories ONLY read/write DB, NO business logic.
Per Artículo VIII (Compatibility): Module with functions (not class).
Functions must match exact signatures from Sessions 6-8 tests.
"""

from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from typing import Optional, Dict, Any


def guardar(db: Session, email: str, hashed_password: str) -> Dict[str, Any]:
    """Create and persist a new usuario.

    Args:
        db: SQLAlchemy session
        email: User email (must be unique)
        hashed_password: Bcrypt-hashed password

    Returns:
        Dict with id, email, created_at (no hashed_password exposed)

    Raises:
        sqlalchemy.exc.IntegrityError if email not unique
    """
    usuario = Usuario(email=email, hashed_password=hashed_password)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return {
        "id": usuario.id,
        "email": usuario.email,
        "created_at": usuario.created_at
    }


def obtener_por_email(db: Session, email: str) -> Optional[Usuario]:
    """Retrieve usuario by email address.

    Args:
        db: SQLAlchemy session
        email: Email to search for

    Returns:
        Usuario object if found, None otherwise

    Used by: authenticate_usuario, get_current_user
    """
    return db.query(Usuario).filter(Usuario.email == email).first()


def obtener_por_id(db: Session, usuario_id: int) -> Optional[Usuario]:
    """Retrieve usuario by ID.

    Args:
        db: SQLAlchemy session
        usuario_id: User ID

    Returns:
        Usuario object if found, None otherwise
    """
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()
