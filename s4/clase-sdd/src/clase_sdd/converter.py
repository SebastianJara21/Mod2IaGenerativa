"""Módulo de conversión de temperatura entre Celsius, Fahrenheit y Kelvin.

Cumple con la especificación de conversor de temperatura:
- Conversión bidireccional entre Celsius, Fahrenheit y Kelvin.
- Redondeo a 2 decimales.
- Validación de temperatura mínima en Kelvin (>= 0 K).
- Manejo de entradas no numéricas sin excepciones no controladas.
- Soporte para misma unidad de origen y destino.
- Soporte para números negativos válidos.
- Tolerancia a mayúsculas/minúsculas y formatos como '100C'.
"""

from enum import Enum
import re
from typing import Any, Tuple


class Unit(str, Enum):
    """Unidades de temperatura soportadas."""
    CELSIUS = "C"
    FAHRENHEIT = "F"
    KELVIN = "K"

    @property
    def symbol(self) -> str:
        """Símbolo estándar para la unidad."""
        if self == Unit.CELSIUS:
            return "°C"
        elif self == Unit.FAHRENHEIT:
            return "°F"
        return "K"

    @property
    def label(self) -> str:
        """Nombre legible de la unidad."""
        if self == Unit.CELSIUS:
            return "Celsius"
        elif self == Unit.FAHRENHEIT:
            return "Fahrenheit"
        return "Kelvin"


# Mapeo de alias y variantes a la unidad correspondiente
_UNIT_ALIASES: dict[str, Unit] = {
    "c": Unit.CELSIUS,
    "celsius": Unit.CELSIUS,
    "°c": Unit.CELSIUS,
    "c°": Unit.CELSIUS,
    "f": Unit.FAHRENHEIT,
    "fahrenheit": Unit.FAHRENHEIT,
    "°f": Unit.FAHRENHEIT,
    "f°": Unit.FAHRENHEIT,
    "k": Unit.KELVIN,
    "kelvin": Unit.KELVIN,
    "°k": Unit.KELVIN,
    "k°": Unit.KELVIN,
}


def normalize_unit(unit: str | Unit) -> Unit:
    """Normaliza y valida la unidad de temperatura ingresada.
    
    Acepta strings como 'c', 'C', 'celsius', 'F', 'f', 'fahrenheit', 'k', 'K', 'kelvin'.
    Lanza ValueError con un mensaje claro si la unidad no es reconocida.
    """
    if isinstance(unit, Unit):
        return unit
    if not isinstance(unit, str):
        raise ValueError(
            f"Error: La unidad debe ser un texto, pero se recibió {type(unit).__name__}: {unit!r}"
        )
    
    cleaned = unit.strip().lower()
    if cleaned in _UNIT_ALIASES:
        return _UNIT_ALIASES[cleaned]
    
    raise ValueError(
        f"Error: Unidad no reconocida '{unit}'. Las unidades válidas son Celsius (C), Fahrenheit (F) o Kelvin (K)."
    )


def parse_temperature_value(value: Any) -> float:
    """Parsea y valida que el valor sea numérico.
    
    Lanza ValueError con un mensaje claro si el valor no es numérico,
    evitando excepciones no controladas.
    """
    if isinstance(value, bool):
        raise ValueError(
            f"Error: Valor no numérico como entrada ({value!r}). Ingrese un número válido."
        )
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        cleaned = value.strip()
        try:
            return float(cleaned)
        except ValueError:
            raise ValueError(
                f"Error: Valor no numérico como entrada ('{value}'). Ingrese un número válido."
            )
            
    raise ValueError(
        f"Error: Tipo de entrada no soportado ({type(value).__name__}: {value!r}). Ingrese un número válido."
    )


def parse_value_and_unit(input_str: str) -> Tuple[float, Unit | None]:
    """Intenta parsear cadenas combinadas como '100C', '100 °C', '-40F', '300K', etc.
    
    Retorna (valor_float, Unit | None). Si no contiene unidad, la unidad retornada es None.
    """
    cleaned = input_str.strip()
    match = re.match(r"^([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*(°?[a-zA-Z]+)?$", cleaned)
    if match:
        val_str, unit_str = match.groups()
        val = float(val_str)
        unit = normalize_unit(unit_str) if unit_str else None
        return val, unit
    
    # Si no coincide con el regex combinado, delegamos a parse_temperature_value
    val = parse_temperature_value(cleaned)
    return val, None


def convert_temperature(
    value: float | int | str,
    from_unit: str | Unit,
    to_unit: str | Unit,
) -> float:
    """Convierte una temperatura entre Celsius, Fahrenheit y Kelvin.

    Criterios:
    - Convierte correctamente entre Celsius, Fahrenheit y Kelvin.
    - Redondea el resultado a 2 decimales.
    - Rechaza una temperatura en Kelvin menor a 0 con mensaje de error claro.
    - Maneja casos borde: no numéricos, misma unidad, números negativos válidos.
    """
    num_val = parse_temperature_value(value)
    unit_from = normalize_unit(from_unit)
    unit_to = normalize_unit(to_unit)

    # Criterio: Rechaza una temperatura en Kelvin menor a 0
    if unit_from == Unit.KELVIN and num_val < 0:
        raise ValueError(
            f"Error: La temperatura en Kelvin no puede ser menor a 0 K (recibido: {num_val} K)."
        )

    # Caso borde: Misma unidad de entrada y salida
    if unit_from == unit_to:
        return round(num_val, 2)

    # 1. Convertir a Celsius como escala intermedia
    if unit_from == Unit.CELSIUS:
        celsius = num_val
    elif unit_from == Unit.FAHRENHEIT:
        celsius = (num_val - 32.0) * (5.0 / 9.0)
    elif unit_from == Unit.KELVIN:
        celsius = num_val - 273.15
    else:
        raise ValueError(f"Error: Unidad de origen no soportada: {unit_from}")

    # 2. Convertir desde Celsius a la unidad destino
    if unit_to == Unit.CELSIUS:
        result = celsius
    elif unit_to == Unit.FAHRENHEIT:
        result = (celsius * (9.0 / 5.0)) + 32.0
    elif unit_to == Unit.KELVIN:
        kelvin = celsius + 273.15
        if kelvin < 0:
            raise ValueError(
                f"Error: La temperatura resultante en Kelvin ({round(kelvin, 2)} K) no puede ser menor a 0 K."
            )
        result = kelvin
    else:
        raise ValueError(f"Error: Unidad de destino no soportada: {unit_to}")

    return round(result, 2)


def format_temperature(value: float, unit: Unit) -> str:
    """Formatea la temperatura con 2 decimales y su símbolo oficial."""
    return f"{value:.2f} {unit.symbol}"
