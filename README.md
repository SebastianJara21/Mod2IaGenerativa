# Certificación: Programación de Backend y MCP en Python para IA Generativa
**Módulo 2**

Repositorio central de prácticas, código fuente y evidencias de entrega del curso.

---

## Estructura del Repositorio

```text
Mod2IaGenerativa/
├── docs/                          # Guías de clase y material de referencia
│   └── guias/
│       ├── practica_01.md
│       └── practica-vibecoding-guiado.md
├── entregas/                      # Evidencias de entrega organizadas por sesión
│   └── s02/
│       └── evidencia/
│           ├── memoria.txt
│           └── rate_limit.txt
├── gemini_client.py               # Cliente base de Gemini (inspección de tokens y roles)
├── conversation.py                # Memoria conversacional (ventana deslizante y rate limit)
├── .env.example                   # Plantilla de variables de entorno
├── .gitignore                     # Configuración de seguridad (ignora .env y entornos)
├── pyproject.toml                 # Configuración de dependencias gestionado con uv
└── README.md                      # Documentación del proyecto y bitácora de entregas
```

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
