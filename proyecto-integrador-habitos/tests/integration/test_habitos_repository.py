"""Integration tests for habitos repository (with real SQLite in-memory DB)."""

from datetime import date, timedelta
import pytest
from app.models import Habito, Marca, Usuario
from app.repositories.habitos import HabitosRepository
from app.utils.crypto import hash_password


@pytest.fixture
def usuario(db):
    """Create test user."""
    user = Usuario(email="habitos@example.com", password_hash=hash_password("testpass123"))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestSaveHabito:
    """Integration tests for save_habito()."""

    def test_save_habito_new(self, db, usuario):
        """Save new habito and get assigned ID."""
        repo = HabitosRepository(db)

        habito = Habito(
            usuario_id=usuario.id,
            nombre="Ejercicio matutino",
            frecuencia_objetivo=5,
        )

        result = repo.save_habito(habito)

        assert result.id is not None
        assert result.usuario_id == usuario.id
        assert result.nombre == "Ejercicio matutino"
        assert result.frecuencia_objetivo == 5

    def test_save_habito_persisted(self, db, usuario):
        """Saved habito is persisted to DB."""
        repo = HabitosRepository(db)

        habito = Habito(usuario_id=usuario.id, nombre="Test", frecuencia_objetivo=3)
        saved = repo.save_habito(habito)

        # Query again to verify persistence
        retrieved = repo.get_habito_by_id(saved.id)
        assert retrieved is not None
        assert retrieved.nombre == "Test"


class TestGetHabitoById:
    """Integration tests for get_habito_by_id()."""

    def test_get_habito_exists(self, db, usuario):
        """Get existing habito by ID."""
        repo = HabitosRepository(db)

        habito = Habito(usuario_id=usuario.id, nombre="Test", frecuencia_objetivo=4)
        saved = repo.save_habito(habito)

        retrieved = repo.get_habito_by_id(saved.id)
        assert retrieved is not None
        assert retrieved.id == saved.id
        assert retrieved.nombre == "Test"

    def test_get_habito_not_exists(self, db):
        """Get non-existent habito returns None."""
        repo = HabitosRepository(db)

        retrieved = repo.get_habito_by_id(999)
        assert retrieved is None


class TestGetHabitosByUsuario:
    """Integration tests for get_habitos_by_usuario()."""

    def test_get_habitos_empty(self, db, usuario):
        """Get habitos returns empty if user has no habits."""
        repo = HabitosRepository(db)

        habitos = repo.get_habitos_by_usuario(usuario.id)
        assert habitos == []

    def test_get_habitos_multiple(self, db, usuario):
        """Get all habitos for user."""
        repo = HabitosRepository(db)

        h1 = Habito(usuario_id=usuario.id, nombre="Hábito 1", frecuencia_objetivo=3)
        h2 = Habito(usuario_id=usuario.id, nombre="Hábito 2", frecuencia_objetivo=5)
        repo.save_habito(h1)
        repo.save_habito(h2)

        habitos = repo.get_habitos_by_usuario(usuario.id)
        assert len(habitos) == 2

    def test_get_habitos_filters_by_usuario(self, db, usuario):
        """Get habitos only returns habits for specified user."""
        repo = HabitosRepository(db)

        # Create another user
        user2 = Usuario(email="other@example.com", password_hash=hash_password("pass123"))
        db.add(user2)
        db.commit()
        db.refresh(user2)

        # Create habitos for both users
        h1 = Habito(usuario_id=usuario.id, nombre="User1 habit", frecuencia_objetivo=3)
        h2 = Habito(usuario_id=user2.id, nombre="User2 habit", frecuencia_objetivo=4)
        repo.save_habito(h1)
        repo.save_habito(h2)

        user1_habitos = repo.get_habitos_by_usuario(usuario.id)
        user2_habitos = repo.get_habitos_by_usuario(user2.id)

        assert len(user1_habitos) == 1
        assert len(user2_habitos) == 1
        assert user1_habitos[0].nombre == "User1 habit"
        assert user2_habitos[0].nombre == "User2 habit"


class TestSaveMarca:
    """Integration tests for save_marca()."""

    def test_save_marca_new(self, db, usuario):
        """Save new marca and get assigned ID."""
        repo = HabitosRepository(db)

        habito = Habito(usuario_id=usuario.id, nombre="Test", frecuencia_objetivo=3)
        saved_habito = repo.save_habito(habito)

        marca = Marca(
            habito_id=saved_habito.id,
            usuario_id=usuario.id,
            fecha=date.today(),
        )

        result = repo.save_marca(marca)

        assert result.id is not None
        assert result.habito_id == saved_habito.id
        assert result.usuario_id == usuario.id
        assert result.fecha == date.today()

    def test_save_marca_persisted(self, db, usuario):
        """Saved marca is persisted to DB."""
        repo = HabitosRepository(db)

        habito = Habito(usuario_id=usuario.id, nombre="Test", frecuencia_objetivo=3)
        saved_habito = repo.save_habito(habito)

        marca = Marca(habito_id=saved_habito.id, usuario_id=usuario.id, fecha=date.today())
        saved_marca = repo.save_marca(marca)

        # Query again to verify persistence
        retrieved = repo.get_marca_by_habito_and_fecha(saved_habito.id, date.today())
        assert retrieved is not None
        assert retrieved.id == saved_marca.id


class TestGetMarcaByHabitoAndFecha:
    """Integration tests for get_marca_by_habito_and_fecha()."""

    def test_get_marca_exists(self, db, usuario):
        """Get existing marca by habito and fecha."""
        repo = HabitosRepository(db)

        habito = Habito(usuario_id=usuario.id, nombre="Test", frecuencia_objetivo=3)
        saved_habito = repo.save_habito(habito)

        marca = Marca(habito_id=saved_habito.id, usuario_id=usuario.id, fecha=date.today())
        repo.save_marca(marca)

        retrieved = repo.get_marca_by_habito_and_fecha(saved_habito.id, date.today())
        assert retrieved is not None
        assert retrieved.fecha == date.today()

    def test_get_marca_not_exists(self, db, usuario):
        """Get non-existent marca returns None."""
        repo = HabitosRepository(db)

        habito = Habito(usuario_id=usuario.id, nombre="Test", frecuencia_objetivo=3)
        saved_habito = repo.save_habito(habito)

        retrieved = repo.get_marca_by_habito_and_fecha(saved_habito.id, date.today())
        assert retrieved is None

    def test_get_marca_different_dates(self, db, usuario):
        """Marca query is specific to date."""
        repo = HabitosRepository(db)

        habito = Habito(usuario_id=usuario.id, nombre="Test", frecuencia_objetivo=3)
        saved_habito = repo.save_habito(habito)

        # Mark today
        marca1 = Marca(habito_id=saved_habito.id, usuario_id=usuario.id, fecha=date.today())
        repo.save_marca(marca1)

        # Query for different date
        from datetime import timedelta
        past_date = date.today() - timedelta(days=1)
        retrieved = repo.get_marca_by_habito_and_fecha(saved_habito.id, past_date)
        assert retrieved is None


class TestDeleteHabito:
    """Integration tests for delete_habito()."""

    def test_delete_habito_success(self, db, usuario):
        """Delete habito successfully."""
        repo = HabitosRepository(db)

        habito = Habito(usuario_id=usuario.id, nombre="Test", frecuencia_objetivo=3)
        saved = repo.save_habito(habito)

        # Delete
        repo.delete_habito(saved.id)

        # Verify deleted
        retrieved = repo.get_habito_by_id(saved.id)
        assert retrieved is None

    def test_delete_habito_cascades_marcas(self, db, usuario):
        """Deleting habito cascades to marcas."""
        repo = HabitosRepository(db)

        habito = Habito(usuario_id=usuario.id, nombre="Test", frecuencia_objetivo=3)
        saved_habito = repo.save_habito(habito)

        # Create marcas
        marca1 = Marca(habito_id=saved_habito.id, usuario_id=usuario.id, fecha=date.today())
        marca2 = Marca(habito_id=saved_habito.id, usuario_id=usuario.id, fecha=date.today() - timedelta(days=1))
        repo.save_marca(marca1)
        repo.save_marca(marca2)

        # Delete habito
        repo.delete_habito(saved_habito.id)

        # Verify marcas also deleted
        retrieved = db.query(Marca).filter(Marca.habito_id == saved_habito.id).all()
        assert len(retrieved) == 0

    def test_delete_habito_nonexistent(self, db):
        """Deleting non-existent habito doesn't error."""
        repo = HabitosRepository(db)

        # Should not raise an error
        repo.delete_habito(999)
