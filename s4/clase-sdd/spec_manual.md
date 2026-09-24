# Especificación: Conversor de Temperatura

## Objetivo
Convertir una temperatura entre Celsius, Fahrenheit y Kelvin.

## Criterios de aceptación
- [x] Convierte correctamente de Celsius a Fahrenheit y viceversa
- [x] Convierte correctamente de Celsius a Kelvin y viceversa
- [x] Redondea el resultado a 2 decimales
- [x] Rechaza una temperatura en Kelvin menor a 0 con un mensaje de error claro

## Casos borde
- Valor no numérico como entrada (ej. "abc") → emitir un mensaje de error claro sin excepciones no controladas.
- Misma unidad de entrada y salida (ej. Celsius a Celsius) → debe devolver el mismo número.
- Números negativos válidos en Celsius y Fahrenheit (ej. -40°C = -40°F) → deben procesarse sin problema.
