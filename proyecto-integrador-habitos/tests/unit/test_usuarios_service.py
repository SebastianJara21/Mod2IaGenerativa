"""Unit tests for usuario service with fake repository (DIP pattern, no unittest.mock)."""

import pytest
from app.models import Usuario
from app.services.usuarios import (
    crear_usuario,
    autenticar_usuario,
    get_current_user,
    DuplicateEmailError,
    InvalidCredentialsError,
)
from app.utils.crypto import hash_password


class FakeUsuariosRepository:
    """Fake repository for testing - implements same contract as real repository."""

    def __init__(self):
        self.usuarios = {}
        self.next_id = 1

    def save_usuario(self, usuario: Usuario) -> Usuario:
        """Save usuario and assign ID."""
        if usuario.id is None:
            usuario.id = self.next_id
            self.next_id += 1
        self.usuarios[usuario.id] = usuario
        return usuario

    def get_usuario_by_email(self, email: str) -> Usuario | None:
        """Get usuario by email."""
        for usuario in self.usuarios.values():
            if usuario.email == email:
                return usuario
        return None

    def get_usuario_by_id(self, id: int) -> Usuario | None:
        """Get usuario by ID."""
        return self.usuarios.get(id)


@pytest.fixture
def fake_repo():
    """Provide fake repository for tests."""
    return FakeUsuariosRepository()


def test_crear_usuario_success(fake_repo):
    """Test creating a new user."""
    usuario = crear_usuario("test@example.com", "password123", repo=fake_repo)

    assert usuario.id == 1
    assert usuario.email == "test@example.com"
    assert usuario.password_hash != "password123"  # Should be hashed
    assert len(usuario.password_hash) >= 60  # Bcrypt hash length


def test_crear_usuario_duplicate_email(fake_repo):
    """Test duplicate email rejection (FR-002)."""
    crear_usuario("test@example.com", "password123", repo=fake_repo)

    # Attempt duplicate
    with pytest.raises(DuplicateEmailError):
        crear_usuario("test@example.com", "password456", repo=fake_repo)


def test_autenticar_usuario_success(fake_repo):
    """Test successful authentication returns JWT."""
    crear_usuario("test@example.com", "password123", repo=fake_repo)

    token = autenticar_usuario("test@example.com", "password123", repo=fake_repo)

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0  # JWT tokens are non-empty strings


def test_autenticar_usuario_wrong_password(fake_repo):
    """Test authentication with wrong password."""
    crear_usuario("test@example.com", "password123", repo=fake_repo)

    with pytest.raises(InvalidCredentialsError):
        autenticar_usuario("test@example.com", "wrong_password", repo=fake_repo)


def test_autenticar_usuario_nonexistent_email(fake_repo):
    """Test authentication with non-existent email."""
    with pytest.raises(InvalidCredentialsError):
        autenticar_usuario("nonexistent@example.com", "password123", repo=fake_repo)


def test_get_current_user_valid_token(fake_repo):
    """Test decoding valid JWT token."""
    # Create user and get token
    crear_usuario("test@example.com", "password123", repo=fake_repo)
    token = autenticar_usuario("test@example.com", "password123", repo=fake_repo)

    # Decode token
    usuario = get_current_user(token, repo=fake_repo)

    assert usuario.id == 1
    assert usuario.email == "test@example.com"


def test_get_current_user_invalid_token(fake_repo):
    """Test invalid JWT token rejection."""
    with pytest.raises(InvalidCredentialsError):
        get_current_user("invalid_token", repo=fake_repo)


def test_get_current_user_malformed_token(fake_repo):
    """Test malformed JWT token."""
    with pytest.raises(InvalidCredentialsError):
        get_current_user("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid", repo=fake_repo)


def test_crear_usuario_repo_required():
    """Test that repo parameter is required."""
    with pytest.raises(ValueError):
        crear_usuario("test@example.com", "password123", repo=None)


def test_autenticar_usuario_repo_required():
    """Test that repo parameter is required."""
    with pytest.raises(ValueError):
        autenticar_usuario("test@example.com", "password123", repo=None)


def test_get_current_user_repo_required():
    """Test that repo parameter is required."""
    with pytest.raises(ValueError):
        get_current_user("token", repo=None)
