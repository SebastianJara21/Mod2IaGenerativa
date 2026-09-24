# Implementation Plan: Conversor de Temperatura

**Branch**: `001-conversor-temperatura` | **Date**: 2026-09-23 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-conversor-temperatura/spec.md`

## Summary

Programa de línea de comandos que convierte una temperatura entre Celsius, Fahrenheit y Kelvin, redondeando el resultado a 2 decimales y rechazando temperaturas en Kelvin menores a 0. Se implementa como un paquete Python mínimo, gestionado con `uv`, sin dependencias externas.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Ninguna (solo biblioteca estándar)

**Storage**: N/A (no persiste datos)

**Testing**: pytest

**Target Platform**: CLI multiplataforma (Windows/Linux/macOS)

**Project Type**: single (herramienta de línea de comandos)

**Performance Goals**: N/A — cálculo aritmético simple, sin restricciones de rendimiento relevantes

**Constraints**: N/A

**Scale/Scope**: Herramienta de un solo comando por invocación; sin concurrencia ni persistencia

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

El archivo `.specify/memory/constitution.md` está en su plantilla sin llenar (no se ejecutó `/speckit.constitution`, paso opcional no requerido por la guía del curso). No hay principios de proyecto definidos, por lo tanto no aplican gates para esta feature.

## Project Structure

### Documentation (this feature)

```text
specs/001-conversor-temperatura/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
└── conversor_temperatura/
    ├── __init__.py
    └── converter.py

tests/
└── test_converter.py
```

**Structure Decision**: Opción 1 (proyecto único). Es una herramienta CLI autocontenida sin frontend/backend separados ni componente móvil, igual que el proyecto equivalente del Bloque 3.A.

## Complexity Tracking

*No aplica: no hay violaciones de constitución que justificar (no hay constitución definida).*
