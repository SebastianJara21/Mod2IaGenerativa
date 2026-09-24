"""Usuario services: business logic for user management.

Per Artículo I (Layers): Services contain business logic, NO database imports.
Per Artículo II.3 (DIP): Repository injected as parameter (default: usuarios_repo).
Per Artículo IV (Security): Passwords hashed before storage, never logged.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from datetime import timedelta
from app.utils.security import hash_password, verify_password, create_access_token
from app.config import settings


def registrar_usuario(
    db: Session,
    email: str,
    password: str,
    repo=None
) -> dict:
    """Register a new user.

    Business logic:
    1. Hash password (never store plain text)
    2. Call repo.guardar to persist
    3. Return user data (no password)

    Args:
        db: SQLAlchemy session
        email: User email (must be unique)
        password: Plain-text password (will be hashed)
        repo: Usuario repository (injected, defaults to usuarios_repo)

    Returns:
        Dict with id, email, created_at

    Raises:
        HTTPException(400) if email already registered

    Per Artículo IV: Password hashed with passlib[bcrypt]
    """
    if repo is None:
        from app.repositories import usuarios as usuarios_repo
        repo = usuarios_repo

    # Hash password (never store plain text per Artículo IV)
    hashed_pwd = hash_password(password)

    try:
        # Persist via repository (DIP injection)
        usuario_dict = repo.guardar(db, email, hashed_pwd)
        return usuario_dict
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email duplicado"
        )


def authenticate_usuario(
    db: Session,
    email: str,
    password: str,
    repo=None
) -> dict:
    """Authenticate user and return JWT token.

    Business logic:
    1. Find usuario by email via repo
    2. Verify password (constant-time comparison)
    3. Create JWT token with email in "sub" claim (OAuth2 standard)
    4. Return token

    Args:
        db: SQLAlchemy session
        email: User email
        password: Plain-text password to verify
        repo: Usuario repository (injected, defaults to usuarios_repo)

    Returns:
        Dict with access_token and token_type

    Raises:
        HTTPException(401) if credentials invalid

    Per Artículo IV.2: JWT HS256, expiry configurable
    """
    if repo is None:
        from app.repositories import usuarios as usuarios_repo
        repo = usuarios_repo

    # Find usuario by email
    usuario = repo.obtener_por_email(db, email)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    # Verify password (constant-time comparison per Artículo IV)
    if not verify_password(password, usuario.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    # Create JWT token with email in "sub" claim (OAuth2 standard)
    # Per Artículo VIII (Compatibility): token carries email for get_current_user to decode
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        data={"sub": usuario.email},  # OAuth2 standard: email in "sub"
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
