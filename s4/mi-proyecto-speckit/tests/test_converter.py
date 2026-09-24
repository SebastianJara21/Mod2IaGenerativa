"""Pruebas del conversor de temperatura frente a los requisitos funcionales
FR-001 a FR-008 de specs/001-conversor-temperatura/spec.md.
"""

import pytest

from conversor_temperatura.converter import Unit, convertir, parse_unidad, parse_valor


# US1 — Convertir temperatura entre unidades (FR-001 a FR-004)
class TestConversionEntreUnidades:
    def test_celsius_a_fahrenheit(self):
        assert convertir(100, Unit.CELSIUS, Unit.FAHRENHEIT) == 212.0

    def test_fahrenheit_a_celsius(self):
        assert convertir(212, Unit.FAHRENHEIT, Unit.CELSIUS) == 100.0

    def test_celsius_a_kelvin(self):
        assert convertir(0, Unit.CELSIUS, Unit.KELVIN) == 273.15

    def test_kelvin_a_celsius(self):
        assert convertir(273.15, Unit.KELVIN, Unit.CELSIUS) == 0.0

    def test_fahrenheit_a_kelvin(self):
        assert convertir(32, Unit.FAHRENHEIT, Unit.KELVIN) == 273.15

    def test_kelvin_a_fahrenheit(self):
        assert convertir(273.15, Unit.KELVIN, Unit.FAHRENHEIT) == 32.0

    def test_redondeo_a_dos_decimales(self):
        assert convertir(37, Unit.CELSIUS, Unit.FAHRENHEIT) == 98.6


# US2 — Rechazar temperaturas Kelvin inválidas (FR-005)
class TestValidacionKelvin:
    def test_rechaza_kelvin_negativo_como_origen(self):
        with pytest.raises(ValueError, match="Kelvin"):
            convertir(-10, Unit.KELVIN, Unit.CELSIUS)

    def test_rechaza_resultado_kelvin_negativo(self):
        with pytest.raises(ValueError, match="Kelvin"):
            convertir(-300, Unit.CELSIUS, Unit.KELVIN)


# US3 — Manejar entradas no numéricas (FR-006)
class TestEntradaNoNumerica:
    def test_valor_no_numerico_lanza_error_controlado(self):
        with pytest.raises(ValueError, match="no numérico"):
            parse_valor("abc")


# Polish — Casos borde adicionales (FR-007, FR-008)
class TestCasosBordeAdicionales:
    def test_misma_unidad_origen_y_destino(self):
        assert convertir(100, Unit.CELSIUS, Unit.CELSIUS) == 100.0

    def test_negativo_valido_en_celsius(self):
        assert convertir(-40, Unit.CELSIUS, Unit.FAHRENHEIT) == -40.0

    def test_negativo_valido_en_fahrenheit(self):
        assert convertir(-40, Unit.FAHRENHEIT, Unit.CELSIUS) == -40.0

    def test_unidad_no_reconocida(self):
        with pytest.raises(ValueError, match="Unidad no reconocida"):
            parse_unidad("X")
