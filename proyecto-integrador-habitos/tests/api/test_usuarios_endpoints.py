"""API tests for usuario endpoints (uses app.dependency_overrides)."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.database import get_db
from app.routers.usuarios import router as usuarios_router


@pytest.fixture
def app(db_engine, db_session):
    """Create FastAPI app with dependency overrides (tables created by db_engine)."""
    app = FastAPI()
    app.include_router(usuarios_router)

    def override_get_db():
        # Rollback any failed transactions before returning session for next request
        db_session.rollback()
        return db_session

    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest.fixture
def client(app):
    """Create FastAPI test client."""
    return TestClient(app)


def test_post_usuarios_success(client):
    """Test POST /usuarios/ creates user (201)."""
    response = client.post(
        "/usuarios/",
        json={"email": "newuser@example.com", "password": "secure123"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "password" not in data


def test_post_usuarios_duplicate_email(client):
    """Test duplicate email rejection (400)."""
    client.post(
        "/usuarios/",
        json={"email": "duplicate@example.com", "password": "password123"}
    )

    response = client.post(
        "/usuarios/",
        json={"email": "duplicate@example.com", "password": "password456"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "email duplicado"


def test_post_usuarios_invalid_email(client):
    """Test invalid email format (422)."""
    response = client.post(
        "/usuarios/",
        json={"email": "not-an-email", "password": "pass123"}
    )

    assert response.status_code == 422


def test_post_usuarios_short_password(client):
    """Test password too short (422)."""
    response = client.post(
        "/usuarios/",
        json={"email": "test@example.com", "password": "short"}
    )

    assert response.status_code == 422


def test_post_token_success(client):
    """Test POST /usuarios/token returns JWT (200)."""
    client.post(
        "/usuarios/",
        json={"email": "testuser@example.com", "password": "password123"}
    )

    response = client.post(
        "/usuarios/token",
        data={"username": "testuser@example.com", "password": "password123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_post_token_invalid_password(client):
    """Test login with wrong password (401)."""
    client.post(
        "/usuarios/",
        json={"email": "testuser@example.com", "password": "correctpassword"}
    )

    response = client.post(
        "/usuarios/token",
        data={"username": "testuser@example.com", "password": "wrongpassword"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "credenciales inválidas"


def test_post_token_nonexistent_user(client):
    """Test login with non-existent email (401)."""
    response = client.post(
        "/usuarios/token",
        data={"username": "nonexistent@example.com", "password": "pass123"}
    )

    assert response.status_code == 401
