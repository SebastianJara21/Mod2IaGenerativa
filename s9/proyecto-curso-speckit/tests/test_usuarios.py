"""Unit tests for usuario services (registrar_usuario, authenticate_usuario).

Per Artículo VII (Testing): Unit tests with ≥90% services coverage.
Uses in-memory SQLite for isolation, mocks repo for pure service logic.
Fixtures from conftest.py: test_engine, test_session
"""

import pytest
from app.models.usuario import Usuario
from sqlalchemy.orm import Session
from app.services import usuarios as usuarios_service
from app.repositories import usuarios as usuarios_repo
from app.utils.security import hash_password, verify_password
from fastapi import HTTPException


class TestRegistrarUsuario:
    """Unit tests for registrar_usuario service."""

    def test_registrar_usuario_exitoso(self, test_session: Session):
        """Test successful user registration."""
        email = "test@example.com"
        password = "securepassword123"

        resultado = usuarios_service.registrar_usuario(
            db=test_session,
            email=email,
            password=password,
            repo=usuarios_repo
        )

        assert resultado["id"] is not None
        assert resultado["email"] == email
        assert resultado["created_at"] is not None
        assert "hashed_password" not in resultado  # Never expose password

    def test_registrar_usuario_email_duplicado(self, test_session: Session):
        """Test registration fails with duplicate email (400)."""
        email = "test@example.com"
        password = "securepassword123"

        # First registration succeeds
        usuarios_service.registrar_usuario(
            db=test_session,
            email=email,
            password=password,
            repo=usuarios_repo
        )

        # Second registration with same email fails
        with pytest.raises(HTTPException) as exc_info:
            usuarios_service.registrar_usuario(
                db=test_session,
                email=email,
                password=password,
                repo=usuarios_repo
            )

        assert exc_info.value.status_code == 400
        assert "email duplicado" in exc_info.value.detail

    def test_password_hasheado(self, test_session: Session):
        """Verify password is hashed before storage (bcrypt)."""
        email = "test@example.com"
        password = "securepassword123"

        usuarios_service.registrar_usuario(
            db=test_session,
            email=email,
            password=password,
            repo=usuarios_repo
        )

        # Retrieve from DB and verify password is hashed
        usuario = usuarios_repo.obtener_por_email(test_session, email)
        assert usuario.hashed_password != password
        assert usuario.hashed_password.startswith("$2b$")  # bcrypt prefix


class TestAuthenticateUsuario:
    """Unit tests for authenticate_usuario service."""

    def test_authenticate_exitoso(self, test_session: Session):
        """Test successful authentication returns JWT token."""
        email = "test@example.com"
        password = "securepassword123"

        # Register user first
        usuarios_service.registrar_usuario(
            db=test_session,
            email=email,
            password=password,
            repo=usuarios_repo
        )

        # Authenticate
        resultado = usuarios_service.authenticate_usuario(
            db=test_session,
            email=email,
            password=password,
            repo=usuarios_repo
        )

        assert "access_token" in resultado
        assert resultado["token_type"] == "bearer"
        assert len(resultado["access_token"]) > 0

    def test_authenticate_email_no_existe(self, test_session: Session):
        """Test authentication fails with nonexistent email (401)."""
        with pytest.raises(HTTPException) as exc_info:
            usuarios_service.authenticate_usuario(
                db=test_session,
                email="nonexistent@example.com",
                password="anypassword",
                repo=usuarios_repo
            )

        assert exc_info.value.status_code == 401
        assert "Credenciales inválidas" in exc_info.value.detail

    def test_authenticate_password_incorrecto(self, test_session: Session):
        """Test authentication fails with wrong password (401)."""
        email = "test@example.com"
        password = "securepassword123"

        # Register user
        usuarios_service.registrar_usuario(
            db=test_session,
            email=email,
            password=password,
            repo=usuarios_repo
        )

        # Try to authenticate with wrong password
        with pytest.raises(HTTPException) as exc_info:
            usuarios_service.authenticate_usuario(
                db=test_session,
                email=email,
                password="wrongpassword",
                repo=usuarios_repo
            )

        assert exc_info.value.status_code == 401
        assert "Credenciales inválidas" in exc_info.value.detail
