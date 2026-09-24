# Research: Conversor de Temperatura

## Resumen

La especificación no dejó ningún aspecto marcado como `[NEEDS CLARIFICATION]`, por lo que no se requirió investigación de incógnitas. Este documento registra las decisiones técnicas tomadas y su justificación.

## Decisiones

### Lenguaje y gestor de paquetes

- **Decision**: Python 3.12 con `uv` como gestor de dependencias y entorno.
- **Rationale**: Es el mismo entorno usado en el resto del repositorio (ver `pyproject.toml` raíz y `s4/clase-sdd/`), lo que mantiene consistencia y facilita comparar ambos bloques (3.A y 3.B).
- **Alternatives considered**: `pip` + `venv` — descartado por no ser el estándar ya adoptado en el proyecto.

### Framework de pruebas

- **Decision**: `pytest`.
- **Rationale**: Estándar de facto en el ecosistema Python, ya usado en `s4/clase-sdd/tests/`.
- **Alternatives considered**: `unittest` de la biblioteca estándar — descartado por ser más verboso sin aportar ventajas para este alcance.

### Fórmulas de conversión

- **Decision**: Usar Celsius como unidad intermedia para las seis conversiones posibles (C→F, F→C, C→K, K→C, F→K, K→F):
  - `F = C * 9/5 + 32`
  - `K = C + 273.15`
- **Rationale**: Fórmulas estándar de física; pasar todo por Celsius como paso intermedio evita duplicar fórmulas directas para cada par de unidades.
- **Alternatives considered**: Fórmulas directas para cada uno de los 6 pares — descartado por ser redundante sin beneficio de precisión o rendimiento.

### Validación de Kelvin

- **Decision**: Rechazar cualquier valor de entrada en Kelvin menor a 0, antes de convertir.
- **Rationale**: 0 K es el cero absoluto; un valor menor no es físicamente posible (requisito FR-005 de la spec).
- **Alternatives considered**: Ninguna — es una regla física fija, no una decisión de diseño.

**Output**: Sin incógnitas pendientes; lista para Fase 1 (diseño).
