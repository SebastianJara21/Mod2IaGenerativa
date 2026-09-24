"""Punto de entrada de la CLI del conversor de temperatura (Spec Kit)."""

import sys
from typing import Sequence

from conversor_temperatura.converter import convertir, parse_unidad, parse_valor


def main(argv: Sequence[str] | None = None) -> int:
    """CLI: conversor-speckit <valor> <unidad_origen> <unidad_destino>."""
    if argv is None:
        argv = sys.argv[1:]

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    if len(argv) != 3:
        print(
            "Uso: conversor-speckit <valor> <unidad_origen> <unidad_destino> "
            "(ej. conversor-speckit 100 C F)",
            file=sys.stderr,
        )
        return 1

    valor_texto, origen_texto, destino_texto = argv

    try:
        valor = parse_valor(valor_texto)
        origen = parse_unidad(origen_texto)
        destino = parse_unidad(destino_texto)
        resultado = convertir(valor, origen, destino)
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    print(f"{valor:.2f} {origen.value} = {resultado:.2f} {destino.value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
