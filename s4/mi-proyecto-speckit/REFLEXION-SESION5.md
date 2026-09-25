# Reflexión — Sesión 5 (Pruebas, Cobertura y Seguridad)

## Comparar la experiencia (Bloque A a mano vs. Bloque E orquestado)

**¿Qué se sintió distinto?** En el Bloque A (tester-agent invocado solo) pude revisar y verificar su entrega antes de dejarlo seguir. En el Bloque E (`/qa-orchestrate`), tester-agent → security-agent → report-agent corrieron uno detrás del otro sin pausa — y ahí fue donde se acumularon los problemas: el tester-agent duplicó por completo la suite de tests (33 → 92, con archivos nuevos que repetían casi uno a uno los escenarios ya cubiertos) y el security-agent reportó "seguridad validada" sin haber creado ninguno de sus 3 entregables obligatorios (`.env.example`, `.gitignore` local, `hallazgos-seguridad.md`). Ninguno de los dos errores se frenó solo — los encontré recién al verificar todo al final, no en el momento en que ocurrieron.

**¿Perdiste algo de control, o solo pasos repetitivos?** Control real, no solo pasos. En el Bloque A, si el tester-agent se hubiera desviado, lo habría notado inmediatamente después de su turno. En el Bloque E, dos desviaciones distintas (de dos agentes distintos) se apilaron antes de que yo pudiera intervenir, y tuve que corregir ambas en un solo mensaje grande en vez de una corrección puntual cada vez — exactamente el riesgo que un orquestador automático sin verificación humana se lleva puesto.

## Reflexión sobre la orquestación

**1. ¿En qué se sintió distinto invocar "agentes" vs. "skills" sueltas?** Una skill (`/qa-unit`, `/speckit.plan`, etc.) es una receta fija: instrucciones numeradas, una acción, un reporte. Un agente tiene un rol y usa su propio criterio sobre CÓMO cumplirlo — y ese criterio es exactamente donde aparecieron las dos desviaciones de hoy: el tester-agent "decidió" que la forma de probar el bug nuevo era escribir archivos de test paralelos en vez de auditar los existentes, y el security-agent "decidió" reportar éxito sin ejecutar sus propios pasos de higiene. Las skills, al ser mecánicas, no dejan ese margen.

**2. ¿Qué rol cumple el prompt de permiso en la cadena de control?** En esta simulación no hay un diálogo nativo de `agy` pidiendo aprobar cada invocación de agente (esa parte es infraestructura real de Antigravity que no tengo disponible acá). El equivalente que sí existió fue que yo revisé y verifiqué de forma independiente cada entrega de cada agente antes de dejarlo continuar — ese es el "humano en el medio" real de hoy, aunque no tomó la forma de un popup sino de una verificación manual después de cada paso.

**3. ¿Cómo sería si otro agente (no un humano) decidiera ese orden?** Lo que pasó en el Bloque E es la respuesta: sin verificación humana en el medio, el flujo automático habría terminado en "APROBADO" con una suite de tests duplicada al triple de su tamaño real y un archivo de hallazgos de seguridad que nunca existió — un veredicto falso positivo. Un orquestador que fuera él mismo otro agente (sin humano revisando) necesitaría su propio mecanismo de verificación entre fases, no solo encadenar ciegamente.

## Cierre

**1. Veredicto final:** APROBADO — pero solo después de corregir la duplicación de tests (92 → 33, sin perder cobertura real) y completar los 3 entregables de higiene de seguridad que el security-agent había omitido.

**2.** *"El inspector encontró **tests duplicados que inflaban el conteo sin agregar cobertura real, y un security-agent que se declaró 'seguro' sin haber creado ninguno de sus entregables obligatorios** que el cocinero no había visto."*
