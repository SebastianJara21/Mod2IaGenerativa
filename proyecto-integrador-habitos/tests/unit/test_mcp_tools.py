"""Unit tests for MCP tools (reuses services/habitos.py)."""

from datetime import date, timedelta
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base
from app.models import Usuario, Habito
from app.utils.crypto import hash_password
from app.services.usuarios import autenticar_usuario
from app.repositories.usuarios import UsuariosRepository
from app.repositories.habitos import HabitosRepository
from app.mcp.tools import (
    crear_habito_tool,
    listar_habitos_tool,
    marcar_habito_tool,
    eliminar_habito_tool,
)


@pytest.fixture(scope="function")
def test_db():
    """Create in-memory SQLite engine for tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    yield session
    session.close()


@pytest.fixture
def test_user(test_db):
    """Create test user and return (user, token)."""
    user = Usuario(email="mcp@example.com", password_hash=hash_password("testpass123"))
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    # Generate JWT token
    repo = UsuariosRepository(test_db)
    token = autenticar_usuario("mcp@example.com", "testpass123", repo=repo)

    return user, token


class TestCrearHabitoTool:
    """Tests for crear_habito_tool()."""

    def test_crear_habito_success(self, test_db, test_user):
        """Create habit successfully via MCP tool."""
        user, token = test_user

        result = crear_habito_tool(
            nombre="Ejercicio",
            frecuencia_objetivo=5,
            token=token,
            db=test_db,
        )

        assert "error" not in result
        assert result["nombre"] == "Ejercicio"
        assert result["frecuencia_objetivo"] == 5
        assert "id" in result
        assert "created_at" in result

    def test_crear_habito_invalid_token(self, test_db):
        """Create habit with invalid token fails."""
        result = crear_habito_tool(
            nombre="Test",
            frecuencia_objetivo=3,
            token="invalid.token.format",
            db=test_db,
        )

        assert result == {"error": "No autorizado"}

    def test_crear_habito_invalid_frecuencia(self, test_db, test_user):
        """Create habit with invalid frecuencia fails."""
        user, token = test_user

        result = crear_habito_tool(
            nombre="Test",
            frecuencia_objetivo=10,  # Invalid: > 7
            token=token,
            db=test_db,
        )

        assert "error" in result


class TestListarHabitosTool:
    """Tests for listar_habitos_tool()."""

    def test_listar_habitos_empty(self, test_db, test_user):
        """List habits returns empty if user has no habits."""
        user, token = test_user

        result = listar_habitos_tool(token=token, db=test_db)

        assert "error" not in result
        assert result["habitos"] == []

    def test_listar_habitos_multiple(self, test_db, test_user):
        """List all habits for user via MCP tool."""
        user, token = test_user
        repo = HabitosRepository(test_db)

        # Create 2 habits
        h1 = Habito(usuario_id=user.id, nombre="Habit 1", frecuencia_objetivo=3)
        h2 = Habito(usuario_id=user.id, nombre="Habit 2", frecuencia_objetivo=5)
        repo.save_habito(h1)
        repo.save_habito(h2)

        result = listar_habitos_tool(token=token, db=test_db)

        assert "error" not in result
        assert len(result["habitos"]) == 2
        nombres = {h["nombre"] for h in result["habitos"]}
        assert nombres == {"Habit 1", "Habit 2"}

    def test_listar_habitos_invalid_token(self, test_db):
        """List habits with invalid token fails."""
        result = listar_habitos_tool(token="invalid.token", db=test_db)

        assert result == {"error": "No autorizado"}


class TestMarcarHabitoTool:
    """Tests for marcar_habito_tool()."""

    def test_marcar_habito_success(self, test_db, test_user):
        """Mark habit as completed successfully via MCP tool."""
        user, token = test_user
        repo = HabitosRepository(test_db)

        # Create a habit
        habito = Habito(usuario_id=user.id, nombre="Test", frecuencia_objetivo=3)
        saved = repo.save_habito(habito)
        habito_id = saved.id  # Store ID before session closes in tool

        result = marcar_habito_tool(
            habito_id=habito_id,
            fecha=date.today().isoformat(),
            token=token,
            db=test_db,
        )

        assert "error" not in result
        assert result["habito_id"] == habito_id
        assert result["fecha"] == date.today().isoformat()
        assert "id" in result

    def test_marcar_habito_future_date(self, test_db, test_user):
        """Mark habit for future date fails (FR-011a)."""
        user, token = test_user
        repo = HabitosRepository(test_db)

        habito = Habito(usuario_id=user.id, nombre="Test", frecuencia_objetivo=3)
        saved = repo.save_habito(habito)
        habito_id = saved.id  # Store ID before session closes in tool

        future_date = (date.today() + timedelta(days=1)).isoformat()

        result = marcar_habito_tool(
            habito_id=habito_id,
            fecha=future_date,
            token=token,
            db=test_db,
        )

        assert "error" in result
        assert "futura" in result["error"]

    def test_marcar_habito_not_found(self, test_db, test_user):
        """Mark non-existent habit fails."""
        user, token = test_user

        result = marcar_habito_tool(
            habito_id=999,
            fecha=date.today().isoformat(),
            token=token,
            db=test_db,
        )

        assert result == {"error": "Hábito no encontrado"}


class TestEliminarHabitoTool:
    """Tests for eliminar_habito_tool() - two-phase confirmation."""

    def test_eliminar_habito_request_confirmation(self, test_db, test_user):
        """Request confirmation for deletion (phase 1)."""
        user, token = test_user
        repo = HabitosRepository(test_db)

        habito = Habito(usuario_id=user.id, nombre="Test", frecuencia_objetivo=3)
        saved = repo.save_habito(habito)
        habito_id = saved.id  # Store ID before session closes in tool

        result = eliminar_habito_tool(
            habito_id=habito_id,
            token=token,
            confirmation_token=None,
            db=test_db,
        )

        assert "error" not in result
        assert result["confirmation_required"] is True
        assert "confirmation_token" in result
        assert result["habito_id"] == habito_id

    def test_eliminar_habito_confirm_and_delete(self, test_db, test_user):
        """Confirm and execute deletion (phase 2)."""
        user, token = test_user
        repo = HabitosRepository(test_db)

        habito = Habito(usuario_id=user.id, nombre="Test", frecuencia_objetivo=3)
        saved = repo.save_habito(habito)
        habito_id = saved.id  # Store ID before session closes in tool

        # Phase 1: Request confirmation
        conf_result = eliminar_habito_tool(
            habito_id=habito_id,
            token=token,
            confirmation_token=None,
            db=test_db,
        )

        conf_token = conf_result["confirmation_token"]

        # Phase 2: Confirm and delete
        result = eliminar_habito_tool(
            habito_id=habito_id,
            token=token,
            confirmation_token=conf_token,
            db=test_db,
        )

        assert "error" not in result
        assert result["deleted"] is True
        assert result["habito_id"] == habito_id

        # Verify deleted
        deleted = repo.get_habito_by_id(habito_id)
        assert deleted is None

    def test_eliminar_habito_invalid_confirmation(self, test_db, test_user):
        """Delete with invalid confirmation token fails."""
        user, token = test_user
        repo = HabitosRepository(test_db)

        habito = Habito(usuario_id=user.id, nombre="Test", frecuencia_objetivo=3)
        saved = repo.save_habito(habito)
        habito_id = saved.id  # Store ID before session closes in tool

        result = eliminar_habito_tool(
            habito_id=habito_id,
            token=token,
            confirmation_token="invalid_token",
            db=test_db,
        )

        assert result == {"error": "Confirmación inválida o expirada"}

        # Verify not deleted
        not_deleted = repo.get_habito_by_id(habito_id)
        assert not_deleted is not None

    def test_eliminar_habito_not_found(self, test_db, test_user):
        """Delete non-existent habit fails."""
        user, token = test_user

        result = eliminar_habito_tool(
            habito_id=999,
            token=token,
            confirmation_token=None,
            db=test_db,
        )

        assert result == {"error": "Hábito no encontrado"}

    def test_eliminar_habito_wrong_user(self, test_db, test_user):
        """Delete another user's habit fails (403)."""
        user, token = test_user

        # Create another user with a habit
        other_user = Usuario(email="other@example.com", password_hash=hash_password("pass"))
        test_db.add(other_user)
        test_db.commit()
        test_db.refresh(other_user)

        repo = HabitosRepository(test_db)
        habito = Habito(usuario_id=other_user.id, nombre="Test", frecuencia_objetivo=3)
        saved = repo.save_habito(habito)

        result = eliminar_habito_tool(
            habito_id=saved.id,
            token=token,
            confirmation_token=None,
            db=test_db,
        )

        assert result == {"error": "No autorizado para eliminar este hábito"}

    def test_eliminar_habito_invented_token_rejected(self, test_db, test_user):
        """Invented/guessed confirmation token is rejected (security test)."""
        user, token = test_user
        repo = HabitosRepository(test_db)

        habito = Habito(usuario_id=user.id, nombre="Test", frecuencia_objetivo=3)
        saved = repo.save_habito(habito)
        habito_id = saved.id

        # Try to delete with a made-up token (not from Phase 1)
        result = eliminar_habito_tool(
            habito_id=habito_id,
            token=token,
            confirmation_token="invented_fake_token_12345678",
            db=test_db,
        )

        # Should be rejected
        assert result == {"error": "Confirmación inválida o expirada"}

        # Verify habit NOT deleted
        not_deleted = repo.get_habito_by_id(habito_id)
        assert not_deleted is not None
