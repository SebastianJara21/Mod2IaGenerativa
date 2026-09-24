"""API tests for usuario registration and authentication endpoints.

Per Artículo VII (Testing): API tests with FastAPI TestClient.
Tests HTTP contracts: POST /usuarios/, POST /usuarios/token
Fixtures from conftest.py: test_engine, test_session, client
"""

import pytest
from fastapi.testclient import TestClient


class TestRegistroUsuario:
    """API tests for POST /usuarios/ endpoint."""

    def test_registro_exitoso(self, client: TestClient):
        """Test successful user registration (201)."""
        payload = {
            "email": "user1@example.com",
            "password": "securepassword123"
        }

        response = client.post("/usuarios/", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["email"] == "user1@example.com"
        assert data["created_at"] is not None
        assert "password" not in data
        assert "hashed_password" not in data

    def test_registro_email_duplicado(self, client: TestClient):
        """Test registration fails with duplicate email (400)."""
        payload = {
            "email": "user2@example.com",
            "password": "securepassword123"
        }

        # First registration succeeds
        response1 = client.post("/usuarios/", json=payload)
        assert response1.status_code == 201

        # Second registration with same email fails
        response2 = client.post("/usuarios/", json=payload)
        assert response2.status_code == 400
        assert "email duplicado" in response2.json()["detail"]

    def test_registro_email_invalido(self, client: TestClient):
        """Test registration fails with invalid email (422)."""
        payload = {
            "email": "not-an-email",
            "password": "securepassword123"
        }

        response = client.post("/usuarios/", json=payload)
        assert response.status_code == 422

    def test_registro_password_vacio(self, client: TestClient):
        """Test registration fails with empty password (422)."""
        payload = {
            "email": "user3@example.com",
            "password": ""
        }

        response = client.post("/usuarios/", json=payload)
        assert response.status_code == 422

    def test_registro_campos_faltantes(self, client: TestClient):
        """Test registration fails with missing fields (422)."""
        # Missing password
        payload = {"email": "user4@example.com"}
        response = client.post("/usuarios/", json=payload)
        assert response.status_code == 422

        # Missing email
        payload = {"password": "securepassword123"}
        response = client.post("/usuarios/", json=payload)
        assert response.status_code == 422


class TestAuthenticationUsuario:
    """API tests for POST /usuarios/token endpoint."""

    def test_login_exitoso(self, client: TestClient):
        """Test successful authentication (200) returns JWT."""
        # First register a user
        registro_payload = {
            "email": "auth1@example.com",
            "password": "securepassword123"
        }
        client.post("/usuarios/", json=registro_payload)

        # Then authenticate
        response = client.post("/usuarios/token", json=registro_payload)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_email_no_existe(self, client: TestClient):
        """Test authentication fails with nonexistent email (401)."""
        payload = {
            "email": "nonexistent@example.com",
            "password": "anypassword"
        }

        response = client.post("/usuarios/token", json=payload)
        assert response.status_code == 401
        assert "Credenciales inválidas" in response.json()["detail"]

    def test_login_password_incorrecto(self, client: TestClient):
        """Test authentication fails with wrong password (401)."""
        # First register
        registro_payload = {
            "email": "auth2@example.com",
            "password": "securepassword123"
        }
        client.post("/usuarios/", json=registro_payload)

        # Then try with wrong password
        payload = {
            "email": "auth2@example.com",
            "password": "wrongpassword"
        }

        response = client.post("/usuarios/token", json=payload)
        assert response.status_code == 401
        assert "Credenciales inválidas" in response.json()["detail"]

    def test_login_email_invalido(self, client: TestClient):
        """Test authentication fails with invalid email (422)."""
        payload = {
            "email": "not-an-email",
            "password": "anypassword"
        }

        response = client.post("/usuarios/token", json=payload)
        assert response.status_code == 422

    def test_login_campos_faltantes(self, client: TestClient):
        """Test authentication fails with missing fields (422)."""
        # Missing password
        payload = {"email": "auth3@example.com"}
        response = client.post("/usuarios/token", json=payload)
        assert response.status_code == 422

        # Missing email
        payload = {"password": "securepassword123"}
        response = client.post("/usuarios/token", json=payload)
        assert response.status_code == 422
