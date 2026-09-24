# Comparación — Spec a Mano vs. Spec Kit

Mismo proyecto (conversor de temperatura) implementado con dos enfoques: [`clase-sdd/`](clase-sdd/) (Bloque 3.A, spec a mano) y [`mi-proyecto-speckit/`](mi-proyecto-speckit/) (Bloque 3.B, Spec Kit).

> Nota: por cuota de uso agotada en `agy` (~165h de bloqueo), el Bloque 3.B se ejecutó con Claude Code sobre las mismas plantillas de Spec Kit que se habrían usado con `agy`. Ver la nota al inicio de [`mi-proyecto-speckit/resultados-3b.md`](mi-proyecto-speckit/resultados-3b.md).

## Tabla Comparativa

| Aspecto | Spec a mano | Spec Kit |
|---|---|---|
| ¿Cubrió los mismos casos borde? | Sí, los 3 definidos en `spec_manual.md` (no numérico, misma unidad, negativos válidos) | Sí, los mismos 3, trasladados a `spec.md` como Edge Cases y a Requisitos Funcionales (FR-001 a FR-008) |
| ¿Qué generó Spec Kit que tú no habías escrito? | — | Historias de usuario priorizadas (P1/P2/P3), criterios de éxito medibles y tecnológicamente agnósticos (`SC-001` a `SC-003`), un checklist de calidad de la spec, y un `research.md` documentando las decisiones técnicas (lenguaje, fórmulas, framework de pruebas) antes de tocar código |
| ¿Qué se sintió más rápido de arrancar? | Spec a mano: un solo archivo de 3 secciones, listo para implementar en un pedido | Spec Kit: 4 comandos en secuencia (specify → plan → tasks → implement), cada uno genera varios archivos; más lento de arrancar pero deja más documentación intermedia |
| ¿Cuál te generó más confianza en el resultado? | Alta para el alcance definido, pero la implementación final incluyó comportamiento no pedido explícitamente (normalización de mayúsculas) por iniciativa del agente | Alta también, y más trazable: cada línea de código de `tasks.md` apunta a un requisito funcional específico (FR-00x), lo que facilita verificar que no se implementó nada fuera de la spec |

## Los 3 Casos, Lado a Lado

| Caso | Resultado Spec a Mano (3.A) | Resultado Spec Kit (3.B) |
|---|---|---|
| **Caso normal** (100°C → F) | `100.00 °C = 212.00 °F` ✅ | `100.00 C = 212.00 F` ✅ |
| **Caso borde de spec** (Kelvin = -10, o "abc") | Error claro en ambos casos ✅ | Error claro en ambos casos ✅ |
| **Caso no contemplado** (unidad en minúscula 'c') | Normalizada automáticamente: `100.00 °C = 212.00 °F` | Rechazada: `Error: Unidad no reconocida: 'c'. Use C, F o K.` |

El caso "no contemplado" es el más revelador: ambos agentes recibieron la misma spec original (sin mencionar mayúsculas/minúsculas), pero llegaron a comportamientos distintos. En 3.A, `agy` implementó la spec completa en un solo pedido y decidió, por su cuenta, tolerar minúsculas. En 3.B, el proceso de Spec Kit pasó primero por una fase de especificación formal (`spec.md` con FR-001 a FR-008) y luego por tareas derivadas estrictamente de esos requisitos (`tasks.md`); como ninguno mencionaba tolerancia de mayúsculas, la implementación final la rechazó. Ninguna de las dos es un error — la spec original no lo definía — pero muestra que Spec Kit tiende a ceñirse más literalmente a lo escrito, mientras que una implementación directa puede "rellenar" huecos con supuestos razonables sin dejar rastro de esa decisión.

## Cierre

> La próxima vez que tenga un proyecto de tamaño **pequeño**, elegiría **spec a mano** porque el ida y vuelta de 4 comandos de Spec Kit (con sus artefactos de plan, research, data-model y tasks) es más peso del que un proyecto de este tamaño necesita; para algo pequeño, una spec de 3 secciones y un solo pedido de implementación ya da suficiente claridad. Spec Kit se sentiría más justificado en un proyecto mediano o grande, donde la trazabilidad de cada línea de código a un requisito específico (FR-00x) y la documentación intermedia (research.md, data-model.md) sí pagan su costo de tiempo extra.
