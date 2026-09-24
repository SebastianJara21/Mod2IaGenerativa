"""Conversión de temperatura entre Celsius, Fahrenheit y Kelvin.

Implementa los requisitos funcionales FR-001 a FR-008 de
specs/001-conversor-temperatura/spec.md.
"""

from enum import Enum


class Unit(str, Enum):
    """Unidades de temperatura soportadas."""

    CELSIUS = "C"
    FAHRENHEIT = "F"
    KELVIN = "K"


def parse_unidad(texto: str) -> Unit:
    """Valida y convierte un texto a una unidad soportada (C, F o K)."""
    try:
        return Unit(texto)
    except ValueError:
        raise ValueError(f"Unidad no reconocida: '{texto}'. Use C, F o K.") from None


def parse_valor(texto: str) -> float:
    """Valida y convierte un texto a un valor numérico de temperatura (FR-006)."""
    try:
        return float(texto)
    except ValueError:
        raise ValueError(
            f"Valor no numérico como entrada ('{texto}'). Ingrese un número válido."
        ) from None


def _a_celsius(valor: float, unidad: Unit) -> float:
    if unidad == Unit.CELSIUS:
        return valor
    if unidad == Unit.FAHRENHEIT:
        return (valor - 32) * 5 / 9
    return valor - 273.15


def _desde_celsius(valor_c: float, unidad: Unit) -> float:
    if unidad == Unit.CELSIUS:
        return valor_c
    if unidad == Unit.FAHRENHEIT:
        return valor_c * 9 / 5 + 32
    return valor_c + 273.15


def convertir(valor: float, unidad_origen: Unit, unidad_destino: Unit) -> float:
    """Convierte una temperatura entre Celsius, Fahrenheit y Kelvin.

    - Redondea el resultado a 2 decimales (FR-004).
    - Rechaza una temperatura en Kelvin menor a 0, sea como valor de
      origen o como resultado de la conversión (FR-005).
    - Devuelve el mismo valor si origen y destino coinciden (FR-007).
    """
    if unidad_origen == Unit.KELVIN and valor < 0:
        raise ValueError(
            f"La temperatura en Kelvin no puede ser menor a 0 K (recibido: {valor} K)."
        )

    if unidad_origen == unidad_destino:
        return round(valor, 2)

    resultado = _desde_celsius(_a_celsius(valor, unidad_origen), unidad_destino)

    if unidad_destino == Unit.KELVIN and resultado < 0:
        raise ValueError(
            f"La conversión da como resultado una temperatura Kelvin menor a 0 K "
            f"({round(resultado, 2)} K)."
        )

    return round(resultado, 2)
