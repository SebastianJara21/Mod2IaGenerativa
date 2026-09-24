# Tasks: Conversor de Temperatura

**Input**: Design documents from `/specs/001-conversor-temperatura/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Incluidas — los requisitos funcionales (FR-001 a FR-008) son verificables y el Bloque 3.A ya usó pruebas automatizadas para el mismo dominio, así que se mantiene la comparación consistente.

**Organization**: Tareas agrupadas por historia de usuario (US1, US2, US3), en el mismo orden de prioridad que `spec.md`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Story]**: Historia de usuario a la que pertenece (US1, US2, US3)

## Path Conventions

Proyecto único (ver `plan.md`): `src/conversor_temperatura/`, `tests/` en la raíz de `s4/mi-proyecto-speckit/`.

---

## Phase 1: Setup

**Purpose**: Inicialización del proyecto

- [X] T001 Crear estructura `src/conversor_temperatura/` y `tests/` en `s4/mi-proyecto-speckit/`
- [X] T002 Inicializar proyecto Python 3.12 con `uv` (`pyproject.toml`) en `s4/mi-proyecto-speckit/pyproject.toml`, con `pytest` como dependencia de desarrollo

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestructura mínima que todas las historias necesitan

**⚠️ CRITICAL**: Ninguna historia de usuario puede empezar hasta terminar esta fase

- [X] T003 Definir la enumeración de unidades (Celsius, Fahrenheit, Kelvin) en `src/conversor_temperatura/converter.py`, según `data-model.md`
- [X] T004 [P] Crear el punto de entrada de la CLI que recibe valor, unidad de origen y unidad de destino en `src/conversor_temperatura/__init__.py`

**Checkpoint**: Fundación lista — se puede empezar con las historias de usuario

---

## Phase 3: User Story 1 - Convertir temperatura entre unidades (Priority: P1) 🎯 MVP

**Goal**: Convertir correctamente un valor entre Celsius, Fahrenheit y Kelvin, redondeado a 2 decimales (FR-001 a FR-004)

**Independent Test**: Convertir 100 de Celsius a Fahrenheit y verificar que el resultado es 212.00

### Tests for User Story 1

- [X] T005 [P] [US1] Test de las 6 conversiones (C↔F, C↔K, F↔K) y del redondeo a 2 decimales en `tests/test_converter.py`

### Implementation for User Story 1

- [X] T006 [US1] Implementar `convertir(valor, unidad_origen, unidad_destino)` con las fórmulas de `research.md` en `src/conversor_temperatura/converter.py` (depende de T003)
- [X] T007 [US1] Redondear el resultado de `convertir` a 2 decimales (FR-004) en `src/conversor_temperatura/converter.py` (depende de T006)
- [X] T008 [US1] Conectar `convertir` con el punto de entrada de la CLI en `src/conversor_temperatura/__init__.py` (depende de T004, T007)

**Checkpoint**: User Story 1 funcional y probable de forma independiente

---

## Phase 4: User Story 2 - Rechazar temperaturas Kelvin inválidas (Priority: P2)

**Goal**: Rechazar con un mensaje de error claro cualquier temperatura en Kelvin menor a 0 (FR-005)

**Independent Test**: Convertir -10 Kelvin y verificar que se devuelve un error, no un número

### Tests for User Story 2

- [X] T009 [P] [US2] Test de rechazo de Kelvin < 0 con mensaje de error claro en `tests/test_converter.py`

### Implementation for User Story 2

- [X] T010 [US2] Agregar validación de Kelvin ≥ 0 antes de convertir, con mensaje de error claro (FR-005) en `src/conversor_temperatura/converter.py` (depende de T006)

**Checkpoint**: User Stories 1 y 2 funcionan de forma independiente

---

## Phase 5: User Story 3 - Manejar entradas no numéricas (Priority: P3)

**Goal**: Responder con un error controlado cuando el valor de entrada no sea numérico (FR-006)

**Independent Test**: Convertir el valor "abc" y verificar que se devuelve un mensaje de error claro, sin excepción no controlada

### Tests for User Story 3

- [X] T011 [P] [US3] Test de entrada no numérica ("abc") en `tests/test_converter.py`

### Implementation for User Story 3

- [X] T012 [US3] Capturar y manejar valores no numéricos con un mensaje de error claro (FR-006), sin excepciones no controladas, en `src/conversor_temperatura/converter.py` (depende de T006)

**Checkpoint**: Las tres historias de usuario funcionan de forma independiente

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Casos borde adicionales de la spec y validación final

- [X] T013 [P] Test de casos borde: misma unidad de origen y destino (FR-007) y negativos válidos en Celsius/Fahrenheit (FR-008) en `tests/test_converter.py`
- [X] T014 Ejecutar manualmente los pasos de `quickstart.md` y confirmar que coinciden con los resultados automatizados
- [X] T015 [P] Documentar el uso de la CLI en `s4/mi-proyecto-speckit/README.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias
- **Foundational (Phase 2)**: depende de Setup — bloquea todas las historias
- **User Stories (Phase 3-5)**: dependen de Foundational; pueden implementarse en paralelo, pero se recomienda el orden P1 → P2 → P3 dado que US2 y US3 extienden la misma función `convertir` de US1
- **Polish (Phase 6)**: depende de que las historias deseadas estén completas

### Parallel Opportunities

- T004 puede avanzar en paralelo con T003 (archivos distintos)
- Las tareas de test marcadas [P] (T005, T009, T011, T013) pueden escribirse en paralelo si se trabaja en equipo, aunque todas caen en el mismo archivo `tests/test_converter.py`

---

## Implementation Strategy

### MVP First (User Story 1 solamente)

1. Completar Phase 1: Setup
2. Completar Phase 2: Foundational
3. Completar Phase 3: User Story 1
4. Validar de forma independiente antes de continuar con US2 y US3

### Incremental Delivery

1. Setup + Foundational → base lista
2. User Story 1 → validar → conversor funcional (MVP)
3. User Story 2 → validar → rechaza Kelvin inválido
4. User Story 3 → validar → maneja entradas no numéricas
5. Polish → casos borde adicionales y documentación
