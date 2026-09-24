# Feature Specification: Conversor de Temperatura

**Feature Branch**: `001-conversor-temperatura`

**Created**: 2026-09-23

**Status**: Draft

**Input**: User description: "Quiero un programa que convierta una temperatura entre Celsius, Fahrenheit y Kelvin. Debe convertir correctamente entre las tres unidades, redondear el resultado a 2 decimales, y rechazar una temperatura en Kelvin menor a 0 con un mensaje de error claro. Como casos borde: debe manejar una entrada no numérica (ej. "abc") con un error claro sin excepciones no controladas, debe devolver el mismo valor si la unidad de entrada y salida es la misma, y debe procesar correctamente números negativos válidos en Celsius y Fahrenheit."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Convertir temperatura entre unidades (Priority: P1)

Un usuario ingresa un valor numérico de temperatura junto con la unidad de origen y la unidad de destino, y el sistema devuelve el valor convertido.

**Why this priority**: Es la funcionalidad central del programa; sin ella no hay producto.

**Independent Test**: Se puede probar ingresando 100 en Celsius con destino Fahrenheit y verificando que el resultado es 212.00.

**Acceptance Scenarios**:

1. **Given** una temperatura válida en Celsius, **When** el usuario solicita convertirla a Fahrenheit, **Then** el sistema devuelve el valor correcto redondeado a 2 decimales.
2. **Given** una temperatura válida en cualquiera de las tres unidades, **When** el usuario solicita convertirla a cualquiera de las otras dos, **Then** el sistema devuelve el valor correcto redondeado a 2 decimales.

---

### User Story 2 - Rechazar temperaturas Kelvin inválidas (Priority: P2)

Un usuario ingresa una temperatura en Kelvin menor a 0, y el sistema rechaza la operación con un mensaje de error claro.

**Why this priority**: Protege la validez física del dato (0 K es el cero absoluto); sin esta regla el sistema podría devolver resultados sin sentido.

**Independent Test**: Se puede probar ingresando -10 en Kelvin y verificando que el sistema devuelve un mensaje de error en vez de un resultado numérico.

**Acceptance Scenarios**:

1. **Given** una temperatura en Kelvin menor a 0, **When** el usuario solicita la conversión, **Then** el sistema rechaza la operación con un mensaje de error claro.

---

### User Story 3 - Manejar entradas no numéricas (Priority: P3)

Un usuario ingresa un valor que no es un número, y el sistema responde con un error controlado en vez de fallar de forma inesperada.

**Why this priority**: Mejora la robustez del programa ante errores de uso; no es el flujo principal pero evita fallos sin control.

**Independent Test**: Se puede probar ingresando "abc" como valor y verificando que el sistema devuelve un mensaje de error claro sin una excepción no controlada.

**Acceptance Scenarios**:

1. **Given** un valor de entrada no numérico, **When** el usuario solicita la conversión, **Then** el sistema devuelve un mensaje de error claro sin lanzar una excepción no controlada.

---

### Edge Cases

- ¿Qué pasa si la unidad de entrada y la unidad de salida son la misma? El sistema debe devolver el mismo valor sin alterarlo.
- ¿Qué pasa si el valor ingresado es un número negativo válido en Celsius o Fahrenheit? El sistema debe procesarlo con normalidad, ya que son valores físicamente posibles en esas escalas.
- ¿Qué pasa si el valor ingresado en Kelvin es menor a 0? El sistema debe rechazarlo (ver User Story 2).
- ¿Qué pasa si el valor de entrada no es numérico? El sistema debe rechazarlo con un error claro (ver User Story 3).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST convertir correctamente una temperatura de Celsius a Fahrenheit y viceversa.
- **FR-002**: El sistema MUST convertir correctamente una temperatura de Celsius a Kelvin y viceversa.
- **FR-003**: El sistema MUST convertir correctamente una temperatura de Fahrenheit a Kelvin y viceversa.
- **FR-004**: El sistema MUST redondear el resultado de toda conversión a 2 decimales.
- **FR-005**: El sistema MUST rechazar una temperatura en Kelvin menor a 0 con un mensaje de error claro.
- **FR-006**: El sistema MUST devolver un mensaje de error claro, sin excepciones no controladas, cuando el valor de entrada no sea numérico.
- **FR-007**: El sistema MUST devolver el mismo valor de entrada cuando la unidad de origen y la unidad de destino sean iguales.
- **FR-008**: El sistema MUST procesar correctamente números negativos válidos en Celsius y Fahrenheit.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un usuario puede convertir una temperatura entre cualquiera de las tres unidades y obtener el resultado correcto en un solo intento.
- **SC-002**: El 100% de las entradas no numéricas o temperaturas Kelvin inválidas producen un mensaje de error claro en vez de un fallo inesperado.
- **SC-003**: Todo resultado de conversión se presenta redondeado a exactamente 2 decimales.

## Assumptions

- El programa se usa como una herramienta de un solo uso por invocación (no requiere persistir historial de conversiones).
- No hay requisitos de interfaz gráfica; una interfaz de línea de comandos es suficiente.
- El rango de temperaturas soportado no tiene límite superior explícito, solo el límite físico inferior de 0 K.
