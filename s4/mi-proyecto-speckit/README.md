# Conversor de Temperatura — Spec Kit (Bloque 3.B)

Mismo proyecto del Bloque 3.A (`s4/clase-sdd/`), esta vez construido con el flujo de [Spec Kit](https://github.com/github/spec-kit): `/speckit.specify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`.

Los artefactos generados por cada comando están en `specs/001-conversor-temperatura/`.

## Uso

```bash
uv sync
uv run conversor-speckit <valor> <unidad_origen> <unidad_destino>
```

Ejemplo:

```bash
uv run conversor-speckit 100 C F
# 100.00 C = 212.00 F
```

Unidades soportadas: `C` (Celsius), `F` (Fahrenheit), `K` (Kelvin).

## Pruebas

```bash
uv run pytest -q
```
