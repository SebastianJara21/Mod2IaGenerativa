"""Usuario routers: REST API endpoints for user management.

Per Artículo I (Layers): Routers ONLY call services, NO business logic, NO DB access.
Per Artículo V (REST Design): Proper HTTP verbs, status codes, error responses.
Per Artículo VIII (Compatibility): Endpoint signatures match Sessions 6-8 test contracts.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioOut
from app.services import usuarios as usuarios_service


router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def registrar_usuario(
    usuario_data: UsuarioCreate,
    db: Session = Depends(get_db)
) -> UsuarioOut:
    """Register a new user.

    Request body:
    - email: Valid email address (must be unique)
    - password: Non-empty string (will be hashed with bcrypt)

    Responses:
    - 201: User successfully created (returns id, email, created_at)
    - 400: Email already registered (duplicate)
    - 422: Validation error (invalid email format, etc.)

    Per Artículo IV (Security): Password hashed before storage, never exposed
    Per Artículo VIII (Compatibility): POST /usuarios/ endpoint signature locked
    """
    resultado = usuarios_service.registrar_usuario(
        db=db,
        email=usuario_data.email,
        password=usuario_data.password
    )
    return UsuarioOut(**resultado)


@router.post("/token", status_code=status.HTTP_200_OK)
def login(
    usuario_data: UsuarioCreate,
    db: Session = Depends(get_db)
) -> dict:
    """Authenticate user and return JWT access token.

    Request body:
    - email: User email
    - password: User password (verified with bcrypt constant-time comparison)

    Responses:
    - 200: Authentication successful (returns access_token, token_type)
    - 401: Invalid email or password
    - 422: Validation error (invalid email format, etc.)

    Token format:
    - Bearer token (JWT HS256)
    - Contains email in "sub" claim (OAuth2 standard)
    - Expiry: configurable via ACCESS_TOKEN_EXPIRE_MINUTES

    Per Artículo IV (Security): JWT HS256, expiry configurable, SECRET_KEY from .env
    Per Artículo VIII (Compatibility): POST /usuarios/token endpoint signature locked
    """
    token_data = usuarios_service.authenticate_usuario(
        db=db,
        email=usuario_data.email,
        password=usuario_data.password
    )
    return token_data
