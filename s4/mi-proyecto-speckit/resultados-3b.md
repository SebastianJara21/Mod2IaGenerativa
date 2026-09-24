# Resultados de Pruebas — Bloque 3.B (Spec Kit)

> Nota sobre el agente usado: `agy` (el agente CLI del curso) alcanzó su cuota de uso individual durante este bloque (bloqueado ~165h). Los 4 comandos de Spec Kit (`/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement`) se ejecutaron con **Claude Code** en su lugar, usando exactamente las mismas plantillas que `specify init` generó para la integración `generic` (`.agy/commands/`). El flujo y los artefactos de Spec Kit son idénticos a los que habría producido cualquier otro agente compatible.

## Casos de Prueba

| Tipo de caso | Entrada y transformación | Resultado esperado | Resultado obtenido | ¿Cumplió la spec? |
|---|---|---|---|---|
| **Caso normal** | 100 °C a Fahrenheit (`conversor-speckit 100 C F`) | 212.00 °F | `100.00 C = 212.00 F` | Sí ✅ |
| **Caso borde de spec** | Kelvin = -10 (`conversor-speckit -10 K C`) o entrada "abc" (`conversor-speckit abc C F`) | Mensaje de error claro sin excepción no controlada | `Error: La temperatura en Kelvin no puede ser menor a 0 K...` / `Error: Valor no numérico como entrada ('abc')...` | Sí ✅ |
| **Caso no contemplado** | Entrada en minúsculas 'c' a 'f' (`conversor-speckit 100 c f`) | Comportamiento del agente sin instrucción previa | `Error: Unidad no reconocida: 'c'. Use C, F o K.` | Ver comparación ⚠️ |

---

## Salida de Ejecución de Terminal

```text
$ uv run conversor-speckit 100 C F
100.00 C = 212.00 F

$ uv run conversor-speckit -10 K C
Error: La temperatura en Kelvin no puede ser menor a 0 K (recibido: -10.0 K).

$ uv run conversor-speckit abc C F
Error: Valor no numérico como entrada ('abc'). Ingrese un número válido.

$ uv run conversor-speckit 100 c f
Error: Unidad no reconocida: 'c'. Use C, F o K.

$ uv run conversor-speckit 100 C C
100.00 C = 100.00 C

$ uv run conversor-speckit -40 C F
-40.00 C = -40.00 F
```

## Nota sobre el caso "no contemplado"

A diferencia del Bloque 3.A —donde `agy`, implementando directamente a partir de la spec en un solo pedido, agregó por iniciativa propia normalización de mayúsculas/minúsculas y parseo de formatos combinados ("100C")—, la implementación generada siguiendo `tasks.md` de Spec Kit **rechaza** la unidad en minúscula, porque ninguno de los requisitos funcionales (FR-001 a FR-008) de `specs/001-conversor-temperatura/spec.md` pide tolerancia de mayúsculas. Esta diferencia es justamente el hallazgo más interesante del caso no contemplado: el proceso estructurado de Spec Kit (spec → plan → tasks → implement) produjo una implementación más apegada literalmente a los requisitos escritos, mientras que la implementación directa de agy en 3.A "rellenó" el hueco con una decisión propia razonable. Ninguna de las dos es incorrecta — la spec no lo definía — pero el comportamiento resultante es distinto.
