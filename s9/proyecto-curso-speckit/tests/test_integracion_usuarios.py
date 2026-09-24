"""Integration tests for usuario repository (DB persistence).

Per Artículo VII (Testing): Integration tests with in-memory SQLite.
Tests database constraints, unique constraints, timestamps.
Fixtures from conftest.py: test_engine, test_session
"""

import pytest
from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.repositories import usuarios as usuarios_repo


class TestGuardarUsuario:
    """Integration tests for guardar (persist usuario)."""

    def test_guardar_usuario_exitoso(self, test_session: Session):
        """Test usuario persisted with all fields."""
        email = "test@example.com"
        hashed_password = "$2b$12$abcdefghijklmnopqrstuvwxyz"

        resultado = usuarios_repo.guardar(test_session, email, hashed_password)

        assert resultado["id"] is not None
        assert resultado["email"] == email
        assert resultado["created_at"] is not None
        assert "hashed_password" not in resultado

    def test_guardar_usuario_uniqueness(self, test_session: Session):
        """Test unique constraint on email."""
        email = "test@example.com"
        hashed_password = "$2b$12$abcdefghijklmnopqrstuvwxyz"

        # First save succeeds
        usuarios_repo.guardar(test_session, email, hashed_password)

        # Second save with same email fails
        from sqlalchemy.exc import IntegrityError
        with pytest.raises(IntegrityError):
            usuarios_repo.guardar(test_session, email, hashed_password)

    def test_obtener_por_email_exitoso(self, test_session: Session):
        """Test retrieve usuario by email."""
        email = "test@example.com"
        hashed_password = "$2b$12$abcdefghijklmnopqrstuvwxyz"

        usuarios_repo.guardar(test_session, email, hashed_password)

        usuario = usuarios_repo.obtener_por_email(test_session, email)
        assert usuario is not None
        assert usuario.email == email
        assert usuario.hashed_password == hashed_password

    def test_obtener_por_email_no_existe(self, test_session: Session):
        """Test retrieve nonexistent usuario returns None."""
        usuario = usuarios_repo.obtener_por_email(test_session, "nonexistent@example.com")
        assert usuario is None

    def test_obtener_por_id(self, test_session: Session):
        """Test retrieve usuario by ID."""
        email = "test@example.com"
        hashed_password = "$2b$12$abcdefghijklmnopqrstuvwxyz"

        resultado = usuarios_repo.guardar(test_session, email, hashed_password)
        usuario_id = resultado["id"]

        usuario = usuarios_repo.obtener_por_id(test_session, usuario_id)
        assert usuario is not None
        assert usuario.id == usuario_id
        assert usuario.email == email

    def test_obtener_por_id_no_existe(self, test_session: Session):
        """Test retrieve nonexistent usuario by ID returns None."""
        usuario = usuarios_repo.obtener_por_id(test_session, 99999)
        assert usuario is None
