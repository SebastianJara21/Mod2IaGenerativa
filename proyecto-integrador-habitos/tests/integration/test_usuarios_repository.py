"""Integration tests for usuario repository with real in-memory SQLite."""

import pytest
from app.models import Usuario, Base
from app.repositories.usuarios import UsuariosRepository
from app.utils.crypto import hash_password


@pytest.fixture
def repo(db_engine, db_session):
    """Provide real repository with in-memory DB session."""
    return UsuariosRepository(db_session)


def test_save_usuario_new_user(repo, db_session):
    """Test saving a new usuario assigns ID and persists."""
    usuario = Usuario(
        email="test@example.com",
        password_hash=hash_password("password123")
    )

    saved = repo.save_usuario(usuario)

    assert saved.id is not None
    assert saved.id == 1
    assert saved.email == "test@example.com"

    # Verify persisted in DB
    verified = db_session.query(Usuario).filter(Usuario.id == 1).first()
    assert verified is not None
    assert verified.email == "test@example.com"


def test_get_usuario_by_email_exists(repo, db_session):
    """Test retrieving usuario by email when exists."""
    usuario = Usuario(
        email="alice@example.com",
        password_hash=hash_password("secure_password")
    )
    repo.save_usuario(usuario)

    found = repo.get_usuario_by_email("alice@example.com")

    assert found is not None
    assert found.id == usuario.id
    assert found.email == "alice@example.com"


def test_get_usuario_by_email_not_exists(repo):
    """Test retrieving usuario by email when doesn't exist."""
    found = repo.get_usuario_by_email("nonexistent@example.com")

    assert found is None


def test_get_usuario_by_id_exists(repo, db_session):
    """Test retrieving usuario by ID when exists."""
    usuario = Usuario(
        email="bob@example.com",
        password_hash=hash_password("another_password")
    )
    saved = repo.save_usuario(usuario)

    found = repo.get_usuario_by_id(saved.id)

    assert found is not None
    assert found.id == saved.id
    assert found.email == "bob@example.com"


def test_get_usuario_by_id_not_exists(repo):
    """Test retrieving usuario by ID when doesn't exist."""
    found = repo.get_usuario_by_id(9999)

    assert found is None


def test_email_uniqueness_constraint(repo, db_session):
    """Test UNIQUE constraint on email prevents duplicates."""
    usuario1 = Usuario(
        email="unique@example.com",
        password_hash=hash_password("password1")
    )
    repo.save_usuario(usuario1)

    usuario2 = Usuario(
        email="unique@example.com",
        password_hash=hash_password("password2")
    )

    # Attempt to save duplicate email
    with pytest.raises(Exception):  # SQLAlchemy IntegrityError
        repo.save_usuario(usuario2)
        db_session.commit()


def test_multiple_usuarios(repo):
    """Test saving and retrieving multiple usuarios."""
    users = [
        Usuario(email="user1@example.com", password_hash=hash_password("p1")),
        Usuario(email="user2@example.com", password_hash=hash_password("p2")),
        Usuario(email="user3@example.com", password_hash=hash_password("p3")),
    ]

    for user in users:
        repo.save_usuario(user)

    # Verify all are retrievable
    assert repo.get_usuario_by_email("user1@example.com") is not None
    assert repo.get_usuario_by_email("user2@example.com") is not None
    assert repo.get_usuario_by_email("user3@example.com") is not None

    # Verify by ID
    assert repo.get_usuario_by_id(1) is not None
    assert repo.get_usuario_by_id(2) is not None
    assert repo.get_usuario_by_id(3) is not None
