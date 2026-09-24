# Data Model: Conversor de Temperatura

No hay persistencia de datos en esta feature. El siguiente modelo describe únicamente las estructuras usadas en memoria durante una conversión.

## Entidades

### Unidad de Temperatura

Enumeración cerrada de las tres escalas soportadas.

- Valores: `Celsius`, `Fahrenheit`, `Kelvin`
- Validación: cualquier valor fuera de este conjunto se rechaza con un error claro.

### Lectura de Temperatura

Representa un valor de entrada o salida.

| Campo | Tipo | Validación |
|---|---|---|
| `valor` | número decimal | Debe ser numérico (FR-006); si la unidad es Kelvin, debe ser ≥ 0 (FR-005) |
| `unidad` | Unidad de Temperatura | Debe ser una de las tres unidades soportadas |

### Resultado de Conversión

| Campo | Tipo | Regla |
|---|---|---|
| `valor` | número decimal | Redondeado a 2 decimales (FR-004) |
| `unidad` | Unidad de Temperatura | Unidad de destino solicitada |

**Relación**: una conversión toma una Lectura de Temperatura (origen) y una Unidad de Temperatura (destino), y produce un Resultado de Conversión. Si origen y destino coinciden, el resultado es igual al valor de entrada (FR-007).
