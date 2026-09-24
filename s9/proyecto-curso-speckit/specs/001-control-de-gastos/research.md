# Research & Technical Decisions: Sistema de Control de Gastos

**Date**: 2026-09-23  
**Phase**: Phase 0 — Outline & Research

---

## Executive Summary

All critical technical decisions are locked by the Specification and Constitution. No NEEDS CLARIFICATION items remain. This research consolidates technology rationales and best practices decisions aligned with the Constitution.

---

## Technology Stack Rationales

### 1. Web Framework: FastAPI + uvicorn[standard]

**Decision**: FastAPI (async Python web framework) + uvicorn[standard] (ASGI server)

**Rationale**:
- Native async/await support for concurrent request handling
- Automatic OpenAPI documentation (Swagger)
- Built-in dependency injection hooks (dependency_overrides for testing)
- Pydantic integration for request/response validation
- MCP SDK compatibility (streamable-http transport)

**Alternatives Considered**:
- Django REST: Synchronous, heavier; overkill for this scope
- Flask: Minimal built-ins; requires more boilerplate for modern features
- FastAPI chosen: Best fit for REST API + async MCP integration

---

### 2. Authentication: pyjwt (not python-jose)

**Decision**: pyjwt for JWT signing and verification (HS256 algorithm)

**Rationale**:
- Single library choice eliminates ambiguity (Constitution Artículo IV.2)
- pyjwt is actively maintained; python-jose is unmaintained
- Simple API: `jwt.encode()`, `jwt.decode()`
- Integrates with FastAPI's dependency injection

**Alternatives Considered**:
- python-jose: Unmaintained, higher risk
- python-jwt: Fewer features
- pyjwt chosen: Active maintenance, simplicity, stability

---

### 3. Password Hashing: passlib[bcrypt] (bcrypt<4.1)

**Decision**: `passlib.context.CryptContext(schemes=["bcrypt"])` with bcrypt<4.1

**Rationale**:
- passlib abstracts bcrypt complexity (automatic salt generation, cost factor tuning)
- bcrypt<4.1: passlib 1.7.4 has runtime breaks with bcrypt ≥4.1 due to API changes
- Industry standard for password storage (irreversible, salted)
- Supports future migration to argon2 (by adding scheme to context)

**Constraints**:
- bcrypt version pinned to <4.1 (Constitution specifies exact version compatibility)

**Alternatives Considered**:
- Argon2: More modern, heavier; bcrypt sufficient for this scale
- scrypt: Similar considerations; bcrypt is conservative choice
- passlib[bcrypt] with bcrypt<4.1 chosen: Proven, stable, explicit version management

---

### 4. ORM & Migrations: SQLAlchemy + Alembic

**Decision**: SQLAlchemy ORM for database abstraction, Alembic for schema versioning

**Rationale**:
- Single codebase works with SQLite (dev) and PostgreSQL (prod) without changes
- Alembic tracks schema versions; reversible migrations (up/down)
- No raw SQL concatenation; parameterized queries prevent SQL injection
- SQLAlchemy relationship modeling simplifies user-gasto foreign key handling

**Implementation**:
- SQLite in-memory for unit/integration tests
- SQLite file-based for development (`.env` DATABASE_URL)
- Postgres for production (`.env` DATABASE_URL switch)
- `connect_args={"check_same_thread": False}` for SQLite in tests only

**Alternatives Considered**:
- Django ORM: Tightly coupled to Django; overkill here
- Manual SQL + driver (psycopg2): More verbose; prone to SQL injection
- SQLAlchemy + Alembic chosen: Decoupling, portability, safety

---

### 5. Configuration: pydantic-settings (reads .env)

**Decision**: `pydantic_settings.BaseSettings` for configuration from `.env` file

**Rationale**:
- Type-safe environment variable binding (e.g., `SECRET_KEY: str`, `DATABASE_URL: str`)
- Automatic validation at app startup (fails fast if missing/invalid)
- Separates secrets from code (`.env` git-ignored)
- `.env.example` documents required variables without values

**Variables Managed**:
- `SECRET_KEY`: Cryptographic key for JWT signing (generated with `openssl rand -hex 32`)
- `DATABASE_URL`: SQLite or PostgreSQL connection string
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT expiry (configurable, never infinite)

**Alternatives Considered**:
- python-dotenv: Simpler but no validation; we prefer type safety
- Environment variables only: Harder to document and share templates
- pydantic-settings chosen: Validation + documentation + standard practice

---

### 6. Validation: Pydantic (EmailStr, OAuthRequestForm)

**Decision**: Pydantic models for request/response schemas; EmailStr for email validation

**Rationale**:
- Declarative schema definitions (GastoCreate vs GastoOut)
- Automatic HTTP 422 errors on invalid input
- EmailStr validates RFC 5321 format (requires email-validator dependency)
- python-multipart required for OAuth2PasswordRequestForm (form-encoded body parsing)

**Dependencies**:
- email-validator: Transitive (required by EmailStr)
- python-multipart: Transitive (required by OAuth2PasswordRequestForm)
- Both included in primary dependencies (cannot be omitted without breaking app startup)

**Alternatives Considered**:
- Manual validation in services: Verbose, error-prone; violates separation of concerns
- Marshmallow: Heavier, overlaps with Pydantic; redundant
- Pydantic chosen: FastAPI integration, minimal code, clear contracts

---

### 7. MCP Integration: Official SDK (streamable-http)

**Decision**: mcp (official Python SDK from Anthropic) with streamable-http transport

**Rationale**:
- Official maintenance; compatible with Claude AI agent ecosystem
- streamable-http transport allows HTTP-based authentication (JWT header propagation)
- Single FastAPI app hosts both REST API and MCP server
- Tools (`registrar_gasto`, `listar_gastos`) call services (no logic duplication)

**Architecture**:
- MCP server mounted in FastAPI app lifespan
- Tools extract JWT from `Authorization` header
- get_current_user adapted for MCP context (verifies JWT before tool execution)
- User identity resolved from token (streamable-http); fallback to .env demo user (stdio only)

**Alternatives Considered**:
- stdio transport: Simpler but no auth propagation; requires hardcoded demo user (documented compromise)
- Custom tool integration: Reinvents MCP; choose official SDK instead
- streamable-http chosen: Auth-capable, official, app-integrated

---

### 8. Testing Stack: pytest + pytest-cov + httpx

**Decision**: pytest for test framework, pytest-cov for coverage, httpx for async HTTP client

**Rationale**:
- pytest: Industry standard, fixtures for dependency injection, plugin ecosystem
- pytest-cov: Integrates coverage measurement; enforces thresholds (Constitution Article VII)
- httpx: Modern async HTTP client compatible with FastAPI's TestClient
- Fixtures for in-memory SQLite DB (no external dependencies during testing)
- app.dependency_overrides replaces real services/repos with fakes during API tests

**Test Pyramid**:
- **Unit** (majority): services with RepositorioFalso (no mocking; DIP via parameter injection)
- **Integration** (moderate): real in-memory DB, full request/response cycle
- **API/E2E** (minimal): HTTP client tests of endpoints

**Coverage Thresholds** (Constitution Article VII.3):
- Services: ≥90% line coverage
- Overall (services + repos + routers + utils): ≥80%
- Excluded: main.py, mcp/server.py, mcp/auth.py, logging_config.py (infrastructure omitted from coverage.run)

**Alternatives Considered**:
- unittest.mock for service tests: Violates DIP; cannot test without mocking
- unittest: Less ergonomic; pytest fixtures superior
- Coverage.py thresholds: Enforced at end of /speckit-implement (not optional)
- pytest + pytest-cov + httpx chosen: Simplicity, DIP-compatible, modern async support

---

## Compatibility Lock: Sessions 6-8 Test Contracts

**Immutable Exports** (test imports must not change):

```python
from app.services.gastos import registrar_gasto, listar_gastos, CategoriaInvalidaError, LimiteExcedidoError, LIMITE_POR_CATEGORIA
from app.repositories.gastos import guardar, listar, total_por_categoria
from app.repositories.usuarios import obtener_por_email, guardar as guardar_usuario
from app.database import get_db
from app.dependencies import get_current_user, get_gastos_repo
from app.models.usuario import Usuario
from tests import RepositorioFalso  # exported from tests.test_gastos
```

**Function Signatures** (exact parameter order, defaults):
- `registrar_gasto(db, usuario_id, descripcion, monto, categoria, repo=gastos_repository) -> dict`
- `listar_gastos(db, usuario_id, skip=0, limit=20, repo=gastos_repository) -> list[dict]`
- `guardar(db, usuario_id, descripcion, monto, categoria) -> dict`
- `listar(db, usuario_id, skip=0, limit=20) -> list[dict]`
- `total_por_categoria(db, usuario_id, categoria) -> float`

**Exception Types** (exact names, not aliased):
- `CategoriaInvalidaError` (raised when category not in ["comida", "transporte", "entretenimiento", "otros"])
- `LimiteExcedidoError` (raised when total_por_categoria + new_monto > 500)

**Constant**:
- `LIMITE_POR_CATEGORIA = 500.0`

---

## No Rework Needed

All decisions above are **direct implementations of Constitutional requirements** (Artículos I-VIII). No ambiguities remain. Proceed to Phase 1 design (data-model.md, contracts/, quickstart.md).
