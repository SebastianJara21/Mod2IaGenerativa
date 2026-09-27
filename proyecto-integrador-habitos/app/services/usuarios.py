"""User authentication and authorization business logic.

Constraint: This service NEVER imports SQLAlchemy, Session, or repositories directly.
Repositories are always injected as parameters (DIP - Dependency Injection Principle).
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from app.models import Usuario
from app.utils.crypto import hash_password, verify_password
from app.config import settings


class DuplicateEmailError(Exception):
    """Raised when attempting to register with existing email."""
    pass


class InvalidCredentialsError(Exception):
    """Raised when login credentials are invalid."""
    pass


def crear_usuario(
    email: str,
    password: str,
    repo=None,  # Injected UsuariosRepository
) -> Usuario:
    """Create a new user account.

    Raises:
        DuplicateEmailError: If email already exists
    """
    # Prevent None repo (would cause error later)
    if repo is None:
        raise ValueError("UsuariosRepository required")

    # Validate business logic (not format - Pydantic handles format)
    if repo.get_usuario_by_email(email) is not None:
        raise DuplicateEmailError(f"Email '{email}' already registered")

    # Create new usuario with hashed password
    usuario = Usuario(
        email=email,
        password_hash=hash_password(password),
    )

    # Persist via repository
    return repo.save_usuario(usuario)


def autenticar_usuario(
    email: str,
    password: str,
    repo=None,  # Injected UsuariosRepository
) -> str:
    """Authenticate user and return JWT token.

    Raises:
        InvalidCredentialsError: If email/password invalid

    Returns:
        JWT token string (access_token)
    """
    if repo is None:
        raise ValueError("UsuariosRepository required")

    # Retrieve user by email
    usuario = repo.get_usuario_by_email(email)
    if usuario is None:
        raise InvalidCredentialsError("Invalid email or password")

    # Verify password
    if not verify_password(password, usuario.password_hash):
        raise InvalidCredentialsError("Invalid email or password")

    # Generate JWT token
    expiration = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(usuario.id),  # Subject: user ID
        "exp": expiration,
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


def get_current_user(
    token: str,
    repo=None,  # Injected UsuariosRepository
) -> Usuario:
    """Decode JWT token and return authenticated user.

    Raises:
        InvalidCredentialsError: If token invalid or expired

    Returns:
        Usuario object
    """
    if repo is None:
        raise ValueError("UsuariosRepository required")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        usuario_id = payload.get("sub")
        if usuario_id is None:
            raise InvalidCredentialsError("Invalid token")
    except jwt.ExpiredSignatureError:
        raise InvalidCredentialsError("Token expired")
    except jwt.InvalidTokenError:
        raise InvalidCredentialsError("Invalid token")

    # Retrieve user
    usuario = repo.get_usuario_by_id(int(usuario_id))
    if usuario is None:
        raise InvalidCredentialsError("User not found")

    return usuario
