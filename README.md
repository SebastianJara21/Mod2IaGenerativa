# Certificación: Programación de Backend y MCP en Python para IA Generativa
**Módulo 2**

Repositorio central de prácticas, código fuente y evidencias de entrega del curso.

---

## Estructura del Repositorio

```text
Mod2IaGenerativa/
├── docs/guias/                    # Guías de clase (referencia del profesor)
├── entregas/s02/evidencia/        # Evidencias de la Clase 2 (memoria.txt, rate_limit.txt)
├── gemini_client.py               # Clase 2: cliente base de Gemini
├── conversation.py                # Clase 2: memoria conversacional
├── s4/
│   ├── clase-sdd/                 # Clase 4, Bloque 3.A: spec a mano
│   ├── mi-proyecto-speckit/       # Clase 4 (Bloque 3.B) + Clase 5 (QA: skills/agentes/hooks)
│   └── comparacion.md             # Clase 4: spec a mano vs. Spec Kit
├── s9/
│   └── proyecto-curso-speckit/    # Clase 9: Gastos con Spec Kit completo (constitution→implement)
├── pyproject.toml / uv.lock       # Dependencias del workspace, gestionadas con uv
└── README.md                      # Este archivo — bitácora de entregas por clase
```

Cada sección de "Registro de Entregas" abajo tiene los links directos a los archivos de esa clase — no hace falta navegar el árbol a mano.

---

## Registro de Entregas

## Clase 2 — APIs de IA Generativa y memoria conversacional

### Conversación de 8 turnos (Paso 7)

Ver evidencia en `entregas/s02/evidencia/memoria.txt`.

```text
--- Turno 1 ---
USER: Me llamo Alex y mi color favorito es el verde.
[tokens] TOTAL: 56
BOT: ¡Hola, Alex! Encantado de conocerte. El verde es un color genial, fresco y natural. ¿En qué te puedo ayudar hoy?

--- Turno 2 ---
USER: ¿Qué framework de Python vimos en la Clase 1?
[tokens] TOTAL: 153
BOT: Hola, Alex. Como soy una inteligencia artificial y no tengo acceso al historial de tus clases privadas o cursos específicos, no sé qué framework vieron en tu Clase 1. 

Sin embargo, los frameworks de Python más comunes para empezar suelen ser Flask (para aplicaciones web sencillas) o FastAPI / Django (para proyectos más grandes). 

¿Te suena alguno de estos?

--- Turno 3 ---
USER: Dame un ejemplo de dato que no cabe en un int.
[tokens] TOTAL: 306
BOT: Un ejemplo clásico es la población mundial actual, que supera los 8.000 millones de personas. 

En muchos lenguajes, un int tradicional de 32 bits tiene un límite máximo de unos 2.147.483.647. Como la población mundial es mayor que ese número, causaría un desbordamiento (overflow), por lo que se necesitaría un tipo de dato más grande, como un long o un número flotante. 

En Python, los enteros se expanden automáticamente, pero en lenguajes como C++ o Java, este número rompería un int estándar.

--- Turno 4 ---
USER: ¿Qué hace el comando uv init?
[tokens] TOTAL: 376
BOT: uv init inicializa un nuevo proyecto de Python utilizando uv. 

Crea la estructura básica del proyecto, incluyendo:
* Un archivo de configuración (pyproject.toml).
* Un entorno virtual (.venv).
* Un archivo de código inicial (main.py).

--- Turno 5 ---
USER: Explica en una frase qué es un token.
[tokens] TOTAL: 415
BOT: Un token es una unidad básica de texto (una palabra o parte de ella) que los modelos de lenguaje procesan y entienden.

--- Turno 6 ---
USER: ¿Qué significa que una API sea stateless?
[tokens] TOTAL: 458
BOT: Significa que el servidor no guarda información sobre el estado del cliente entre una petición y otra; cada solicitud debe incluir todos los datos necesarios para ser procesada.

--- Turno 7 ---
USER: ¿Para qué sirve un archivo .env?
[tokens] TOTAL: 504
BOT: Sirve para almacenar variables de entorno sensibles (como contraseñas, claves de API o credenciales de bases de datos) de forma segura y separada del código fuente.

--- Turno 8 ---
USER: ¿Cómo me llamo y cuál es mi color favorito?
[tokens] TOTAL: 529
BOT: Te llamas Alex y tu color favorito es el verde.
```

### Por qué elegí ventana deslizante

Elegí la estrategia de ventana deslizante (`trim_history()` con `MAX_TURNS = 10`) porque para interacciones recientes y acotadas ofrece la máxima fidelidad sin pérdida de detalle contextual inmediato, sin incurrir en costos computacionales extra de llamadas adicionales para sintetizar (como en resumen progresivo), sin requerir heurísticas de filtrado (como memoria selectiva) ni dependencias de infraestructura o latencia adicional (como almacenamiento externo o base de datos).

### Límite de solicitudes provocado (Paso 9)

Ver evidencia en `entregas/s02/evidencia/rate_limit.txt`.

Se provocó el error 429 (`RESOURCE_EXHAUSTED` / cuota de RPM alcanzada) enviando 20 peticiones seguidas; el programa capturó la excepción `ClientError`, aplicó reintentos con retroceso exponencial (`backoff`) y completó la ejecución controladamente sin caerse.

## Clase 4 — Spec Sencilla + Spec Kit

Mismo proyecto (conversor de temperatura) implementado con dos enfoques de Spec-Driven Development, para comparar resultados.

- **Bloque 3.A — Spec a mano**: [`s4/clase-sdd/`](s4/clase-sdd/) — spec escrita a mano (`spec_manual.md`) e implementada en un solo pedido al agente. Resultados en [`s4/clase-sdd/resultados-3a.md`](s4/clase-sdd/resultados-3a.md).
- **Bloque 3.B — Spec Kit**: [`s4/mi-proyecto-speckit/`](s4/mi-proyecto-speckit/) — flujo `/speckit.specify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`. Artefactos generados en `specs/001-conversor-temperatura/`. Resultados en [`s4/mi-proyecto-speckit/resultados-3b.md`](s4/mi-proyecto-speckit/resultados-3b.md).
- **Comparación final**: [`s4/comparacion.md`](s4/comparacion.md) — tabla comparativa, los 3 casos de prueba lado a lado y la frase de cierre.

> Nota: `agy` (agente CLI del curso) alcanzó su cuota de uso individual durante el Bloque 3.B. Los 4 comandos de Spec Kit se ejecutaron con Claude Code sobre las mismas plantillas que `specify init --integration generic` generó para `agy`, así que el flujo y los artefactos producidos son equivalentes a los que se habrían obtenido con `agy`.

## Clase 5 — Pruebas, Cobertura y Seguridad (Skills, Agentes y Hooks)

Sobre el mismo proyecto de la Clase 4 (`s4/mi-proyecto-speckit/`): 7 skills de QA, 3 agentes especializados y un hook que bloquea al agente mientras los tests estén en rojo.

- **Skills** (`.agents/skills/`): [`qa-unit`](s4/mi-proyecto-speckit/.agents/skills/qa-unit/SKILL.md), [`qa-integration`](s4/mi-proyecto-speckit/.agents/skills/qa-integration/SKILL.md), [`qa-e2e`](s4/mi-proyecto-speckit/.agents/skills/qa-e2e/SKILL.md), [`qa-coverage`](s4/mi-proyecto-speckit/.agents/skills/qa-coverage/SKILL.md), [`qa-security`](s4/mi-proyecto-speckit/.agents/skills/qa-security/SKILL.md), [`qa-report`](s4/mi-proyecto-speckit/.agents/skills/qa-report/SKILL.md) (+ [`generar_reporte.py`](s4/mi-proyecto-speckit/.agents/skills/qa-report/generar_reporte.py)), [`qa-orchestrate`](s4/mi-proyecto-speckit/.agents/skills/qa-orchestrate/SKILL.md).
- **Agentes** (`.agents/agents/`): [`tester-agent`](s4/mi-proyecto-speckit/.agents/agents/tester-agent/agent.md), [`security-agent`](s4/mi-proyecto-speckit/.agents/agents/security-agent/agent.md), [`report-agent`](s4/mi-proyecto-speckit/.agents/agents/report-agent/agent.md).
- **Hook**: [`gate-tests.sh`](s4/mi-proyecto-speckit/.agents/hooks/gate-tests.sh) + [`hooks.json`](s4/mi-proyecto-speckit/.agents/hooks.json) — bloquea el fin de turno del agente mientras `pytest` falle (evento `Stop`).
- **Tests extendidos**: unitarios en [`tests/test_converter.py`](s4/mi-proyecto-speckit/tests/test_converter.py), integración en [`tests/integration/`](s4/mi-proyecto-speckit/tests/integration/), e2e en [`tests/e2e/`](s4/mi-proyecto-speckit/tests/e2e/) — 33 tests, 91% cobertura.
- **Veredicto de calidad**: [`reporte-qa.html`](s4/mi-proyecto-speckit/reporte-qa.html) → APROBADO.
- **Hallazgos de seguridad**: [`hallazgos-seguridad.md`](s4/mi-proyecto-speckit/hallazgos-seguridad.md).
- **Reflexión y cierre**: [`REFLEXION-SESION5.md`](s4/mi-proyecto-speckit/REFLEXION-SESION5.md).

> Nota: `agy` (Google Antigravity) tampoco estaba disponible para esta sesión, así que los 3 agentes se simularon con un subagente de Claude Code invocado en lenguaje natural, exactamente como indica la guía ("Usa el agente X para..."). Durante la simulación se detectaron y corrigieron 2 desviaciones reales del subagente — documentadas en `REFLEXION-SESION5.md`.

## Proyecto Integrador — Seguimiento de Hábitos (Sesión 9-10)

Proyecto final evaluado con presentación en vivo (REST + MCP funcionando). Aplica la misma arquitectura y forma de trabajar de "Gastos" (Sesiones 6-8) a una idea propia, siguiendo el flujo completo de Spec Kit: [`proyecto-integrador-habitos/`](proyecto-integrador-habitos/).

- **Artefactos de Spec Kit**: [`constitution.md`](proyecto-integrador-habitos/.specify/memory/constitution.md) (7 artículos), [`spec.md`](proyecto-integrador-habitos/specs/001-habits-tracker/spec.md) (con `/speckit.clarify` resuelto), [`plan.md`](proyecto-integrador-habitos/specs/001-habits-tracker/plan.md), [`tasks.md`](proyecto-integrador-habitos/specs/001-habits-tracker/tasks.md) (55 tareas).
- **REST**: 6 endpoints (`usuarios/`, `habitos/`) — código en [`app/routers/`](proyecto-integrador-habitos/app/routers/).
- **MCP**: 4 tools (`crear_habito`, `listar_habitos`, `marcar_habito`, `eliminar_habito`) sobre transporte `streamable-http` estándar del SDK oficial — [`app/mcp/server.py`](proyecto-integrador-habitos/app/mcp/server.py). Verificado con el cliente oficial del SDK: sesión inicializada, tools listadas, tool invocada con resultado real.
- **Testing**: 109/109 tests en verde, cobertura 91% (`services/` 96.5% ≥90%, conjunto 93.5% ≥70% — umbrales de la constitución).
- **Seguridad**: OAuth2 + JWT (HS256), contraseñas con `passlib[bcrypt]`, secretos solo en `.env` (nunca versionado), autorización siempre desde el JWT.

> Nota: igual que en las prácticas anteriores, `agy` no estaba disponible — el flujo completo (`/speckit.constitution` → `/speckit.specify`+`/speckit.clarify` → `/speckit.plan`+`/speckit.analyze` → `/speckit.implement`) se ejecutó con un subagente de Claude Code simulando a `agy`, con verificación independiente después de cada fase. Se encontraron y corrigieron 10 desviaciones reales durante el proceso — desde una decisión de negocio tomada en silencio (fecha futura al marcar un hábito) hasta que el servidor MCP inicial no existía y, en su segundo intento, no hablaba el protocolo estándar. El detalle completo de cada corrección queda documentado en el historial de commits.
