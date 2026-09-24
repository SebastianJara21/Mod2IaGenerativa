# Implementation Plan: Sistema de Control de Gastos Personales

**Branch**: `001-control-de-gastos` | **Date**: 2026-09-23 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-control-de-gastos/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

A personal expense tracking system exposing REST API (registration, authentication, expense logging with category limits) and MCP tools for CLI/agent integration. Technical approach: FastAPI layered architecture (routers → services → repositories) with JWT authentication, SQLAlchemy ORM for multi-database support, and pytest for test pyramid validation (unit ≥90% coverage of services, ≥80% overall).

## Technical Context

**Language/Version**: Python 3.8+ (FastAPI requirement)

**Primary Dependencies**:
- **Web Framework**: FastAPI, uvicorn[standard]
- **ORM & Migrations**: SQLAlchemy, Alembic
- **Authentication**: pyjwt (JWT, HS256 signing)
- **Password Hashing**: passlib[bcrypt], bcrypt<4.1 (passlib 1.7.4 incompatible with newer bcrypt versions)
- **Configuration**: pydantic-settings (reads .env)
- **Validation**: pydantic (EmailStr requires email-validator), python-multipart (OAuth2PasswordRequestForm requires this)
- **MCP Integration**: mcp (official SDK, streamable-http transport)
- **Testing**: pytest, pytest-cov (coverage validation), httpx (TestClient for API tests)

**Storage**: SQLite (development), PostgreSQL (production) — single codebase via SQLAlchemy + Alembic migrations

**Testing**: pytest with fixtures for in-memory DB, app.dependency_overrides for API tests (httpx), pytest-cov for coverage reporting

**Target Platform**: Linux server (cloud-deployable)

**Project Type**: web-service (REST API + MCP tools in single FastAPI app)

**Performance Goals** (from spec Success Criteria):
- SC-002: Validation rejects invalid gastos in <500ms
- SC-003: Listing 10,000 gastos completes in <1 second

**Constraints**:
- SC-001: User registration + authentication cycle <30 seconds
- SC-004: 100% data isolation by user (zero cross-contamination)
- SC-008: Password never exposed in logs, responses, or error traces
- SC-009: Unhandled errors return 500 generic (no implementation details)

**Scale/Scope**: Single user at a time (personal finance app); authentication per-session. Compatibility locked with Sessions 6-8 function signatures (no parameter reordering, exception type names fixed).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Traceability to Constitution Articles

✓ **Artículo I — Arquitectura en capas**: Implemented as separate Python packages under `app/`:
  - `app/routers/` — receive HTTP, delegate to services, translate responses (no business logic)
  - `app/services/` — all business logic (category validation, limit checking, user isolation)
  - `app/repositories/` — database operations only (CRUD, totals, no logic)
  - `app/utils/` — pure functions (no dependencies on services/routers/repositories)
  - `app/mcp/tools/` — tools call services, never reimplement logic
  - No cross-layer imports that violate dependency direction

✓ **Artículo II — SOLID (DIP focus)**: Services receive repositories as parameters with defaults:
  - `registrar_gasto(db, usuario_id, descripcion, monto, categoria, repo=gastos_repository)`
  - `listar_gastos(db, usuario_id, skip=0, limit=20, repo=gastos_repository)`
  - No external DI container; plain parameter defaults maintain simplicity
  - Tests inject fake repositories without mocking

✓ **Artículo III — Persistencia**: SQLAlchemy + Alembic
  - Single codebase (services/routers unchanged between SQLite dev and Postgres prod)
  - All database code in repositories; no raw SQL concatenation
  - Alembic for schema versioning and migration
  - Every user-data query includes usuario_id filter (no cross-user leaks)

✓ **Artículo IV — Seguridad (non-negotiable)**:
  - Passwords: passlib.context.CryptContext(schemes=["bcrypt"]) with bcrypt<4.1
  - Auth: pyjwt for JWT signing (HS256), single library choice (not "or python-jose")
  - Configuration: pydantic_settings.BaseSettings reads .env for SECRET_KEY, DATABASE_URL
  - Authorization: usuario_id ALWAYS from JWT via get_current_user, NEVER from URL/body/query params
  - Errors: unhandled exceptions → 500 generic (no stack traces); details logged internally
  - Validation: Pydantic schemas validate all user input before services

✓ **Artículo V — Diseño de endpoints REST**: Standard HTTP verbs/codes
  - POST /usuarios/ → 201 (create user)
  - POST /usuarios/token → 200 (JWT token)
  - POST /gastos/ → 201 (create expense)
  - GET /gastos/ → 200 (list expenses with skip/limit pagination)
  - 400: business rule violations (invalid category, limit exceeded)
  - 401: missing/invalid token
  - 422: schema validation errors
  - Separate input/output schemas (GastoCreate vs GastoOut)

✓ **Artículo VI — MCP: tools y reutilización**:
  - Tools: `registrar_gasto`, `listar_gastos` call service functions (no reimplementation)
  - MCP mounted in same FastAPI app (streamable-http transport)
  - get_current_user adapted to extract JWT from MCP Authorization header
  - Errors: structured {"error": "..."} never uncontrolled exceptions
  - User identity: from JWT token (streamable-http); fallback to .env demo user (stdio only, documented)
  - Destructive ops: DELETE requires explicit confirmation (future feature, not in scope)

✓ **Artículo VII — Testing y cobertura (mandatory)**:
  - Pyramid: units (services with fake repos) > integration (in-memory DB) > API/E2E (minimal)
  - Services tests inject RepositorioFalso (no unittest.mock)
  - API tests use app.dependency_overrides for get_db, get_gastos_repo, get_current_user
  - Coverage: services ≥90%, overall ≥80% (pytest --cov=app measured at end of /speckit-implement)
  - In-memory SQLite for integration tests
  - 100% of explicit business rules covered (5 error cases + 4 categories + limit validation)
  - All MCP tools tested (happy path + business error)
  - Omitted from coverage (per .pyproject.toml [tool.coverage.run] omit): main.py, mcp/server.py, mcp/auth.py, logging_config.py (infrastructure)

✓ **Artículo VIII — Compatibilidad con proyecto de referencia**:
  - Function signatures IMMUTABLE (locked to Sessions 6-8 test imports):
    - `app/services/gastos.py`: CategoriaInvalidaError, LimiteExcedidoError, LIMITE_POR_CATEGORIA=500.0, registrar_gasto(..., repo=gastos_repository), listar_gastos(..., repo=gastos_repository)
    - `app/repositories/gastos.py`: functions (not class), guardar/listar/total_por_categoria return dicts (not ORM objects)
    - `app/repositories/usuarios.py`: obtener_por_email, guardar functions
    - Dependencies: app.database.get_db, app.dependencies.get_current_user, app.dependencies.get_gastos_repo, app.models.usuario.Usuario
    - `tests/__init__.py` exports RepositorioFalso from tests.test_gastos
  - Tests copied from Sessions 6-8 without assertion modifications (contract enforcement)

**Gate Status**: PASS — All constitution articles traceable to implementation approach. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
app/
├── __init__.py
├── main.py                      # FastAPI app entry, lifespan, middleware
├── database.py                  # SQLAlchemy engine, session factory, get_db
├── dependencies.py              # get_current_user, get_gastos_repo (DIP injection)
├── models/
│   ├── __init__.py
│   ├── usuario.py              # Usuario ORM model
│   └── gasto.py                # Gasto ORM model
├── schemas/
│   ├── __init__.py
│   ├── usuario.py              # UsuarioCreate, UsuarioOut Pydantic schemas
│   └── gasto.py                # GastoCreate, GastoOut Pydantic schemas
├── routers/
│   ├── __init__.py
│   ├── usuarios.py             # POST /usuarios/, POST /usuarios/token
│   └── gastos.py               # POST /gastos/, GET /gastos/
├── services/
│   ├── __init__.py
│   ├── gastos.py               # registrar_gasto, listar_gastos (business logic)
│   └── usuarios.py             # register_usuario, authenticate_usuario
├── repositories/
│   ├── __init__.py
│   ├── gastos.py               # guardar, listar, total_por_categoria (DB-only)
│   └── usuarios.py             # obtener_por_email, guardar (DB-only)
├── utils/
│   ├── __init__.py
│   ├── security.py             # hash_password, verify_password, create_access_token
│   └── validators.py           # Pure validation functions
├── mcp/
│   ├── __init__.py
│   ├── server.py               # MCP server setup (not in coverage omit)
│   ├── auth.py                 # MCP auth (not in coverage omit)
│   └── tools/
│       ├── __init__.py
│       ├── gastos.py           # registrar_gasto, listar_gastos tools
│       └── usuarios.py         # (future tools)
├── exceptions/
│   ├── __init__.py
│   └── gastos.py               # CategoriaInvalidaError, LimiteExcedidoError
└── logging_config.py           # Logging setup (not in coverage omit)

tests/
├── __init__.py                 # Exports RepositorioFalso for import compatibility
├── conftest.py                 # pytest fixtures (in-memory DB, test client, mocks)
├── unit/
│   ├── test_services_gastos.py            # 100% coverage of registrar_gasto, listar_gastos
│   ├── test_services_usuarios.py          # 100% coverage of auth logic
│   ├── test_repositories_gastos.py        # Repository query logic
│   └── test_utils_security.py             # Pure function tests
├── integration/
│   ├── test_gastos_integracion.py         # End-to-end with real (in-memory) DB
│   └── test_usuarios_integracion.py
├── api/
│   ├── test_api_gastos.py                 # Copied from Sessions 6-8 (no modifications)
│   ├── test_api_usuarios.py
│   └── test_mcp_tools.py                  # MCP tool behavior validation
└── test_gastos.py              # RepositorioFalso definition (imported by conftest, api tests)

pyproject.toml                  # pytest config + [tool.coverage.run] omit for main.py, mcp/server.py, etc.
.env.example                    # SECRET_KEY, DATABASE_URL, ACCESS_TOKEN_EXPIRE_MINUTES templates
.env                            # (git-ignored) actual values for development
alembic/
├── versions/
└── env.py                      # Auto-generated by Alembic
```

**Structure Decision**: Single FastAPI web service with strict layering (routers → services → repositories). No external DI container; dependency injection via function parameter defaults (DIP). Alembic migrations manage schema versioning. Tests import and test each layer independently (unit), together (integration), and via HTTP (API/E2E).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
