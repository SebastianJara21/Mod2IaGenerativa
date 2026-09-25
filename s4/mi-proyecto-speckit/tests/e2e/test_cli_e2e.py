"""Tests end-to-end: invocación del programa como proceso completo.

Prueba el programa como lo usaría un usuario real, invocando via subprocess
y verificando stdout, stderr y código de salida.
"""

import subprocess
import sys


def run_converter(valor: str, origen: str, destino: str) -> tuple[int, str, str]:
    """Ejecuta el programa como subprocess y devuelve (exit_code, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, "-m", "conversor_temperatura", valor, origen, destino],
        capture_output=True,
        text=True,
        cwd=".",
    )
    return result.returncode, result.stdout, result.stderr


class TestCLIE2E:
    """Tests end-to-end del conversor via subprocess."""

    def test_e2e_celsius_to_fahrenheit(self):
        """US1: Usuario convierte 100°C a Fahrenheit → obtiene 212.00°F."""
        exit_code, stdout, stderr = run_converter("100", "C", "F")
        assert exit_code == 0, f"Expected exit 0, got {exit_code}. stderr: {stderr}"
        assert "212.00 F" in stdout
        assert "100.00 C" in stdout

    def test_e2e_fahrenheit_to_celsius(self):
        """US1: Usuario convierte 32°F a Celsius → obtiene 0.00°C."""
        exit_code, stdout, stderr = run_converter("32", "F", "C")
        assert exit_code == 0, f"Expected exit 0, got {exit_code}. stderr: {stderr}"
        assert "0.00 C" in stdout

    def test_e2e_celsius_to_kelvin(self):
        """US1: Usuario convierte 0°C a Kelvin → obtiene 273.15 K."""
        exit_code, stdout, stderr = run_converter("0", "C", "K")
        assert exit_code == 0, f"Expected exit 0, got {exit_code}. stderr: {stderr}"
        assert "273.15 K" in stdout

    def test_e2e_kelvin_to_fahrenheit(self):
        """US1: Usuario convierte 273.15 K a Fahrenheit → obtiene 32.00°F."""
        exit_code, stdout, stderr = run_converter("273.15", "K", "F")
        assert exit_code == 0, f"Expected exit 0, got {exit_code}. stderr: {stderr}"
        assert "32.00 F" in stdout

    def test_e2e_same_unit_origin_destination(self):
        """US1 edge case: Usuario convierte 100°C a Celsius → obtiene 100.00°C."""
        exit_code, stdout, stderr = run_converter("100", "C", "C")
        assert exit_code == 0, f"Expected exit 0, got {exit_code}. stderr: {stderr}"
        assert "100.00 C = 100.00 C" in stdout

    def test_e2e_negative_kelvin_as_origin_rejected(self):
        """US2: Usuario ingresa -10 K → programa rechaza con error claro."""
        exit_code, stdout, stderr = run_converter("-10", "K", "C")
        assert exit_code == 1, f"Expected exit 1, got {exit_code}"
        assert "Error:" in stderr
        assert "Kelvin" in stderr

    def test_e2e_conversion_resulting_negative_kelvin_rejected(self):
        """US2: Usuario convierte -300°C a K → programa rechaza (resultado sería K negativo)."""
        exit_code, stdout, stderr = run_converter("-300", "C", "K")
        assert exit_code == 1, f"Expected exit 1, got {exit_code}"
        assert "Error:" in stderr
        assert "Kelvin" in stderr

    def test_e2e_non_numeric_value_rejected(self):
        """US3: Usuario ingresa 'abc' como valor → programa rechaza con error claro."""
        exit_code, stdout, stderr = run_converter("abc", "C", "F")
        assert exit_code == 1, f"Expected exit 1, got {exit_code}"
        assert "Error:" in stderr
        # Verify error is about invalid value, not an unhandled exception
        assert "Traceback" not in stderr
        assert "abc" in stderr

    def test_e2e_invalid_unit_rejected(self):
        """US3: Usuario ingresa unidad inválida 'X' → programa rechaza."""
        exit_code, stdout, stderr = run_converter("100", "X", "F")
        assert exit_code == 1, f"Expected exit 1, got {exit_code}"
        assert "Error:" in stderr
        assert "Unidad no reconocida" in stderr

    def test_e2e_wrong_argument_count_rejected(self):
        """CLI rejects invocation with incorrect number of arguments."""
        result = subprocess.run(
            [sys.executable, "-m", "conversor_temperatura", "100", "C"],
            capture_output=True,
            text=True,
            cwd=".",
        )
        assert result.returncode == 1
        assert "Uso:" in result.stderr

    def test_e2e_negative_valid_in_celsius(self):
        """US1 edge case: User converts -40°C to Fahrenheit → gets -40.00°F."""
        exit_code, stdout, stderr = run_converter("-40", "C", "F")
        assert exit_code == 0, f"Expected exit 0, got {exit_code}. stderr: {stderr}"
        assert "-40.00 F" in stdout
