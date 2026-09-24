"""FastAPI dependencies for database sessions and authentication.

Per Artículo II.3 (DIP - Dependency Injection Pattern):
All services receive repositories as parameters with defaults, never imported fixed.
This enables testing without mocking (just inject RepositorioFalso).
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
from app.database import get_db as get_db_session
from app.utils.security import decode_access_token

# OAuth2 scheme: tokenUrl for login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/token")


def get_db() -> Session:
    """Get database session (FastAPI dependency).

    Wraps the sessionmaker get_db for FastAPI dependency injection.
    """
    for db in get_db_session():
        return db


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Extract and validate user from JWT bearer token.

    Per Artículo IV.4 (Autorización):
    Usuario MUST come from JWT token, NEVER from URL/body/query params.

    Per Artículo VIII (Compatibility):
    Returns full Usuario object (not just int), so tests can override
    with lambda: Usuario(...) without type mismatch.

    JWT carries email in "sub" claim (standard OAuth2 pattern).

    Raises:
        HTTPException(401) if token missing, invalid, or user not found
    Returns:
        Usuario object (id, email, hashed_password)
    """
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        email: str = payload.get("sub")  # Standard OAuth2: email in "sub" claim
        if email is None:
            raise credenciales_exception
    except (jwt.InvalidTokenError, jwt.DecodeError, jwt.ExpiredSignatureError):
        raise credenciales_exception

    # Query database to get full Usuario object (allows test override)
    from app.repositories import usuarios as usuarios_repo
    usuario = usuarios_repo.obtener_por_email(db, email)

    if usuario is None:
        raise credenciales_exception

    return usuario


def get_gastos_repo():
    """Get default gastos repository (DIP pattern).

    Returns the production gastos_repository by default,
    but can be overridden in tests with a RepositorioFalso.

    Per Artículo II.3: Services call this to get repo as parameter.
    """
    # Imported here to avoid circular dependency at module load time
    from app.repositories import gastos as gastos_repo_module
    return gastos_repo_module


def get_usuarios_repo():
    """Get default usuarios repository (DIP pattern)."""
    from app.repositories import usuarios as usuarios_repo_module
    return usuarios_repo_module
