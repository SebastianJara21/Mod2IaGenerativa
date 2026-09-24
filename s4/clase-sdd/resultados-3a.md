# Resultados de Pruebas — Bloque 3.A (Spec a Mano)

## Casos de Prueba

| Tipo de caso | Entrada y transformación | Resultado esperado | Resultado obtenido | ¿Cumplió la spec? |
|---|---|---|---|---|
| **Caso normal** | 100 °C a Fahrenheit (`clase-sdd 100 C F`) | 212.00 °F | `100.00 °C = 212.00 °F` | Sí ✅ |
| **Caso borde de spec** | Entrada "abc" (`clase-sdd abc C F`) o Kelvin = -10 K (`clase-sdd -10 K C`) | Mensaje de error claro sin excepción no controlada | `Error: Valor no numérico como entrada ('abc')...` / `Error: La temperatura en Kelvin no puede ser menor a 0 K...` | Sí ✅ |
| **Caso no contemplado** | Entrada en minúsculas 'c' a 'f' (`clase-sdd 100 c f`) o formato '100C' (`clase-sdd 100C F`) | Comportamiento del agente sin instrucción previa | `100.00 °C = 212.00 °F` (Normalización automática de minúsculas y parseo de formato compuesto) | Sí ✅ |

---

## Salida de Ejecución de Terminal
```text
$ uv run clase-sdd 100 C F
100.00 °C = 212.00 °F

$ uv run clase-sdd abc C F
Error: Valor no numérico como entrada ('abc'). Ingrese un número válido.

$ uv run clase-sdd -10 K C
Error: La temperatura en Kelvin no puede ser menor a 0 K (recibido: -10.0 K).

$ uv run clase-sdd 100 c f
100.00 °C = 212.00 °F

$ uv run clase-sdd 100C F
100.00 °C = 212.00 °F

$ uv run clase-sdd -40 C F
-40.00 °C = -40.00 °F

$ uv run clase-sdd 100 C C
100.00 °C = 100.00 °C
```
