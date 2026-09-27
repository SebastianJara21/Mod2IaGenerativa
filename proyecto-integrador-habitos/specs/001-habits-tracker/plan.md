# Implementation Plan: Personal Habits Tracker

**Branch**: `001-habits-tracker` | **Date**: 2026-09-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-habits-tracker/spec.md`

## Summary

Personal habit tracking system with user registration, JWT authentication, habit CRUD operations, daily mark tracking with retroactive support (but no future dates), and MCP tools equivalence. 

**Technical Approach**: FastAPI web service with SQLAlchemy ORM, Alembic migrations, SQLite (dev) / Postgres (prod), JWT auth via pyjwt + passlib[bcrypt], MCP server integrated via streamable-http within the same app. Layered architecture (routers/services/repositories/utils) enforced by package structure and DIP for testability.

## Technical Context

**Language/Version**: Python 3.10+

**Primary Dependencies**: 
- FastAPI + uvicorn[standard]
- SQLAlchemy + Alembic
- pyjwt (JWT signing, single library — no alternatives)
- passlib[bcrypt] + bcrypt<4.1 (passlib 1.7.4 runtime compatible; newer bcrypt versions break passlib)
- pydantic-settings (BaseSettings for .env)
- email-validator, python-multipart (pydantic.EmailStr and OAuth2PasswordRequestForm dependencies)
- SDK official "mcp" (streamable-http transport)
- pytest + pytest-cov + httpx (testing)

**Storage**: SQLite (development), PostgreSQL (production) via conditional `connect_args` in database.py

**Testing**: pytest with fixtures (in-memory SQLite), app.dependency_overrides for API tests, pytest-cov for coverage verification

**Target Platform**: Linux server (API), MCP server (streamable-http)

**Project Type**: Web service + MCP server (integrated)

**Performance Goals**: No explicit SLA in spec; assume standard web app expectations (<1s pagination, <2 interactions for auth)

**Constraints**: 
- Passwords never exposed in responses
- Ownership always enforced via JWT usuario_id, never from input
- No future date marking allowed (FR-11a)
- Secret/Database URL in .env only (never versionable)

**Scale/Scope**: Single user system; per-user habit tracking with daily marks. No explicit user volume target; assume low concurrency (v1 simplicity).

## Constitution Check

**GATE 1: PASS** — Layered Architecture (Artículo I)
- routers/services/repositories/utils/mcp as separate packages under `app/`
- No cross-layer imports violating dependency direction
- mcp/tools/ never reimplements services/ logic

**GATE 2: PASS** — SOLID Principles (Artículo II)
- SRP: services/ functions single responsibility, _validar_x separate from orquestación
- OCP: Constants/Enums for extensibility (e.g., frecuencia range 1-7)
- DIP: Services receive repositories as parameters with defaults (no direct imports), not unittest.mock
- No artificial LSP/ISP enforcement (no formal interfaces required)

**GATE 3: PASS** — Persistence (Artículo III)
- SQLAlchemy ORM (no raw SQL strings)
- Alembic for migrations
- SQLite dev + Postgres prod, single database.py
- All Habito/Marca queries filter by usuario_id (ownership enforcement)

**GATE 4: PASS** — Security (Artículo IV)
- Passwords: passlib.context.CryptContext(schemes=["bcrypt"]) — single library, no alternatives
- Auth: pyjwt HS256, configurable ACCESS_TOKEN_EXPIRE_MINUTES (never infinite)
- .env for SECRET_KEY + DATABASE_URL (never versionable, .env.example provided)
- Authorization: usuario_id from JWT (get_current_user), never from URL/body/query params
- Unhandled Exception → 500 generic message (never stack trace)
- All input validated with Pydantic schemas before services/

**GATE 5: PASS** — REST Design (Artículo V)
- POST→201, GET→200, 401/404/400/422/403/204 as specified
- Pagination: skip/limit query params with defaults, 422 on invalid
- Input/output schemas separate (never expose SQLAlchemy models)

**GATE 6: PASS** — MCP Integration (Artículo VI)
- Each tool (crear_habito, marcar_habito, listar_habitos, eliminar_habito) calls services/ directly
- Tool descriptions specific, not generic
- Errors returned as {"error": "..."}, not unhandled exceptions
- eliminar_habito: explicit server-side confirmation required (not model-dependent)
- streamable-http: JWT identity extracted from Authorization header, used by get_current_user

**GATE 7: PASS** — Testing (Artículo VII)
- Pyramid: unitarias (mayoría) → integración → API/E2E (minoría)
- Unit tests: fake repository injected as parameter (no unittest.mock)
- Coverage goals: services/ ≥90%, ensemble ≥70%
- Integration tests: real SQLite in-memory DB
- API tests: app.dependency_overrides for get_db, repo, get_current_user
- Each MCP tool: 2+ tests (success + business error)
- Every task.md requirement: test in green before completion
- Coverage exclusions declared in [tool.coverage.run] omit: main.py, mcp/server.py, mcp/auth.py, startup/shutdown

## Project Structure

### Documentation (this feature)

```text
specs/001-habits-tracker/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (Phase 1 in progress)
├── research.md          # Phase 0 research artifacts (to be generated)
├── data-model.md        # Phase 1 data model (to be generated)
├── quickstart.md        # Phase 1 validation guide (to be generated)
├── contracts/           # Phase 1 REST + MCP contracts (to be generated)
│   ├── REST_API.md
│   └── MCP_TOOLS.md
├── checklists/
│   └── requirements.md   # Quality checklist (completed)
└── tasks.md             # Phase 2 task breakdown (later, /speckit-tasks)
```

### Source Code (repository root)

```text
app/
├── __init__.py
├── main.py              # FastAPI + MCP server startup
├── database.py          # SQLAlchemy engine, conditional connect_args (SQLite vs Postgres)
├── config.py            # pydantic_settings.BaseSettings (.env loading)
│
├── routers/             # HTTP handlers, translate to/from services
│   ├── __init__.py
│   ├── usuarios.py      # POST /usuarios/, POST /usuarios/token
│   └── habitos.py       # POST/GET /habitos/, POST /habitos/{id}/marcar, DELETE /habitos/{id}
│
├── services/            # Business logic, no SQLAlchemy/Session imports
│   ├── __init__.py
│   ├── usuarios.py      # crear_usuario, autenticar_usuario, get_current_user
│   └── habitos.py       # crear_habito, listar_habitos, marcar_habito, eliminar_habito (_validar_fecha, etc.)
│
├── repositories/        # DB persistence only, no business rules
│   ├── __init__.py
│   ├── usuarios.py      # save_usuario, get_usuario_by_email, etc.
│   └── habitos.py       # save_habito, get_habitos_by_usuario, get_marca, etc.
│
├── models/              # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── usuario.py       # Usuario (id, email, password_hash, created_at)
│   └── habito.py        # Habito (id, usuario_id FK, nombre, frecuencia_objetivo, created_at)
│                        # Marca (id, habito_id FK, usuario_id FK, fecha, created_at)
│
├── schemas/             # Pydantic input/output contracts
│   ├── __init__.py
│   ├── usuario.py       # UsuarioCreate, UsuarioResponse (no password exposed)
│   └── habito.py        # HabitoCreate, HabitoResponse, MarcaResponse
│
├── utils/               # Pure functions, no services/repos/routers imports
│   ├── __init__.py
│   └── crypto.py        # Hash/verify functions (wrapper around passlib)
│
└── mcp/                 # MCP server, tool definitions, auth adapter
    ├── __init__.py
    ├── server.py        # MCP server setup (streamable-http)
    ├── auth.py          # Extract JWT from Authorization header, call get_current_user
    └── tools.py         # Tool definitions (crear_habito, marcar_habito, listar_habitos, eliminar_habito)
                         # Each tool calls services/ directly

tests/
├── conftest.py          # pytest fixtures (in-memory DB, app overrides, test client)
├── unit/
│   ├── test_habitos_service.py      # Services logic with fake repositories
│   ├── test_usuarios_service.py
│   └── test_utils_crypto.py
├── integration/
│   ├── test_habitos_repository.py   # Real DB operations
│   └── test_usuarios_repository.py
└── api/
    ├── test_usuarios_endpoints.py   # app.dependency_overrides
    ├── test_habitos_endpoints.py
    └── test_mcp_tools.py

.env.example             # Template: SECRET_KEY, DATABASE_URL, ACCESS_TOKEN_EXPIRE_MINUTES
.env                     # IGNORED by .gitignore
migrations/              # Alembic version control
├── versions/
└── env.py
```

**Structure Decision**: Single monolithic FastAPI app (not split into microservices) with integrated MCP server. Layered architecture enforced by separate packages under `app/` with unidirectional dependencies. All tests colocated in `tests/` with subdirectories by test type (unit/integration/api). No cross-package imports except downward (routers → services → repositories, never reverse).

## Complexity Tracking

No violations of Constitution identified. All design decisions align with governance:
- Layered architecture naturally enforces separation
- DIP via parameter defaults requires no external container
- Single-library choices (pyjwt, passlib) simplify security auditing
- Testing pyramid structure supports coverage goals

---

## Phase 0: Research (Outline)

No NEEDS CLARIFICATION items identified in Technical Context. All technology choices pre-specified by coordinator:

**Research Tasks (consolidated in research.md)**:
1. ✓ pyjwt + passlib[bcrypt] integration for JWT + password hashing
2. ✓ pydantic_settings.BaseSettings for .env loading
3. ✓ SQLAlchemy sessionmaker + Alembic versioning strategy
4. ✓ pytest fixtures for in-memory SQLite in tests
5. ✓ app.dependency_overrides for FastAPI tests
6. ✓ MCP streamable-http integration (protocol, auth adapter design)
7. ✓ Fake repository pattern for unit testing (no unittest.mock)

**Output**: research.md (artifact, to be generated with decision + rationale for each)

---

## Phase 1: Design (Outline)

### Phase 1a: Data Model → data-model.md

**Entities** (from spec.md + Business Rules):
- **Usuario**: id (PK), email (unique), password_hash, created_at
  - Validation: email unique + non-empty, password_hash non-empty
  - Lifecycle: Created at registration, no updates in v1
  
- **Habito**: id (PK), usuario_id (FK → Usuario), nombre, frecuencia_objetivo, created_at
  - Validation: nome non-empty (1-255 chars), frecuencia_objetivo ∈ [1, 7]
  - Ownership: usuario_id immutable, all queries filtered by this
  - Lifecycle: Created, Listed, marked via Marca, Deleted
  
- **Marca**: id (PK), habito_id (FK → Habito), usuario_id (FK → Usuario), fecha, created_at
  - Validation: fecha ≤ today (FR-11a), no duplicates per (habito_id, fecha)
  - Lifecycle: Created (via marcar_habito), Queried (via listar_habitos with marks), Deleted (cascade on Habito delete)

**Output**: data-model.md (markdown with ERD diagram, field listing, constraints)

### Phase 1b: Interface Contracts → contracts/

**REST API** (contracts/REST_API.md):
```
POST   /usuarios/            → 201 (Usuario) | 400 (email duplicado) | 422 (validation)
POST   /usuarios/token       → 200 (JWT token) | 401 (credenciales inválidas)
POST   /habitos/             → 201 (Habito) | 400 (frecuencia) | 401 | 422
GET    /habitos/             → 200 (List[Habito] paginated) | 401 | 422 (skip/limit)
POST   /habitos/{id}/marcar  → 201 (Marca) | 400 (duplicate/future) | 401 | 404
DELETE /habitos/{id}         → 204 | 401 | 403 (not owner) | 404
```

**MCP Tools** (contracts/MCP_TOOLS.md):
```
crear_habito(nombre, frecuencia_objetivo)
  → {"id": ..., "nombre": ..., "frecuencia_objetivo": ...}
  | {"error": "..."}

marcar_habito(habito_id, fecha)
  → {"habito_id": ..., "fecha": ..., "created_at": ...}
  | {"error": "ya marcado ese día" | "fecha no puede ser posterior a la fecha actual"}

listar_habitos(skip=0, limit=20)
  → {"items": [...], "total": ...}

eliminar_habito(habito_id)
  → {prompt: "¿Confirmar eliminación de hábito X?"}
  → {"deleted": true} | {"error": "..."}
```

**Output**: contracts/REST_API.md, contracts/MCP_TOOLS.md (full endpoint/tool definitions, request/response schemas, error codes)

### Phase 1c: Validation Guide → quickstart.md

**Purpose**: Runnable scenarios proving end-to-end feature works.

**Scenarios**:
1. Register user (POST /usuarios/) → get email/password, verify 201
2. Login (POST /usuarios/token) → get JWT token, verify 200
3. Create habit (POST /habitos/ with JWT) → get Habito with id, verify 201
4. List habits (GET /habitos/ with JWT) → verify list contains created habit
5. Mark today (POST /habitos/{id}/marcar, no fecha param) → verify 201 with today
6. Mark yesterday (POST /habitos/{id}/marcar with fecha=yesterday) → verify 201 (retroactive OK)
7. Mark twice same day (POST /habitos/{id}/marcar twice, same fecha) → verify 400 "ya marcado"
8. Mark future (POST /habitos/{id}/marcar with fecha=tomorrow) → verify 400 "fecha no puede ser..."
9. Delete habit (DELETE /habitos/{id}) → verify 204, GET /habitos/ no longer contains it
10. Unauthorized access (GET /habitos/ without JWT) → verify 401

**Output**: quickstart.md (link to data model, contract details; runnable curl/python commands, expected responses)

---

## Next Steps

1. **Generate research.md** (Phase 0 complete)
2. **Generate data-model.md, contracts/, quickstart.md** (Phase 1 complete)
3. **Run /speckit-tasks** for task breakdown (Phase 2)
4. **Run /speckit-implement** for code generation + testing

---

**Constitution Alignment**: All 7 articles addressed in Technical Context gates. No violations. Design ready for implementation.
