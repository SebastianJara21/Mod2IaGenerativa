"""API tests for habitos endpoints."""

from datetime import date, timedelta
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.database import get_db
from app.routers.habitos import router as habitos_router
from app.routers.usuarios import router as usuarios_router
from app.models import Usuario
from app.utils.crypto import hash_password
from app.services.usuarios import autenticar_usuario
from app.repositories.usuarios import UsuariosRepository


@pytest.fixture
def app(db_engine, db_session):
    """Create FastAPI app with dependency overrides."""
    app = FastAPI()
    app.include_router(usuarios_router)
    app.include_router(habitos_router)

    def override_get_db():
        db_session.rollback()
        return db_session

    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest.fixture
def client(app):
    """Create FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def test_user(db_session):
    """Create test user and return (user, token)."""
    user = Usuario(email="habitos@example.com", password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Generate JWT token
    repo = UsuariosRepository(db_session)
    token = autenticar_usuario("habitos@example.com", "password123", repo=repo)

    return user, token


class TestPostHabitos:
    """Tests for POST /habitos/ (create habit)."""

    def test_create_habito_success(self, client, test_user):
        """Create habit successfully (201)."""
        user, token = test_user

        response = client.post(
            "/habitos/",
            json={"nombre": "Ejercicio", "frecuencia_objetivo": 5},
            headers={"Authorization": token},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Ejercicio"
        assert data["frecuencia_objetivo"] == 5
        assert data["usuario_id"] == user.id

    def test_create_habito_no_auth(self, client):
        """Create habit without auth fails (401)."""
        response = client.post(
            "/habitos/",
            json={"nombre": "Test", "frecuencia_objetivo": 3},
        )

        assert response.status_code == 401

    def test_create_habito_invalid_frecuencia(self, client, test_user):
        """Create habit with invalid frecuencia fails (422)."""
        user, token = test_user

        response = client.post(
            "/habitos/",
            json={"nombre": "Test", "frecuencia_objetivo": 10},  # Invalid: > 7
            headers={"Authorization": token},
        )

        assert response.status_code == 422


class TestGetHabitos:
    """Tests for GET /habitos/ (list habits)."""

    def test_list_habitos_empty(self, client, test_user):
        """List habits returns empty if user has no habits."""
        user, token = test_user

        response = client.get("/habitos/", headers={"Authorization": token})

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_list_habitos_multiple(self, client, db_session, test_user):
        """List all habits for user."""
        from app.models import Habito
        from app.repositories.habitos import HabitosRepository

        user, token = test_user
        repo = HabitosRepository(db_session)

        # Create 2 habits
        h1 = Habito(usuario_id=user.id, nombre="Habit 1", frecuencia_objetivo=3)
        h2 = Habito(usuario_id=user.id, nombre="Habit 2", frecuencia_objetivo=5)
        repo.save_habito(h1)
        repo.save_habito(h2)

        response = client.get("/habitos/", headers={"Authorization": token})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        nombres = {h["nombre"] for h in data}
        assert nombres == {"Habit 1", "Habit 2"}

    def test_list_habitos_no_auth(self, client):
        """List habits without auth fails (401)."""
        response = client.get("/habitos/")

        assert response.status_code == 401


class TestPostMarcarHabito:
    """Tests for POST /habitos/{id}/marcar (mark habit completed)."""

    def test_marcar_habito_success(self, client, db_session, test_user):
        """Mark habit as completed successfully (201)."""
        from app.models import Habito
        from app.repositories.habitos import HabitosRepository

        user, token = test_user
        repo = HabitosRepository(db_session)

        # Create a habit
        habito = Habito(usuario_id=user.id, nombre="Test", frecuencia_objetivo=3)
        saved = repo.save_habito(habito)

        response = client.post(
            f"/habitos/{saved.id}/marcar",
            json={"fecha": date.today().isoformat()},
            headers={"Authorization": token},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["habito_id"] == saved.id
        assert data["usuario_id"] == user.id
        assert data["fecha"] == date.today().isoformat()

    def test_marcar_habito_future_date(self, client, db_session, test_user):
        """Mark habit for future date fails (400)."""
        from app.models import Habito
        from app.repositories.habitos import HabitosRepository

        user, token = test_user
        repo = HabitosRepository(db_session)

        habito = Habito(usuario_id=user.id, nombre="Test", frecuencia_objetivo=3)
        saved = repo.save_habito(habito)

        future_date = (date.today() + timedelta(days=1)).isoformat()

        response = client.post(
            f"/habitos/{saved.id}/marcar",
            json={"fecha": future_date},
            headers={"Authorization": token},
        )

        assert response.status_code == 400
        assert "futura" in response.json()["detail"]

    def test_marcar_habito_not_found(self, client, test_user):
        """Mark non-existent habit fails (404)."""
        user, token = test_user

        response = client.post(
            f"/habitos/999/marcar",
            json={"fecha": date.today().isoformat()},
            headers={"Authorization": token},
        )

        assert response.status_code == 404

    def test_marcar_habito_duplicate(self, client, db_session, test_user):
        """Mark habit twice for same date fails (400)."""
        from app.models import Habito
        from app.repositories.habitos import HabitosRepository

        user, token = test_user
        repo = HabitosRepository(db_session)

        habito = Habito(usuario_id=user.id, nombre="Test", frecuencia_objetivo=3)
        saved = repo.save_habito(habito)

        # Mark once
        client.post(
            f"/habitos/{saved.id}/marcar",
            json={"fecha": date.today().isoformat()},
            headers={"Authorization": token},
        )

        # Try to mark again
        response = client.post(
            f"/habitos/{saved.id}/marcar",
            json={"fecha": date.today().isoformat()},
            headers={"Authorization": token},
        )

        assert response.status_code == 400
        assert "ya marcado" in response.json()["detail"].lower()

    def test_marcar_habito_no_auth(self, client):
        """Mark habit without auth fails (401)."""
        response = client.post(
            "/habitos/1/marcar",
            json={"fecha": date.today().isoformat()},
        )

        assert response.status_code == 401


class TestDeleteHabito:
    """Tests for DELETE /habitos/{id} (delete habit)."""

    def test_delete_habito_success(self, client, db_session, test_user):
        """Delete habit successfully (204)."""
        from app.models import Habito
        from app.repositories.habitos import HabitosRepository

        user, token = test_user
        repo = HabitosRepository(db_session)

        # Create a habit
        habito = Habito(usuario_id=user.id, nombre="Test", frecuencia_objetivo=3)
        saved = repo.save_habito(habito)

        response = client.delete(
            f"/habitos/{saved.id}",
            headers={"Authorization": token},
        )

        assert response.status_code == 204

        # Verify deleted
        deleted = repo.get_habito_by_id(saved.id)
        assert deleted is None

    def test_delete_habito_not_found(self, client, test_user):
        """Delete non-existent habit fails (404)."""
        user, token = test_user

        response = client.delete(
            "/habitos/999",
            headers={"Authorization": token},
        )

        assert response.status_code == 404

    def test_delete_habito_wrong_user(self, client, db_session, test_user):
        """Delete habit of another user fails (403 - unauthorized)."""
        from app.models import Usuario, Habito
        from app.repositories.habitos import HabitosRepository

        user, token = test_user

        # Create another user with a habit
        other_user = Usuario(email="other@example.com", password_hash="hashedpass")
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)

        repo = HabitosRepository(db_session)
        habito = Habito(usuario_id=other_user.id, nombre="Test", frecuencia_objetivo=3)
        saved = repo.save_habito(habito)

        response = client.delete(
            f"/habitos/{saved.id}",
            headers={"Authorization": token},
        )

        assert response.status_code == 403
        assert "autorizado" in response.json()["detail"].lower()

    def test_delete_habito_no_auth(self, client):
        """Delete habit without auth fails (401)."""
        response = client.delete("/habitos/1")

        assert response.status_code == 401
