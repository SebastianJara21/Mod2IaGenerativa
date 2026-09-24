"""Punto de entrada principal para el conversor de temperatura."""

import sys
from typing import Sequence

from clase_sdd.converter import (
    Unit,
    convert_temperature,
    format_temperature,
    normalize_unit,
    parse_temperature_value,
    parse_value_and_unit,
)


def run_conversion(
    val_str: str,
    from_unit_str: str | None,
    to_unit_str: str,
) -> int:
    """Ejecuta la conversión controlando excepciones y emitiendo mensajes claros."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    try:
        # Detectar si el valor incluye unidad (ej. "100C" o "100")
        parsed_val, detected_unit = parse_value_and_unit(val_str)
        
        # Determinar unidad de origen
        if from_unit_str is not None:
            source_unit = normalize_unit(from_unit_str)
        elif detected_unit is not None:
            source_unit = detected_unit
        else:
            print("Error: No se especificó la unidad de origen (C, F o K).", file=sys.stderr)
            return 1
            
        target_unit = normalize_unit(to_unit_str)

        # Realizar conversión
        converted = convert_temperature(parsed_val, source_unit, target_unit)

        # Formatear salida con 2 decimales
        orig_formatted = format_temperature(parsed_val, source_unit)
        dest_formatted = format_temperature(converted, target_unit)
        print(f"{orig_formatted} = {dest_formatted}")
        return 0

    except ValueError as err:
        # Emite mensaje de error claro sin excepciones no controladas
        print(str(err), file=sys.stderr)
        return 1
    except Exception as err:
        print(f"Error inesperado: {err}", file=sys.stderr)
        return 1


def main(argv: Sequence[str] | None = None) -> int:
    """CLI para el conversor de temperatura.
    
    Uso:
        clase-sdd <valor> <origen> <destino>   (ej: clase-sdd 100 C F)
        clase-sdd <valor_con_unidad> <destino> (ej: clase-sdd 100C F)
        clase-sdd                             (modo interactivo)
    """
    if argv is None:
        argv = sys.argv[1:]

    # Ayuda
    if argv and argv[0] in ("-h", "--help", "help"):
        print("Uso del Conversor de Temperatura:")
        print("  clase-sdd <valor> <origen> <destino>   (ej. clase-sdd 100 C F)")
        print("  clase-sdd <valor_con_unidad> <destino> (ej. clase-sdd 100C F)")
        print("  clase-sdd                             (inicia modo interactivo)")
        print("\nUnidades soportadas: Celsius (C), Fahrenheit (F), Kelvin (K)")
        return 0

    # 3 argumentos: clase-sdd <valor> <origen> <destino>
    if len(argv) == 3:
        return run_conversion(argv[0], argv[1], argv[2])

    # 2 argumentos: clase-sdd <valor_con_unidad> <destino>
    if len(argv) == 2:
        return run_conversion(argv[0], None, argv[1])

    # Modo interactivo cuando no se pasan argumentos
    if len(argv) == 0:
        print("=== Conversor de Temperatura ===")
        try:
            val_input = input("Ingrese la temperatura (ej. 100 o 100C): ").strip()
            if not val_input:
                print("Error: Entrada vacía. Debe ingresar un valor numérico.", file=sys.stderr)
                return 1

            # Revisar si ya incluyó unidad
            _, detected = parse_value_and_unit(val_input)
            if detected is None:
                from_u = input("Unidad de origen (C / F / K): ").strip()
            else:
                from_u = detected.value

            to_u = input("Unidad de destino (C / F / K): ").strip()
            return run_conversion(val_input, from_u, to_u)
        except (KeyboardInterrupt, EOFError):
            print("\nOperación cancelada por el usuario.")
            return 0

    print("Error: Parámetros inválidos. Use --help para ver la sintaxis.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
