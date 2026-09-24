# Quickstart: Conversor de Temperatura

Guía de validación manual para comprobar que la feature funciona de extremo a extremo, en paralelo con `s4/clase-sdd/resultados-3a.md` (mismo conjunto de casos, para poder comparar).

## Prerrequisitos

- Python 3.12 y `uv` instalados.
- Dependencias instaladas: `uv sync` en la raíz de `s4/mi-proyecto-speckit/`.

## Casos de validación

| Caso | Comando (ejemplo) | Resultado esperado |
|---|---|---|
| Caso normal | convertir 100 de Celsius a Fahrenheit | `212.00` |
| Caso borde de la spec | convertir Kelvin = -10 a cualquier unidad | Mensaje de error claro, sin excepción no controlada |
| Caso borde de la spec | convertir "abc" (no numérico) | Mensaje de error claro, sin excepción no controlada |
| Caso no contemplado | convertir con unidad de origen y destino iguales (ej. C a C) | Devuelve el mismo valor |

Los comandos exactos de invocación se definen durante `/speckit.implement`, según cómo `tasks.md` estructure la CLI. Ver `tests/test_converter.py` para los casos automatizados equivalentes.
