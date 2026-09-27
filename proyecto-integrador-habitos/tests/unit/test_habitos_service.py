"""Unit tests for habitos service (with FakeHabitosRepository)."""

from datetime import date, timedelta
import pytest
from app.models import Habito, Marca
from app.services.habitos import (
    crear_habito,
    listar_habitos,
    marcar_habito,
    eliminar_habito,
    FechaFuturaError,
    HabitoNoEncontradoError,
    HabitoNoAutorizadoError,
    YaMarcadoError,
)


class FakeHabitosRepository:
    """Fake repository for unit testing habitos service."""

    def __init__(self):
        self.habitos = {}  # {id: Habito}
        self.marcas = {}   # {id: Marca}
        self.next_habito_id = 1
        self.next_marca_id = 1

    def save_habito(self, habito: Habito) -> Habito:
        """Save habito (assign ID if new)."""
        if not hasattr(habito, 'id') or habito.id is None:
            habito.id = self.next_habito_id
            self.next_habito_id += 1
        self.habitos[habito.id] = habito
        return habito

    def get_habito_by_id(self, id: int) -> Habito | None:
        """Get habito by ID."""
        return self.habitos.get(id)

    def get_habitos_by_usuario(self, usuario_id: int) -> list[Habito]:
        """Get all habitos for user."""
        return [h for h in self.habitos.values() if h.usuario_id == usuario_id]

    def save_marca(self, marca: Marca) -> Marca:
        """Save marca (assign ID if new)."""
        if not hasattr(marca, 'id') or marca.id is None:
            marca.id = self.next_marca_id
            self.next_marca_id += 1
        self.marcas[marca.id] = marca
        return marca

    def get_marca_by_habito_and_fecha(self, habito_id: int, fecha: date) -> Marca | None:
        """Get marca for habito and fecha."""
        for marca in self.marcas.values():
            if marca.habito_id == habito_id and marca.fecha == fecha:
                return marca
        return None

    def delete_habito(self, habito_id: int) -> None:
        """Delete habito and cascade delete marcas."""
        if habito_id in self.habitos:
            del self.habitos[habito_id]
            # Cascade delete marcas
            self.marcas = {
                id: m for id, m in self.marcas.items()
                if m.habito_id != habito_id
            }


class TestCrearHabito:
    """Unit tests for crear_habito()."""

    def test_crear_habito_success(self):
        """Create habito successfully."""
        repo = FakeHabitosRepository()

        habito = crear_habito(
            usuario_id=1,
            nombre="Ejercicio diario",
            frecuencia_objetivo=5,
            repo=repo,
        )

        assert habito.id == 1
        assert habito.usuario_id == 1
        assert habito.nombre == "Ejercicio diario"
        assert habito.frecuencia_objetivo == 5
        assert habito in repo.habitos.values()

    def test_crear_habito_repo_required(self):
        """repo parameter is required."""
        with pytest.raises(ValueError, match="repo is required"):
            crear_habito(
                usuario_id=1,
                nombre="Test",
                frecuencia_objetivo=3,
                repo=None,
            )


class TestListarHabitos:
    """Unit tests for listar_habitos()."""

    def test_listar_habitos_empty(self):
        """List habitos returns empty for user with no habits."""
        repo = FakeHabitosRepository()

        habitos = listar_habitos(usuario_id=1, repo=repo)
        assert habitos == []

    def test_listar_habitos_multiple(self):
        """List all habitos for a user."""
        repo = FakeHabitosRepository()

        # Create habitos for user 1
        h1 = Habito(usuario_id=1, nombre="Hábito 1", frecuencia_objetivo=3)
        h2 = Habito(usuario_id=1, nombre="Hábito 2", frecuencia_objetivo=5)
        repo.save_habito(h1)
        repo.save_habito(h2)

        # Create habito for user 2 (should not be returned)
        h3 = Habito(usuario_id=2, nombre="Hábito 3", frecuencia_objetivo=2)
        repo.save_habito(h3)

        habitos = listar_habitos(usuario_id=1, repo=repo)
        assert len(habitos) == 2
        assert h1 in habitos
        assert h2 in habitos
        assert h3 not in habitos

    def test_listar_habitos_repo_required(self):
        """repo parameter is required."""
        with pytest.raises(ValueError, match="repo is required"):
            listar_habitos(usuario_id=1, repo=None)


class TestMarcarHabito:
    """Unit tests for marcar_habito()."""

    def test_marcar_habito_success(self):
        """Mark habito successfully for today."""
        repo = FakeHabitosRepository()
        habito = Habito(usuario_id=1, nombre="Test", frecuencia_objetivo=3)
        repo.save_habito(habito)

        marca = marcar_habito(
            usuario_id=1,
            habito_id=habito.id,
            fecha=date.today(),
            repo=repo,
        )

        assert marca.habito_id == habito.id
        assert marca.usuario_id == 1
        assert marca.fecha == date.today()
        assert marca in repo.marcas.values()

    def test_marcar_habito_future_date_error(self):
        """Cannot mark habito for future date (FR-011a)."""
        repo = FakeHabitosRepository()
        habito = Habito(usuario_id=1, nombre="Test", frecuencia_objetivo=3)
        repo.save_habito(habito)

        future_date = date.today() + timedelta(days=1)

        with pytest.raises(FechaFuturaError):
            marcar_habito(
                usuario_id=1,
                habito_id=habito.id,
                fecha=future_date,
                repo=repo,
            )

    def test_marcar_habito_past_date_ok(self):
        """Can mark habito for past date."""
        repo = FakeHabitosRepository()
        habito = Habito(usuario_id=1, nombre="Test", frecuencia_objetivo=3)
        repo.save_habito(habito)

        past_date = date.today() - timedelta(days=1)

        marca = marcar_habito(
            usuario_id=1,
            habito_id=habito.id,
            fecha=past_date,
            repo=repo,
        )

        assert marca.fecha == past_date

    def test_marcar_habito_not_found(self):
        """Error if habito doesn't exist."""
        repo = FakeHabitosRepository()

        with pytest.raises(HabitoNoEncontradoError):
            marcar_habito(
                usuario_id=1,
                habito_id=999,
                fecha=date.today(),
                repo=repo,
            )

    def test_marcar_habito_wrong_user(self):
        """Error if habito belongs to different user."""
        repo = FakeHabitosRepository()
        habito = Habito(usuario_id=2, nombre="Test", frecuencia_objetivo=3)
        repo.save_habito(habito)

        with pytest.raises(HabitoNoEncontradoError):
            marcar_habito(
                usuario_id=1,  # Different user
                habito_id=habito.id,
                fecha=date.today(),
                repo=repo,
            )

    def test_marcar_habito_duplicate_marca(self):
        """Error if habito already marked for that date."""
        repo = FakeHabitosRepository()
        habito = Habito(usuario_id=1, nombre="Test", frecuencia_objetivo=3)
        repo.save_habito(habito)

        # Mark once
        marcar_habito(
            usuario_id=1,
            habito_id=habito.id,
            fecha=date.today(),
            repo=repo,
        )

        # Try to mark again for same date
        with pytest.raises(YaMarcadoError):
            marcar_habito(
                usuario_id=1,
                habito_id=habito.id,
                fecha=date.today(),
                repo=repo,
            )

    def test_marcar_habito_repo_required(self):
        """repo parameter is required."""
        with pytest.raises(ValueError, match="repo is required"):
            marcar_habito(
                usuario_id=1,
                habito_id=1,
                fecha=date.today(),
                repo=None,
            )


class TestEliminarHabito:
    """Unit tests for eliminar_habito()."""

    def test_eliminar_habito_success(self):
        """Delete habito successfully."""
        repo = FakeHabitosRepository()
        habito = Habito(usuario_id=1, nombre="Test", frecuencia_objetivo=3)
        repo.save_habito(habito)

        eliminar_habito(usuario_id=1, habito_id=habito.id, repo=repo)

        # Verify deleted
        assert repo.get_habito_by_id(habito.id) is None

    def test_eliminar_habito_cascades_marcas(self):
        """Deleting habito cascades to marcas."""
        repo = FakeHabitosRepository()
        habito = Habito(usuario_id=1, nombre="Test", frecuencia_objetivo=3)
        repo.save_habito(habito)

        # Create marcas
        marca1 = Marca(habito_id=habito.id, usuario_id=1, fecha=date.today())
        marca2 = Marca(habito_id=habito.id, usuario_id=1, fecha=date.today() - timedelta(days=1))
        repo.save_marca(marca1)
        repo.save_marca(marca2)

        # Delete habito
        eliminar_habito(usuario_id=1, habito_id=habito.id, repo=repo)

        # Verify marcas also deleted
        assert len([m for m in repo.marcas.values() if m.habito_id == habito.id]) == 0

    def test_eliminar_habito_not_found(self):
        """Error if habito doesn't exist."""
        repo = FakeHabitosRepository()

        with pytest.raises(HabitoNoEncontradoError):
            eliminar_habito(usuario_id=1, habito_id=999, repo=repo)

    def test_eliminar_habito_wrong_user(self):
        """Error if habito belongs to different user (403)."""
        repo = FakeHabitosRepository()
        habito = Habito(usuario_id=2, nombre="Test", frecuencia_objetivo=3)
        repo.save_habito(habito)

        with pytest.raises(HabitoNoAutorizadoError):
            eliminar_habito(usuario_id=1, habito_id=habito.id, repo=repo)

    def test_eliminar_habito_repo_required(self):
        """repo parameter is required."""
        with pytest.raises(ValueError, match="repo is required"):
            eliminar_habito(usuario_id=1, habito_id=1, repo=None)
