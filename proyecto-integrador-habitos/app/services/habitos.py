"""Habitos business logic (service layer - no SQLAlchemy imports)."""

from datetime import date
from app.models import Habito, Marca


class FechaFuturaError(Exception):
    """Raised when trying to mark a habit for a future date."""
    pass


class HabitoNoEncontradoError(Exception):
    """Raised when a habit is not found (404)."""
    pass


class HabitoNoAutorizadoError(Exception):
    """Raised when a habit exists but doesn't belong to user (403)."""
    pass


class YaMarcadoError(Exception):
    """Raised when trying to mark a habit that's already marked for that date."""
    pass


def crear_habito(
    usuario_id: int,
    nombre: str,
    frecuencia_objetivo: int,
    repo=None,
) -> Habito:
    """
    Create a new habit for a user.

    Args:
        usuario_id: User ID
        nombre: Habit name
        frecuencia_objetivo: Target frequency (1-7 times per week)
        repo: HabitosRepository instance (dependency injection)

    Returns:
        Created Habito object with assigned ID

    Raises:
        ValueError: If repo is None (required)
    """
    if repo is None:
        raise ValueError("repo is required")

    habito = Habito(
        usuario_id=usuario_id,
        nombre=nombre,
        frecuencia_objetivo=frecuencia_objetivo,
    )
    return repo.save_habito(habito)


def listar_habitos(usuario_id: int, repo=None) -> list[Habito]:
    """
    List all habits for a user.

    Args:
        usuario_id: User ID
        repo: HabitosRepository instance (dependency injection)

    Returns:
        List of Habito objects

    Raises:
        ValueError: If repo is None (required)
    """
    if repo is None:
        raise ValueError("repo is required")

    return repo.get_habitos_by_usuario(usuario_id)


def marcar_habito(
    usuario_id: int,
    habito_id: int,
    fecha: date,
    repo=None,
) -> Marca:
    """
    Mark a habit as completed for a specific date.

    Args:
        usuario_id: User ID
        habito_id: Habit ID
        fecha: Date to mark (FR-011a: must not be in future)
        repo: HabitosRepository instance (dependency injection)

    Returns:
        Created Marca object

    Raises:
        ValueError: If repo is None (required)
        FechaFuturaError: If fecha is in the future (FR-011a)
        HabitoNoEncontradoError: If habito doesn't exist or doesn't belong to user
        YaMarcadoError: If habit already marked for that date
    """
    if repo is None:
        raise ValueError("repo is required")

    # FR-011a: Cannot mark for future dates
    if fecha > date.today():
        raise FechaFuturaError(f"No se puede marcar hábito para fecha futura: {fecha}")

    # Verify habito exists and belongs to user
    habito = repo.get_habito_by_id(habito_id)
    if not habito or habito.usuario_id != usuario_id:
        raise HabitoNoEncontradoError(f"Hábito {habito_id} no encontrado")

    # Check if already marked for this date
    existing_marca = repo.get_marca_by_habito_and_fecha(habito_id, fecha)
    if existing_marca:
        raise YaMarcadoError(f"Hábito ya marcado para {fecha}")

    # Create marca
    marca = Marca(
        habito_id=habito_id,
        usuario_id=usuario_id,
        fecha=fecha,
    )
    return repo.save_marca(marca)


def eliminar_habito(
    usuario_id: int,
    habito_id: int,
    repo=None,
) -> None:
    """
    Delete a habit (User Story 4, FR-007).

    Args:
        usuario_id: User ID
        habito_id: Habit ID to delete
        repo: HabitosRepository instance (dependency injection)

    Raises:
        ValueError: If repo is None (required)
        HabitoNoEncontradoError: If habito doesn't exist (404)
        HabitoNoAutorizadoError: If habito exists but doesn't belong to user (403)
    """
    if repo is None:
        raise ValueError("repo is required")

    # Verify habito exists at all
    habito = repo.get_habito_by_id(habito_id)
    if not habito:
        raise HabitoNoEncontradoError(f"Hábito {habito_id} no encontrado")

    # Verify habito belongs to user
    if habito.usuario_id != usuario_id:
        raise HabitoNoAutorizadoError(f"No autorizado para eliminar hábito {habito_id}")

    # Delete habito (cascades to marcas via FK)
    repo.delete_habito(habito_id)
