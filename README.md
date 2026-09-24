# Práctica 2 — Programación de Backend y MCP en Python para IA Generativa

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
