"""Tests de integración: CLI conectando con módulos de conversión.

Prueba que la función main() integra correctamente el parsing de valores,
parsing de unidades, validación Kelvin y conversión (US1, US2, US3).
"""

import pytest
from io import StringIO
from unittest.mock import patch

from conversor_temperatura import main


class TestMainIntegration:
    """Tests en memoria (sin subprocess) del flujo CLI integrado."""

    def test_main_conversion_celsius_to_fahrenheit(self, capsys):
        """US1: CLI conversa temperatura válida Celsius a Fahrenheit."""
        exit_code = main(["100", "C", "F"])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "212.00 F" in captured.out

    def test_main_conversion_kelvin_to_celsius(self, capsys):
        """US1: CLI convierte temperatura válida Kelvin a Celsius."""
        exit_code = main(["273.15", "K", "C"])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "0.00 C" in captured.out

    def test_main_same_unit_origin_destination(self, capsys):
        """US1 edge case: CLI devuelve mismo valor si origen y destino son iguales."""
        exit_code = main(["50", "C", "C"])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "50.00 C = 50.00 C" in captured.out

    def test_main_rejects_negative_kelvin_as_origin(self, capsys):
        """US2: CLI rechaza temperatura Kelvin negativa de origen."""
        exit_code = main(["-10", "K", "C"])
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err
        assert "Kelvin" in captured.err

    def test_main_rejects_conversion_resulting_negative_kelvin(self, capsys):
        """US2: CLI rechaza conversión que resulte en Kelvin negativo."""
        exit_code = main(["-300", "C", "K"])
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err
        assert "Kelvin" in captured.err

    def test_main_rejects_non_numeric_value(self, capsys):
        """US3: CLI rechaza entrada no numérica con error claro."""
        exit_code = main(["abc", "C", "F"])
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err
        assert "no numérico" in captured.err

    def test_main_rejects_invalid_unit(self, capsys):
        """CLI rechaza unidad no reconocida."""
        exit_code = main(["100", "X", "F"])
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err
        assert "Unidad no reconocida" in captured.err

    def test_main_rejects_wrong_argument_count(self, capsys):
        """CLI rechaza invocación con número incorrecto de argumentos."""
        exit_code = main(["100", "C"])
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Uso:" in captured.err
