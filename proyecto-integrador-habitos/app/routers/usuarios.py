"""Usuario HTTP routes (REST layer - translates HTTP ↔ services)."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.repositories.usuarios import UsuariosRepository
from app.services.usuarios import (
    crear_usuario,
    autenticar_usuario,
    DuplicateEmailError,
    InvalidCredentialsError,
)
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, Token

router = APIRouter(tags=["usuarios"])


@router.post("/usuarios/", response_model=UsuarioResponse, status_code=201)
def register_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
):
    """Register a new user (FR-001, FR-002)."""
    try:
        repo = UsuariosRepository(db)
        created = crear_usuario(usuario.email, usuario.password, repo=repo)
        return created
    except DuplicateEmailError:
        raise HTTPException(status_code=400, detail="email duplicado")


@router.post("/usuarios/token", response_model=Token)
def login_usuario(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticate user and return JWT token (FR-003, Artículo IV.2: OAuth2 password flow)."""
    try:
        repo = UsuariosRepository(db)
        token = autenticar_usuario(form_data.username, form_data.password, repo=repo)
        return Token(access_token=token)
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="credenciales inválidas")
