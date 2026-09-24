"""Suite de pruebas unitarias para el conversor de temperatura.

Verifica todos los criterios de aceptación y casos borde de la especificación:
1. Celsius a Fahrenheit y viceversa
2. Celsius a Kelvin y viceversa
3. Redondeo a 2 decimales
4. Rechazo de Kelvin < 0 con mensaje de error claro
5. Casos borde: valores no numéricos, misma unidad, negativos válidos.
6. Casos no contemplados: minúsculas ('c', 'f', 'k') y formato '100C'.
"""

import unittest
from clase_sdd.converter import (
    Unit,
    convert_temperature,
    normalize_unit,
    parse_temperature_value,
    parse_value_and_unit,
)
from clase_sdd import run_conversion, main
from io import StringIO
import sys


class TestTemperatureConverter(unittest.TestCase):
    """Pruebas de la lógica de conversión de temperatura."""

    # 1. Celsius <-> Fahrenheit
    def test_celsius_to_fahrenheit_boiling(self):
        """100 °C = 212.00 °F"""
        self.assertEqual(convert_temperature(100, Unit.CELSIUS, Unit.FAHRENHEIT), 212.0)

    def test_celsius_to_fahrenheit_freezing(self):
        """0 °C = 32.00 °F"""
        self.assertEqual(convert_temperature(0, Unit.CELSIUS, Unit.FAHRENHEIT), 32.0)

    def test_fahrenheit_to_celsius_boiling(self):
        """212 °F = 100.00 °C"""
        self.assertEqual(convert_temperature(212, Unit.FAHRENHEIT, Unit.CELSIUS), 100.0)

    def test_fahrenheit_to_celsius_freezing(self):
        """32 °F = 0.00 °C"""
        self.assertEqual(convert_temperature(32, Unit.FAHRENHEIT, Unit.CELSIUS), 0.0)

    # 2. Celsius <-> Kelvin
    def test_celsius_to_kelvin_zero(self):
        """0 °C = 273.15 K"""
        self.assertEqual(convert_temperature(0, Unit.CELSIUS, Unit.KELVIN), 273.15)

    def test_celsius_to_kelvin_boiling(self):
        """100 °C = 373.15 K"""
        self.assertEqual(convert_temperature(100, Unit.CELSIUS, Unit.KELVIN), 373.15)

    def test_kelvin_to_celsius_absolute_zero(self):
        """0 K = -273.15 °C"""
        self.assertEqual(convert_temperature(0, Unit.KELVIN, Unit.CELSIUS), -273.15)

    def test_kelvin_to_celsius_water_freezing(self):
        """273.15 K = 0.00 °C"""
        self.assertEqual(convert_temperature(273.15, Unit.KELVIN, Unit.CELSIUS), 0.0)

    # Conversión adicional Fahrenheit <-> Kelvin
    def test_fahrenheit_to_kelvin(self):
        """32 °F = 273.15 K"""
        self.assertEqual(convert_temperature(32, Unit.FAHRENHEIT, Unit.KELVIN), 273.15)

    def test_kelvin_to_fahrenheit(self):
        """273.15 K = 32.00 °F"""
        self.assertEqual(convert_temperature(273.15, Unit.KELVIN, Unit.FAHRENHEIT), 32.0)

    # 3. Redondeo a 2 decimales
    def test_rounding_two_decimals(self):
        """Conversión con decimales infinitos o mayores a 2 se redondea a 2."""
        # 1 °C = 33.8 °F
        self.assertEqual(convert_temperature(1, "C", "F"), 33.8)
        # 37 °C a F = 98.6
        self.assertEqual(convert_temperature(37, "C", "F"), 98.6)
        # 33 °F a C = 0.5555... -> 0.56
        self.assertEqual(convert_temperature(33, "F", "C"), 0.56)

    # 4. Rechazar Kelvin < 0 con mensaje claro
    def test_reject_kelvin_below_zero(self):
        """Debe lanzar ValueError con mensaje claro si Kelvin < 0."""
        with self.assertRaises(ValueError) as ctx:
            convert_temperature(-10, Unit.KELVIN, Unit.CELSIUS)
        self.assertIn("La temperatura en Kelvin no puede ser menor a 0 K", str(ctx.exception))

    def test_reject_kelvin_result_below_zero(self):
        """Debe lanzar ValueError si la temperatura resultante en Kelvin es menor a 0 K."""
        with self.assertRaises(ValueError) as ctx:
            convert_temperature(-300, Unit.CELSIUS, Unit.KELVIN)
        self.assertIn("no puede ser menor a 0 K", str(ctx.exception))

    # 5. Casos borde
    def test_non_numeric_input_string(self):
        """Valor 'abc' debe lanzar un ValueError claro sin excepción no controlada."""
        with self.assertRaises(ValueError) as ctx:
            convert_temperature("abc", "C", "F")
        self.assertIn("Valor no numérico como entrada", str(ctx.exception))

    def test_non_numeric_input_boolean(self):
        """Boolean no debe ser aceptado como número."""
        with self.assertRaises(ValueError):
            convert_temperature(True, "C", "F")

    def test_same_unit_conversion(self):
        """Misma unidad debe retornar el mismo número redondeado."""
        self.assertEqual(convert_temperature(100, "C", "C"), 100.0)
        self.assertEqual(convert_temperature(75.5, "F", "F"), 75.5)
        self.assertEqual(convert_temperature(300, "K", "K"), 300.0)

    def test_valid_negative_temperatures(self):
        """-40 °C debe ser exactamente -40.00 °F y viceversa."""
        self.assertEqual(convert_temperature(-40, "C", "F"), -40.0)
        self.assertEqual(convert_temperature(-40, "F", "C"), -40.0)
        self.assertEqual(convert_temperature(-10, "C", "F"), 14.0)

    # 6. Casos no contemplados (flexibilidad de interfaz)
    def test_lowercase_units(self):
        """Debe aceptar unidades en minúsculas ('c', 'f', 'k')."""
        self.assertEqual(convert_temperature(100, "c", "f"), 212.0)
        self.assertEqual(convert_temperature(0, "c", "k"), 273.15)
        self.assertEqual(convert_temperature(212, "f", "c"), 100.0)

    def test_full_unit_names(self):
        """Debe aceptar nombres completos como 'celsius', 'fahrenheit', 'kelvin'."""
        self.assertEqual(convert_temperature(100, "celsius", "fahrenheit"), 212.0)

    def test_combined_string_input(self):
        """Debe parsear formatos como '100C' o '100 °C'."""
        val, unit = parse_value_and_unit("100C")
        self.assertEqual(val, 100.0)
        self.assertEqual(unit, Unit.CELSIUS)

        val_neg, unit_f = parse_value_and_unit("-40F")
        self.assertEqual(val_neg, -40.0)
        self.assertEqual(unit_f, Unit.FAHRENHEIT)


class TestCLI(unittest.TestCase):
    """Pruebas para la interfaz de línea de comandos."""

    def test_cli_success_case(self):
        """Caso normal: 100 C F -> retorna 0 y formatea 212.00 °F."""
        saved_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            exit_code = main(["100", "C", "F"])
            output = sys.stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("100.00 °C = 212.00 °F", output)
        finally:
            sys.stdout = saved_stdout

    def test_cli_non_numeric_error(self):
        """Caso borde: entrada 'abc' -> código de error 1 sin excepción sin capturar."""
        saved_stderr = sys.stderr
        sys.stderr = StringIO()
        try:
            exit_code = main(["abc", "C", "F"])
            err_output = sys.stderr.getvalue()
            self.assertEqual(exit_code, 1)
            self.assertIn("Valor no numérico como entrada", err_output)
        finally:
            sys.stderr = saved_stderr

    def test_cli_kelvin_negative_error(self):
        """Caso borde: Kelvin = -10 K -> código de error 1 con mensaje claro."""
        saved_stderr = sys.stderr
        sys.stderr = StringIO()
        try:
            exit_code = main(["-10", "K", "C"])
            err_output = sys.stderr.getvalue()
            self.assertEqual(exit_code, 1)
            self.assertIn("La temperatura en Kelvin no puede ser menor a 0 K", err_output)
        finally:
            sys.stderr = saved_stderr

    def test_cli_lowercase_and_combined_args(self):
        """Caso no contemplado: '100c' y 'f' o '100' 'c' 'f'."""
        saved_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            exit_code = main(["100c", "f"])
            output = sys.stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("100.00 °C = 212.00 °F", output)
        finally:
            sys.stdout = saved_stdout


if __name__ == "__main__":
    unittest.main()
