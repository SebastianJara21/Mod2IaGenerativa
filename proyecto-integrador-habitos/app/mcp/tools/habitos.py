"""MCP tools for habit management (reuses services/habitos.py business logic)."""

import secrets
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.repositories.usuarios import UsuariosRepository
from app.repositories.habitos import HabitosRepository
from app.services.habitos import (
    crear_habito as crear_habito_service,
    listar_habitos as listar_habitos_service,
    marcar_habito as marcar_habito_service,
    eliminar_habito as eliminar_habito_service,
    FechaFuturaError,
    HabitoNoEncontradoError,
    HabitoNoAutorizadoError,
    YaMarcadoError,
)
from app.services.usuarios import InvalidCredentialsError, get_current_user


# Server-managed confirmation tokens with expiration
# Key: (usuario_id, habito_id), Value: (token, expires_at)
_confirmaciones_pendientes: dict[tuple[int, int], tuple[str, datetime]] = {}


def _limpiar_confirmaciones_expiradas():
    """Remove expired confirmation tokens."""
    ahora = datetime.now()
    expirados = [key for key, (_, expira) in _confirmaciones_pendientes.items() if expira < ahora]
    for key in expirados:
        del _confirmaciones_pendientes[key]


def crear_habito_tool(nombre: str, frecuencia_objetivo: int, token: str, db: Session | None = None) -> dict:
    """Create a new habit for the authenticated user.

    Returns the habit ID, name, target frequency (times per week), and creation timestamp.
    Validates that frequency is between 1-7 times per week.
    """
    if db is None:
        db = SessionLocal()

    try:
        # Authenticate user via token
        repo_usuarios = UsuariosRepository(db)
        usuario = get_current_user(token, repo=repo_usuarios)

        # Create habit via service layer
        repo_habitos = HabitosRepository(db)
        habito = crear_habito_service(
            usuario_id=usuario.id,
            nombre=nombre,
            frecuencia_objetivo=frecuencia_objetivo,
            repo=repo_habitos,
        )

        return {
            "id": habito.id,
            "nombre": habito.nombre,
            "frecuencia_objetivo": habito.frecuencia_objetivo,
            "created_at": habito.created_at.isoformat(),
        }
    except InvalidCredentialsError:
        return {"error": "No autorizado"}
    except IntegrityError:
        return {"error": "Validación: Constraint violation (e.g., frecuencia_objetivo must be 1-7)"}
    except ValueError as e:
        return {"error": f"Validación: {str(e)}"}
    finally:
        if db:
            db.close()


def listar_habitos_tool(token: str, db: Session | None = None) -> dict:
    """List all habits created by the authenticated user.

    Returns an array of habits with ID, name, and target frequency.
    """
    if db is None:
        db = SessionLocal()

    try:
        # Authenticate user via token
        repo_usuarios = UsuariosRepository(db)
        usuario = get_current_user(token, repo=repo_usuarios)

        # List habits via service layer
        repo_habitos = HabitosRepository(db)
        habitos = listar_habitos_service(usuario_id=usuario.id, repo=repo_habitos)

        return {
            "habitos": [
                {
                    "id": h.id,
                    "nombre": h.nombre,
                    "frecuencia_objetivo": h.frecuencia_objetivo,
                }
                for h in habitos
            ]
        }
    except InvalidCredentialsError:
        return {"error": "No autorizado"}
    finally:
        if db:
            db.close()


def marcar_habito_tool(habito_id: int, fecha: str, token: str, db: Session | None = None) -> dict:
    """Mark a habit as completed on a specific date.

    Date must be in ISO format (YYYY-MM-DD) and cannot be in the future.
    Prevents marking the same habit twice on the same day.
    Returns the mark ID, habit ID, and date marked.
    """
    if db is None:
        db = SessionLocal()

    try:
        # Authenticate user via token
        repo_usuarios = UsuariosRepository(db)
        usuario = get_current_user(token, repo=repo_usuarios)

        # Parse fecha
        fecha_obj = date.fromisoformat(fecha)

        # Mark habit via service layer
        repo_habitos = HabitosRepository(db)
        marca = marcar_habito_service(
            usuario_id=usuario.id,
            habito_id=habito_id,
            fecha=fecha_obj,
            repo=repo_habitos,
        )

        return {
            "id": marca.id,
            "habito_id": marca.habito_id,
            "fecha": marca.fecha.isoformat(),
        }
    except InvalidCredentialsError:
        return {"error": "No autorizado"}
    except HabitoNoEncontradoError:
        return {"error": "Hábito no encontrado"}
    except FechaFuturaError as e:
        return {"error": str(e)}
    except YaMarcadoError as e:
        return {"error": str(e)}
    except ValueError as e:
        return {"error": f"Validación: {str(e)}"}
    finally:
        if db:
            db.close()


def eliminar_habito_tool(
    habito_id: int,
    token: str,
    confirmation_token: str | None = None,
    db: Session | None = None,
) -> dict:
    """Delete a habit (requires server-managed two-phase confirmation).

    Phase 1 (no confirmation_token): Returns a confirmation token valid for 60 seconds.
    Phase 2 (with confirmation_token): Executes the deletion.
    Cannot delete habits that belong to other users.
    """
    if db is None:
        db = SessionLocal()

    try:
        # Authenticate user via token
        repo_usuarios = UsuariosRepository(db)
        usuario = get_current_user(token, repo=repo_usuarios)

        # Check if habit exists and belongs to user (without modifying)
        repo_habitos = HabitosRepository(db)
        habito = repo_habitos.get_habito_by_id(habito_id)

        if not habito:
            return {"error": "Hábito no encontrado"}

        if habito.usuario_id != usuario.id:
            return {"error": "No autorizado para eliminar este hábito"}

        # Clean up expired confirmations
        _limpiar_confirmaciones_expiradas()

        # If no confirmation token, request confirmation
        if confirmation_token is None:
            # Generate real random token
            conf_token = secrets.token_hex(16)
            expires_at = datetime.now() + timedelta(seconds=60)
            _confirmaciones_pendientes[(usuario.id, habito_id)] = (conf_token, expires_at)

            return {
                "confirmation_required": True,
                "confirmation_token": conf_token,
                "habito_id": habito_id,
                "message": "Confirmación requerida para eliminar hábito",
            }

        # Verify confirmation token against server-stored value
        key = (usuario.id, habito_id)
        if key not in _confirmaciones_pendientes:
            return {"error": "Confirmación inválida o expirada"}

        stored_token, expires_at = _confirmaciones_pendientes[key]

        # Check expiration
        if datetime.now() > expires_at:
            del _confirmaciones_pendientes[key]
            return {"error": "Confirmación inválida o expirada"}

        # Check token match
        if confirmation_token != stored_token:
            return {"error": "Confirmación inválida o expirada"}

        # Delete token (one-time use only)
        del _confirmaciones_pendientes[key]

        # Execute deletion via service layer
        eliminar_habito_service(
            usuario_id=usuario.id,
            habito_id=habito_id,
            repo=repo_habitos,
        )

        return {
            "deleted": True,
            "habito_id": habito_id,
        }

    except InvalidCredentialsError:
        return {"error": "No autorizado"}
    except ValueError as e:
        return {"error": f"Validación: {str(e)}"}
    finally:
        if db:
            db.close()


def register(mcp) -> None:
    """Registers the MCP tools for habit management on the FastMCP instance.

    Args:
        mcp: FastMCP instance from mcp.server.fastmcp import FastMCP
    """
    @mcp.tool()
    def crear_habito(nombre: str, frecuencia_objetivo: int, token: str) -> dict:
        """Create a new habit for the authenticated user.

        Use when the user wants to set up a new habit to track.
        Returns the habit ID, name, target frequency (times per week), and creation timestamp.
        Validates that frequency is between 1-7 times per week.
        """
        return crear_habito_tool(nombre=nombre, frecuencia_objetivo=frecuencia_objetivo, token=token)

    @mcp.tool()
    def listar_habitos(token: str) -> dict:
        """List all habits created by the authenticated user.

        Use when the user wants to see their habits or get a summary.
        Returns an array of habits with ID, name, and target frequency.
        """
        return listar_habitos_tool(token=token)

    @mcp.tool()
    def marcar_habito(habito_id: int, fecha: str, token: str) -> dict:
        """Mark a habit as completed on a specific date.

        Use when the user completes a habit on a given day.
        Date must be in ISO format (YYYY-MM-DD) and cannot be in the future.
        Prevents marking the same habit twice on the same day.
        Returns the mark ID, habit ID, and date marked.
        """
        return marcar_habito_tool(habito_id=habito_id, fecha=fecha, token=token)

    @mcp.tool()
    def eliminar_habito(habito_id: int, token: str, confirmation_token: str | None = None) -> dict:
        """Delete a habit (requires server-managed two-phase confirmation).

        Use when the user wants to remove a habit. This requires confirmation for safety.

        Phase 1 (no confirmation_token): Returns a confirmation token valid for 60 seconds.
        Phase 2 (with confirmation_token): Executes the deletion.

        Cannot delete habits that belong to other users.
        """
        return eliminar_habito_tool(habito_id=habito_id, token=token, confirmation_token=confirmation_token)
