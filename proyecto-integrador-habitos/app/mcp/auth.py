"""MCP authentication utilities - JWT extraction from Authorization header."""

from app.services.usuarios import get_current_user
from app.repositories.usuarios import UsuariosRepository
from sqlalchemy.orm import Session


def extract_jwt_from_auth_header(auth_header: str | None) -> str | None:
    """
    Extract JWT token from Authorization header (Bearer scheme).

    Args:
        auth_header: HTTP Authorization header value (e.g., "Bearer <token>")

    Returns:
        JWT token string if valid Bearer scheme, None otherwise
    """
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]


def authenticate_mcp_request(
    auth_header: str | None,
    db: Session,
) -> dict | None:
    """
    Authenticate MCP request via JWT token in Authorization header.

    Args:
        auth_header: HTTP Authorization header value
        db: Database session for repository operations

    Returns:
        User dict with id, email if authentication succeeds
        None if authentication fails (no token, invalid token, etc.)
    """
    token = extract_jwt_from_auth_header(auth_header)
    if not token:
        return None

    try:
        repo = UsuariosRepository(db)
        usuario = get_current_user(token, repo=repo)
        return {
            "id": usuario.id,
            "email": usuario.email,
        }
    except Exception:
        # Catches InvalidCredentialsError and other JWT decoding errors
        return None
