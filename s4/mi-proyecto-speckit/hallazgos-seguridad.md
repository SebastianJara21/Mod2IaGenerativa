# Hallazgos de Seguridad - Conversor de Temperatura

## Tabla de Hallazgos

| Caso | Lo que se encontró | Corrección sugerida |
|---|---|---|
| 🔑 Secreto expuesto | Sin hallazgos | No hay claves, contraseñas o tokens hardcodeados en el código. El proyecto no utiliza API keys ni credenciales. |
| 🧪 Validación de entradas | Sin hallazgos | Las funciones `parse_valor()` y `parse_unidad()` validan correctamente tipos de entrada. La función `convertir()` valida rangos válidos (rechaza Kelvin negativo). Todas las entradas de usuario pasan por validación explícita. |
| 🚪 Manejo de excepciones | Sin hallazgos | No hay bloques `except:` genéricos ni `except: pass`. Todas las excepciones son específicas (`except ValueError`). Se usa encadenamiento de excepciones apropiadamente con `from None`. |

## Acciones de higiene aplicadas

1. **Creado `.env.example`**: Archivo de plantilla para variables de entorno creado (aunque el proyecto actualmente no las utiliza). Contiene instrucciones claras de que no debe cometerse a control de versiones.

2. **Creado `.gitignore`**: Archivo de exclusión de git creado en la raíz del proyecto con:
   - Línea `.env` para excluir archivos de entorno
   - Exclusiones estándar para Python (.venv, __pycache__, *.pyc, etc.)
   - Exclusiones para IDEs y sistemas operativos

3. **Verificado con git**: Confirmado que `.env` está siendo ignorado correctamente:
   - `git check-ignore -q .env` → Exit code 0 (ignorado)
   - `git ls-files --error-unmatch .env` → Exit code 1 (.env NO está trackeado)

## Conclusión

✅ El proyecto cumple con los estándares básicos de seguridad. No hay secretos expuestos, la validación de entrada es robusta y el manejo de excepciones es apropiado. La infraestructura de higiene (.env.example y .gitignore) está ahora en su lugar para proteger futuras adiciones de variables de entorno.
