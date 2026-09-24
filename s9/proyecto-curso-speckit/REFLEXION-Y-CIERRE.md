# Reflexión y Cierre (Paso 9) + Checklist de autoverificación

## Reflexión

**1. ¿Qué artículo tuviste que "defender" activamente?**

El Artículo VIII (Compatibilidad con el proyecto de referencia), dos veces, durante `/speckit-clarify` — antes incluso de llegar a `/speckit-implement`:
- El agente recomendó que el límite de 500 por categoría se reseteara mensualmente. Rompía la firma fija `total_por_categoria(db, usuario_id, categoria) -> float` (sin parámetro de fecha). Lo corregí a "cumulativo sin reset".
- El agente recomendó agregar PATCH/DELETE de gastos "porque suena razonable para un CRUD completo". No estaba en la tabla de endpoints ni en el contrato de firmas — era scope no pedido. Lo corregí a solo POST/GET.

En ambos casos el agente sugirió la opción "más completa" por defecto, no la que decía la spec. Sin el Artículo VIII escrito explícitamente, no habría tenido con qué rebatirlo más que "no me gusta" — con él, la respuesta fue mecánica: "esa firma no tiene ese parámetro, esa tabla no tiene ese endpoint".

**2. Tiempo pensando vs. escribiendo, comparado con sesiones anteriores donde se escribía código a mano.**

Casi todo el tiempo se fue en orquestar y revisar, no en redactar: la constitución y la spec ya venían dadas por la guía, listas para pegar — lo que sí consumió tiempo real fue leer cada reporte del agente contra cada artículo antes de aprobarlo. La sesión terminó recortada por tiempo real de entrega (quedaron ~8-10 min antes de la hora límite), lo cual es en sí mismo el hallazgo: escribir la spec fue rápido, pero **verificar que el agente no se saliera de ella task por task** es el trabajo que de verdad consume el tiempo — y es exactamente el trabajo que en las Sesiones 6-8 (escribiendo a mano) no existía, porque uno mismo era quien decidía cada línea.

**3. Si el umbral de cobertura no se hubiera puesto por escrito, ¿el agente se habría detenido en 60% sin decírtelo?**

Con base en lo que sí se observó (dos veces el agente ofreció por su cuenta la opción más cómoda/genérica en vez de la más ceñida a la spec), la respuesta razonable es sí. El patrón fue consistente: ante una decisión no forzada por texto explícito, el agente elige la opción "de manual" antes que la exacta — el mismo comportamiento que haría plausible que se detuviera en un umbral de cobertura cómodo si nadie hubiera escrito el número exacto.

> "Hoy la especificación reemplazó al código como fuente de verdad. Lo comprobé cuando el agente propuso dos veces la opción 'razonable' que no era la que decía el contrato, y el artículo de la constitución que más me costó defender fue el VIII (compatibilidad) — porque exige rechazar sugerencias que suenan bien pero no están en el texto."

---

## Checklist de autoverificación (estado real a la hora de entrega)

- [x] `constitution.md` tiene los 8 artículos, cada uno verificable
- [x] `spec.md` incluye tabla de endpoints REST, equivalente MCP, contrato de compatibilidad y los 5 casos de error explícitos
- [x] Corrí `/speckit-clarify` y resolví 2 ambigüedades (ambas corregidas contra el Artículo VIII, ver Reflexión)
- [x] `plan.md` conecta cada decisión técnica con su artículo
- [x] `tasks.md` (64 tareas) sin tarea de código sin test emparejado, con tarea final de cobertura
- [x] Corrí `/speckit-analyze` — 0 desviaciones encontradas, error 4 y 5 explícitamente cubiertos en tasks.md
- [ ] Usé el prompt de verificación tarea-por-tarea de `/speckit-implement` — **no llegué a correrlo, sin tiempo**
- [ ] Corregí una desviación durante `/speckit-implement` — **no aplica, no se ejecutó** (sí corregí 2 desviaciones durante `/speckit-clarify`, ver Reflexión pregunta 1)
- [ ] `pytest --cov=app` cumple el umbral del Artículo VII.3 — **no aplica, no hay código implementado**
- [ ] Los 5 casos de error tienen test identificable corriendo en verde — **están en tasks.md, no ejecutados**
- [ ] Tests de `test_gastos.py`, `test_integracion_gastos.py`, `test_api_gastos.py` (S6-S8) pasan sin modificar — **no copiados, no corridos**
- [ ] Tools MCP reutilizan `services/gastos.py` — **no implementado**
- [ ] Autorización nunca acepta `usuario_id` del cliente — **diseñado así en spec/plan/tasks, no verificado en código porque no existe código**

**Estado honesto:** documentos de especificación (constitution → spec → plan → tasks → analyze) completos y consistentes entre sí. Implementación (`/speckit-implement`, Pasos 7-8) no ejecutada por límite de tiempo real de entrega.
