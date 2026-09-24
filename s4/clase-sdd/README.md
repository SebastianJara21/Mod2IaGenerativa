# Conversor de Temperatura (clase-sdd)

Implementación guiada por especificación (SDD - *Spec-Driven Development*) para convertir temperaturas entre Celsius (°C), Fahrenheit (°F) y Kelvin (K).

## Características y Cumplimiento de la Especificación

- **Conversión completa:** Celsius ↔ Fahrenheit ↔ Kelvin.
- **Redondeo:** Resultados con precisión de 2 decimales.
- **Cero absoluto en Kelvin:** Rechazo estricto de temperaturas menores a 0 K con mensaje descriptivo.
- **Manejo de casos borde:**
  - Control de valores no numéricos sin excepciones no controladas.
  - Conversión entre la misma unidad devuelve el mismo valor.
  - Soporte de números negativos válidos (ej. -40 °C = -40 °F).
- **Flexibilidad:** Admite unidades en minúsculas/mayúsculas (`c`, `f`, `k`), nombres completos (`celsius`, `fahrenheit`, `kelvin`) y formatos compuestos (`100C`, `-40F`).

---

## Uso

### 1. Vía CLI
```bash
# Caso normal (100 C a F)
uv run clase-sdd 100 C F
# Salida: 100.00 °C = 212.00 °F

# Formato compuesto
uv run clase-sdd 100C F
# Salida: 100.00 °C = 212.00 °F

# Minúsculas
uv run clase-sdd 100 c k
# Salida: 100.00 °C = 373.15 K

# Caso borde: Entrada no numérica
uv run clase-sdd abc C F
# Salida: Error: Valor no numérico como entrada ('abc'). Ingrese un número válido.

# Caso borde: Kelvin < 0
uv run clase-sdd -10 K C
# Salida: Error: La temperatura en Kelvin no puede ser menor a 0 K (recibido: -10.0 K).
```

### 2. Modo Interactivo
```bash
uv run clase-sdd
```

### 3. Ejecución de Pruebas Unitarias
```bash
uv run python -m unittest discover tests
```
