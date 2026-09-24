/# Contexto del Proyecto — Módulo 2: IA Generativa
## Para: Agente que retoma el trabajo en este repositorio

---

## El Proyecto

**Repositorio:** https://github.com/SebastianJara21/Mod2IaGenerativa.git  
**Ruta local:** `c:\Users\sebas\Documents\Cursos\CEDIA TMO\IA-GENERATIVA\Módulo 2\Code\practica2`  
**Estudiante:** Sebastian Jara (SebastianJara21)  
**Curso:** Programación de Backend y MCP en Python para IA Generativa (10 sesiones)  
**Entorno:** Python 3.12, `uv` para gestión de paquetes, `agy` como agente de IA de línea de comandos.

---

## Estructura del Repositorio

```
Mod2IaGenerativa/
├── docs/guias/               # Guías de clase (solo referencia, no se entregan)
│   ├── practica_01.md        # Sesión 2: Gemini API y memoria
│   ├── practica-02.md        # Sesión 3: Vibe Coding
│   └── practica-03.md        # Sesión 4: Spec Manual + Spec Kit (EN PROGRESO)
├── entregas/                 # Evidencias de entrega
│   └── s02/evidencia/
│       ├── memoria.txt       # ✅ Salida de conversación de 8 turnos
│       └── rate_limit.txt    # ✅ Captura del error 429 manejado
├── s4/                       # Sesión 4 (EN PROGRESO)
│   ├── clase-sdd/            # Bloque 3.A: Spec manual — COMPLETO
│   │   ├── spec_manual.md
│   │   ├── resultados-3a.md  # ✅ 3 casos probados y documentados
│   │   └── src/              # Código generado por agy (conversor de temperatura)
│   ├── mi-proyecto-speckit/  # Bloque 3.B: Spec Kit — COMPLETO
│   │   ├── specs/001-conversor-temperatura/  # spec.md, plan.md, tasks.md, etc.
│   │   ├── src/conversor_temperatura/        # Código generado siguiendo tasks.md
│   │   └── resultados-3b.md  # ✅ 3 casos probados y documentados
│   └── comparacion.md        # ✅ Tabla comparativa + frase de cierre
├── vibe-coding/              # Sesión 3: código desechable (no se commitea)
│   └── notas.md              # Notas de predicciones y reflexiones completadas
├── gemini_client.py          # ✅ Cliente Gemini: parámetros explícitos, tokens, finish_reason
├── conversation.py           # ✅ Memoria conversacional: ventana deslizante MAX_TURNS=10, backoff 429/5xx
├── .env                      # Clave real (gitignored)
├── .env.example              # Plantilla pública
├── pyproject.toml            # Dependencias: google-genai>=2.25.0, python-dotenv>=1.2.3
├── uv.lock
└── README.md                 # Bitácora del curso con sección Clase 2 completa
```

---

## Estado por Sesión

### ✅ Sesión 2 — APIs de IA Generativa y Memoria Conversacional (ENTREGADA)
- **Modelo usado:** `gemini-3.5-flash-lite` (gemini-2.5-flash no disponible para cuentas nuevas)
- **Archivos clave:** `gemini_client.py`, `conversation.py`
- **Cumple el checklist completo:** system_instruction, temperature, max_output_tokens explícitos; total_token_count por llamada; finish_reason; ClientError (429 con backoff) y ServerError (5xx); API key en variable de entorno; evidencias en `entregas/s02/evidencia/`
- **README:** tiene sección "Clase 2" completa con transcripción, justificación de ventana deslizante y confirmación de rate-limit
- **Git:** commiteado y pusheado en rama `master`

### ✅ Sesión 3 — Vibe Coding (ENTREGADA, sin repo)
- **Entregable:** PDF para AVAC (no requiere repo)
- **Código:** en `vibe-coding/` (desechable, no forma parte de la entrega de repositorio)
- **notas.md:** completado con predicciones, resultados de 3 rondas, falla provocada (TypeError: NoneType) y 3 preguntas de reflexión final
- **Estado:** texto del informe generado, el usuario debe armar el PDF con capturas y subir al AVAC

### 🔄 Sesión 4 — Spec Manual + Spec Kit (EN PROGRESO)
**Bloque 3.A — Spec a mano:** ✅ COMPLETO
- Proyecto: conversor de temperatura (Celsius / Fahrenheit / Kelvin)
- `spec_manual.md` creado con Objetivo, Criterios de Aceptación (4 verificables) y Casos Borde (3)
- `agy` implementó el código en `s4/clase-sdd/src/` con tests
- `resultados-3a.md` completo con los 3 casos: normal (100°C→212°F ✅), borde ("abc" y -10K dan error controlado ✅), no contemplado (minúsculas 'c' manejadas automáticamente ✅)
- Falta: 📸 Captura 1 (el usuario toma la captura manualmente)

**Bloque 3.B — Spec Kit:** ✅ COMPLETO
- `specify-cli` instalado globalmente (`uv tool install`); `agy` no apareció como integración soportada oficialmente, así que se usó el plan B de la guía: `--integration generic --integration-options="--commands-dir .agy/commands/"`
- **Importante:** `agy` alcanzó su cuota de uso individual durante este bloque (bloqueo ~165h). Los 4 comandos se ejecutaron con **Claude Code** en su lugar, sobre las mismas plantillas generadas en `.agy/commands/` (son agnósticas del agente)
- Los comandos reales quedaron con **punto**, no guion: `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement` (la guía dice `/speckit-specify` etc., desactualizado frente a la versión instalada del CLI)
- Feature creada: `s4/mi-proyecto-speckit/specs/001-conversor-temperatura/` (spec.md, plan.md, research.md, data-model.md, quickstart.md, tasks.md — 15 tareas, todas marcadas `[X]`)
- Código implementado en `s4/mi-proyecto-speckit/src/conversor_temperatura/`, 14 tests pasando (`uv run pytest -q`)
- `resultados-3b.md` completo con los mismos 3 casos que 3.A. Hallazgo del caso no contemplado: la implementación de Spec Kit **no** tolera unidades en minúscula (a diferencia de la de `agy` en 3.A, que sí las normalizó por iniciativa propia) — documentado como el hallazgo más interesante de la comparación
- Falta: 📸 Captura 2 (el usuario toma la captura manualmente del flujo `/speckit.specify → /speckit.implement`)

**Pendiente completo de Sesión 4:**
- [x] Bloque 3.B ejecutado y `resultados-3b.md` completado
- [x] `s4/comparacion.md`: tabla comparativa + frase de cierre
- [x] README.md actualizado con sección "Clase 4"
- [ ] Commit + push de todo `s4/`
- [ ] PDF para AVAC: breve explicación + Captura 1 (spec a mano) + Captura 2 (flujo speckit) + tabla comparativa + enlace al repo

---

## Reglas y Convenciones del Proyecto

1. **El código del repo y los commits van en español** (el usuario rechazó commit en inglés).
2. **Sin overengineering**: solo lo que pide la guía, nada más.
3. **`.env` nunca se sube:** está en `.gitignore` y verificado.
4. **Modelo:** `gemini-3.5-flash-lite` es el que funciona con la clave actual (gemini-2.5-flash retorna 404 "no longer available to new users").
5. **Las guías del profesor** (`docs/guias/`) van en el repo como referencia (Opción A acordada), no en la raíz.
6. **Código de Sesión 3** (vibe-coding/) no se sube al repo — es desechable por diseño.
7. **Estructura de commits:** un commit al final de cada bloque importante, mensaje descriptivo en español.

---

## Próximas Sesiones (referencia)
- **Sesión 5 (Jueves):** retomar el código de `s4/` para agregarle tests reales y revisión de seguridad básica. No se empieza proyecto nuevo.
- **Sesiones 6-10:** pendiente de guías.
