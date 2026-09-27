"""Habitos HTTP routes (REST layer - translates HTTP ↔ services)."""

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.repositories.usuarios import UsuariosRepository
from app.repositories.habitos import HabitosRepository
from app.services.usuarios import get_current_user, InvalidCredentialsError
from app.services.habitos import (
    crear_habito,
    listar_habitos,
    marcar_habito,
    eliminar_habito,
    FechaFuturaError,
    HabitoNoEncontradoError,
    HabitoNoAutorizadoError,
    YaMarcadoError,
)
from app.schemas.habito import HabitoCreate, HabitoResponse, MarcaCreate, MarcaResponse
from app.schemas.usuario import Token

router = APIRouter(tags=["habitos"])


@router.post("/habitos/", response_model=HabitoResponse, status_code=201)
def create_habito(
    habito_data: HabitoCreate,
    db: Session = Depends(get_db),
    authorization: str | None = Header(None),
):
    """Create a new habit (requires authentication)."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")

    try:
        repo_usuarios = UsuariosRepository(db)
        usuario = get_current_user(authorization, repo=repo_usuarios)

        repo_habitos = HabitosRepository(db)
        habito = crear_habito(
            usuario_id=usuario.id,
            nombre=habito_data.nombre,
            frecuencia_objetivo=habito_data.frecuencia_objetivo,
            repo=repo_habitos,
        )
        return habito
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="No autorizado")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/habitos/", response_model=list[HabitoResponse])
def list_habitos(
    db: Session = Depends(get_db),
    authorization: str | None = Header(None),
):
    """List all habits for authenticated user."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")

    try:
        repo_usuarios = UsuariosRepository(db)
        usuario = get_current_user(authorization, repo=repo_usuarios)

        repo_habitos = HabitosRepository(db)
        habitos = listar_habitos(usuario_id=usuario.id, repo=repo_habitos)
        return habitos
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="No autorizado")


@router.post("/habitos/{habito_id}/marcar", response_model=MarcaResponse, status_code=201)
def mark_habito(
    habito_id: int,
    marca_data: MarcaCreate,
    db: Session = Depends(get_db),
    authorization: str | None = Header(None),
):
    """Mark a habit as completed for a specific date."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")

    try:
        repo_usuarios = UsuariosRepository(db)
        usuario = get_current_user(authorization, repo=repo_usuarios)

        repo_habitos = HabitosRepository(db)
        marca = marcar_habito(
            usuario_id=usuario.id,
            habito_id=habito_id,
            fecha=marca_data.fecha,
            repo=repo_habitos,
        )
        return marca
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="No autorizado")
    except FechaFuturaError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HabitoNoEncontradoError:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")
    except YaMarcadoError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/habitos/{habito_id}", status_code=204)
def delete_habito(
    habito_id: int,
    db: Session = Depends(get_db),
    authorization: str | None = Header(None),
):
    """Delete a habit (User Story 4, FR-007)."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")

    try:
        repo_usuarios = UsuariosRepository(db)
        usuario = get_current_user(authorization, repo=repo_usuarios)

        repo_habitos = HabitosRepository(db)
        eliminar_habito(
            usuario_id=usuario.id,
            habito_id=habito_id,
            repo=repo_habitos,
        )
        # 204 No Content response (no body)
        return None
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="No autorizado")
    except HabitoNoAutorizadoError:
        raise HTTPException(status_code=403, detail="No autorizado para eliminar este hábito")
    except HabitoNoEncontradoError:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
