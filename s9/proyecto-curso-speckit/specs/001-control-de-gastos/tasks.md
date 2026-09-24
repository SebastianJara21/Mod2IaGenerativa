# Tasks: Sistema de Control de Gastos Personales

**Input**: Design documents from `/specs/001-control-de-gastos/`

**Prerequisites**: plan.md (tech stack), spec.md (user stories), data-model.md (entities), quickstart.md (validation)

**Testing**: ALL code tasks have paired tests (unit + integration). Tests are MANDATORY per Artículo VII (Constitution).

**Test Files**: Copied from Sessions 6-8 (exact names, no subdirectories):
- `tests/test_gastos.py` — Unit tests for gastos service + RepositorioFalso definition
- `tests/test_integracion_gastos.py` — Integration tests for gastos with real DB
- `tests/test_api_gastos.py` — API contract tests (copied, unmodified)

**Organization**: Tasks grouped by user story (P1, P2) to enable independent implementation and testing.

---

## Format: `- [ ] [ID] [P?] [Story?] Description with file path`

- **[ID]**: Task identifier (T001, T002, ...)
- **[P]**: Parallelizable (different files, no inter-task dependencies)
- **[Story]**: User story label ([US1], [US2], ...) for story-specific tasks
- **File paths**: Relative to repo root (`app/`, `tests/`, `alembic/`)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency management

- [ ] T001 Create project directory structure: `app/`, `app/routers/`, `app/services/`, `app/repositories/`, `app/models/`, `app/schemas/`, `app/utils/`, `app/mcp/`, `app/exceptions/`, `tests/`, `alembic/`
- [ ] T002 Initialize Python project with requirements.txt (FastAPI, uvicorn, SQLAlchemy, Alembic, pyjwt, passlib[bcrypt], bcrypt<4.1, pydantic-settings, email-validator, python-multipart, mcp, pytest, pytest-cov, httpx)
- [ ] T003 [P] Create `.env.example` with template variables (SECRET_KEY, DATABASE_URL, ACCESS_TOKEN_EXPIRE_MINUTES)
- [ ] T004 [P] Initialize Alembic for database migrations: `alembic init alembic` (if not already done)
- [ ] T005 Create `app/__init__.py` (package marker, empty or minimal)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure MUST complete before user story implementation begins

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create app/database.py: SQLAlchemy engine setup (SQLite for dev, Postgres prod switchable via .env DATABASE_URL), Session factory, get_db dependency
- [ ] T007 Create app/config.py (or use pydantic_settings): Load SECRET_KEY, DATABASE_URL, ACCESS_TOKEN_EXPIRE_MINUTES from .env
- [ ] T008 Create app/exceptions/gastos.py: Define CategoriaInvalidaError, LimiteExcedidoError (exactly as per Compatibility Contract, Artículo VIII)
- [ ] T009 Create app/utils/security.py: Implement hash_password (passlib.context.CryptContext with bcrypt), verify_password, create_access_token (pyjwt, HS256)
- [ ] T010 Create app/dependencies.py: Implement get_db, get_current_user (extract usuario_id from JWT), get_gastos_repo (DIP injection pattern per Artículo II.3)
- [ ] T011 Create app/logging_config.py: Configure logging (errors logged internally, never exposed to client per Artículo IV.5)
- [ ] T012 Create app/main.py: FastAPI app initialization, lifespan management, middleware setup, mount routers (will be added in later tasks), mount MCP server
- [ ] T013 [P] Create alembic/env.py revision: Configure Alembic to use SQLAlchemy models from app/models/ for automatic migration generation

**Checkpoint**: Foundation ready - user story implementation can now proceed

---

## Phase 3: User Story 1 - Registro de Usuario (Priority: P1) 🎯 MVP

**Goal**: Users can register with email and password; account created with hashed password

**Independent Test**: User registration returns 201 with user data (no password); duplicate email returns 400; invalid email returns 422

### Tests for User Story 1

- [ ] T014 [P] [US1] Create unit test file `tests/test_usuarios.py`: Test registrar_usuario service function (valid registration, duplicate email error, password hashing verification)
- [ ] T015 [P] [US1] Create integration test in `tests/test_integracion_usuarios.py`: Test usuario creation with real (in-memory) SQLite DB, verify DB state
- [ ] T016 [P] [US1] Create API test in `tests/test_api_usuarios_registro.py`: Test POST /usuarios/ endpoint (201 success, 400 duplicate, 422 validation)

### Implementation for User Story 1

- [ ] T017 [P] [US1] Create app/models/usuario.py: Define Usuario ORM model (fields: id INTEGER PK, email VARCHAR(255) UNIQUE NOT NULL, hashed_password VARCHAR(255) NOT NULL, created_at DATETIME DEFAULT now(), updated_at DATETIME)
- [ ] T018 [P] [US1] Create app/schemas/usuario.py: Define UsuarioCreate (email EmailStr, password str), UsuarioOut (id, email, created_at — NO hashed_password)
- [ ] T019 [US1] Create app/repositories/usuarios.py: Implement guardar(db, email, hashed_password) -> dict (returns {id, email, created_at}), obtener_por_email(db, email) -> Usuario | None
- [ ] T020 [US1] Create app/services/usuarios.py: Implement registrar_usuario(db, email, password, repo=usuarios_repo) -> dict (validates email uniqueness via repo, hashes password with security.hash_password, calls repo.guardar, returns user dict without password)
- [ ] T021 [US1] Create app/routers/usuarios.py: Implement POST /usuarios/ endpoint (accepts UsuarioCreate, calls service.registrar_usuario, returns UsuarioOut with 201, catches duplicate email error → 400, validation errors → 422)
- [ ] T022 [US1] Run tests for User Story 1: Ensure all tests pass (T014, T015, T016)

**Checkpoint**: User registration fully functional and independently testable

---

## Phase 4: User Story 2 - Autenticación y Obtención de Token (Priority: P1)

**Goal**: Users can authenticate with email/password to get JWT access token for protected operations

**Independent Test**: Valid credentials return 200 with JWT; invalid credentials return 401; missing credentials return 422

### Tests for User Story 2

- [ ] T023 [P] [US2] Create unit test in `tests/test_usuarios.py`: Add test_authenticate_usuario (valid creds, invalid password, user not found)
- [ ] T024 [P] [US2] Create integration test in `tests/test_integracion_usuarios.py`: Add test for authentication flow with real DB (register user, then authenticate)
- [ ] T025 [P] [US2] Create API test in `tests/test_api_usuarios_token.py`: Test POST /usuarios/token endpoint (200 with JWT, 401 invalid, 422 missing fields)

### Implementation for User Story 2

- [ ] T026 [P] [US2] Create app/schemas/token.py: Define TokenResponse (access_token str, token_type str = "bearer"), TokenData (usuario_id int, exp datetime)
- [ ] T027 [US2] Update app/services/usuarios.py: Add authenticate_usuario(db, email, password, repo=usuarios_repo) -> dict (validates user exists via repo.obtener_por_email, verifies password via security.verify_password, calls security.create_access_token with usuario_id, returns token dict)
- [ ] T028 [US2] Update app/routers/usuarios.py: Add POST /usuarios/token endpoint (accepts OAuth2PasswordRequestForm username/password, calls service.authenticate_usuario, returns TokenResponse 200, catches auth errors → 401, validation → 422)
- [ ] T029 [US2] Update app/dependencies.py: Enhance get_current_user to decode JWT, extract usuario_id, verify expiry; raise 401 if token invalid/missing
- [ ] T030 [US2] Run tests for User Story 2: Ensure all tests pass (T023, T024, T025)

**Checkpoint**: User authentication fully functional; protected endpoints can now check get_current_user

---

## Phase 5: User Story 3 - Registrar Gasto (Priority: P1)

**Goal**: Authenticated users can create expenses with description, amount, and valid category; system validates amount > 0, category in enum, and cumulative limit ≤ 500 per category

**Independent Test**: Valid gasto returns 201; invalid category returns 400; monto ≤ 0 returns 422; limit exceeded returns 400; no auth returns 401

### Tests for User Story 3

- [ ] T031 [P] [US3] Copy tests from Sessions 6-8 reference: Import `tests/test_gastos.py` (unit tests for registrar_gasto, listar_gastos, RepositorioFalso definition)
- [ ] T032 [P] [US3] Copy tests: Import `tests/test_integracion_gastos.py` (integration tests with real DB)
- [ ] T033 [P] [US3] Create unit test in `tests/test_gastos.py`: Add test_registrar_gasto_categoria_invalida (invalid category → CategoriaInvalidaError), test_registrar_gasto_monto_invalido (monto ≤ 0 → ValidationError or service validation), test_registrar_gasto_limite_excedido (total > 500 → LimiteExcedidoError)
- [ ] T034 [P] [US3] Create API test in `tests/test_api_gastos.py`: Add test_post_gastos_success (201), test_post_gastos_categoria_invalida (400), test_post_gastos_limite_excedido (400), test_post_gastos_sin_auth (401), test_post_gastos_monto_invalido (422)

### Implementation for User Story 3

- [ ] T035 [P] [US3] Create app/models/gasto.py: Define Gasto ORM model (fields: id INTEGER PK, usuario_id INTEGER FK, descripcion VARCHAR(255) NOT NULL, monto NUMERIC(10,2) NOT NULL CHECK(monto > 0), categoria VARCHAR(50) NOT NULL CHECK(categoria IN ('comida', 'transporte', 'entretenimiento', 'otros')), created_at DATETIME, updated_at DATETIME)
- [ ] T036 [P] [US3] Create app/schemas/gasto.py: Define GastoCreate (descripcion str min_length=1, monto Decimal gt=0, categoria CategoriaEnum), GastoOut (id, usuario_id, descripcion, monto, categoria, created_at)
- [ ] T037 [P] [US3] Define app/models/gasto.py: CategoriaEnum = ["comida", "transporte", "entretenimiento", "otros"] (exact values per spec)
- [ ] T038 [US3] Create app/repositories/gastos.py: Implement guardar(db, usuario_id, descripcion, monto, categoria) -> dict (creates Gasto, returns dict), listar(db, usuario_id, skip=0, limit=20) -> list[dict], total_por_categoria(db, usuario_id, categoria) -> float (sum of all gastos for user in category, cumulative/never reset per Artículo VIII)
- [ ] T039 [US3] Create app/services/gastos.py: Implement registrar_gasto(db, usuario_id, descripcion, monto, categoria, repo=gastos_repository) -> dict (validates categoria in enum → raise CategoriaInvalidaError if not, checks total_por_categoria + monto > 500 → raise LimiteExcedidoError, calls repo.guardar, returns gasto dict). Also: listar_gastos(db, usuario_id, skip=0, limit=20, repo=gastos_repository) -> list[dict]
- [ ] T040 [US3] Create app/routers/gastos.py: Implement POST /gastos/ endpoint (requires get_current_user, accepts GastoCreate, calls service.registrar_gasto with current user_id, returns GastoOut 201; catches CategoriaInvalidaError → 400 "categoría inválida", LimiteExcedidoError → 400 "límite excedido", validation errors → 422, auth errors → 401)
- [ ] T041 [US3] Update app/main.py: Import and mount routers.gastos.router at /gastos
- [ ] T042 [US3] Create Alembic migration: `alembic revision --autogenerate -m "Add gasto table"` (generates migration for Gasto model, creates gastos table with all fields and constraints)
- [ ] T043 [US3] Run tests for User Story 3: Ensure all tests pass (T031-T034)

**Checkpoint**: Gasto creation fully functional with category and limit validation

---

## Phase 6: User Story 4 - Listar Gastos Propios (Priority: P1)

**Goal**: Authenticated users can list their gastos with pagination (skip, limit); user isolation enforced (no cross-user leaks)

**Independent Test**: Valid request returns 200 list; pagination works (skip/limit); cross-user access attempt returns only authenticated user's gastos; invalid skip/limit returns 422; no auth returns 401

### Tests for User Story 4

- [ ] T044 [P] [US4] Create unit test in `tests/test_gastos.py`: Add test_listar_gastos_paginacion (skip=0 limit=20 works), test_listar_gastos_empty (no gastos returns empty list), test_listar_gastos_usuario_isolation (only returns authenticated user's gastos)
- [ ] T045 [P] [US4] Create integration test in `tests/test_integracion_gastos.py`: Add test for listar_gastos with real DB, verify pagination, user isolation
- [ ] T046 [P] [US4] Create API test in `tests/test_api_gastos.py`: Add test_get_gastos_success (200 list), test_get_gastos_pagination (skip/limit work), test_get_gastos_usuario_isolation (user A doesn't see user B's gastos), test_get_gastos_sin_auth (401), test_get_gastos_invalid_skip (422), test_get_gastos_invalid_limit (422)

### Implementation for User Story 4

- [ ] T047 [US4] Update app/routers/gastos.py: Implement GET /gastos/ endpoint (requires get_current_user, accepts query params skip=0 limit=20, validates skip ≥ 0 and limit > 0 → 422 if invalid, calls service.listar_gastos with current user_id, returns list[GastoOut] 200; auth errors → 401)
- [ ] T048 [US4] Ensure app/services/gastos.py listar_gastos filters ONLY by usuario_id from JWT (never from request params) — user isolation is non-negotiable per Artículo IV.4
- [ ] T049 [US4] Run tests for User Story 4: Ensure all tests pass (T044, T045, T046); verify user isolation holds

**Checkpoint**: Gasto listing fully functional with pagination and user isolation

---

## Phase 7: User Story 5 - Tool MCP: Registrar Gasto (Priority: P2)

**Goal**: CLI/agent clients can use MCP tool `registrar_gasto` to create gastos; tool calls service (no logic duplication per Artículo VI)

**Independent Test**: Tool with valid args returns gasto; invalid category returns error structure; limit exceeded returns error; unauth returns error

### Tests for User Story 5

- [ ] T050 [P] [US5] Create MCP tool test in `tests/test_mcp_gastos.py`: Test registrar_gasto tool (valid call, invalid category error, limit exceeded error, auth handling)

### Implementation for User Story 5

- [ ] T051 [P] [US5] Create app/mcp/tools/gastos.py: Define registrar_gasto(descripcion, monto, categoria) tool that calls app/services/gastos.registrar_gasto (extracts usuario_id from MCP auth context via JWT header), returns gasto dict or error struct {"error": "..."}
- [ ] T052 [US5] Update app/main.py: Mount MCP server in FastAPI lifespan, register registrar_gasto tool
- [ ] T053 [US5] Implement MCP auth adaptation: Extract JWT from Authorization header in MCP context, pass to get_current_user-equivalent for MCP
- [ ] T054 [US5] Run tests for User Story 5: Ensure all tests pass (T050)

**Checkpoint**: MCP registrar_gasto tool fully functional

---

## Phase 8: User Story 6 - Tool MCP: Listar Gastos (Priority: P2)

**Goal**: CLI/agent clients can use MCP tool `listar_gastos` to list their gastos; tool calls service

**Independent Test**: Tool with skip/limit returns list; pagination works; only returns user's gastos

### Tests for User Story 6

- [ ] T055 [P] [US6] Create MCP tool test in `tests/test_mcp_gastos.py`: Add test_listar_gastos_tool (valid call, pagination, user isolation)

### Implementation for User Story 6

- [ ] T056 [P] [US6] Update app/mcp/tools/gastos.py: Define listar_gastos(skip=0, limit=20) tool that calls app/services/gastos.listar_gastos (extracts usuario_id from MCP auth context), returns list[dict] or error
- [ ] T057 [US6] Update app/main.py: Register listar_gastos tool in MCP server
- [ ] T058 [US6] Run tests for User Story 6: Ensure all tests pass (T055)

**Checkpoint**: Both MCP tools fully functional

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements across all stories, final validation, coverage verification

- [ ] T059 [P] Run integration test suite: `pytest tests/test_integracion_gastos.py -v` (all integration tests pass)
- [ ] T060 [P] Run API test suite: `pytest tests/test_api_gastos.py tests/test_api_usuarios_*.py -v` (all API tests pass)
- [ ] T061 [P] Run MCP tool tests: `pytest tests/test_mcp_gastos.py -v` (all MCP tests pass)
- [ ] T062 Validate quickstart.md scenarios: Run all 6 validation scenarios from quickstart.md manually; confirm each endpoint/tool behaves as documented
- [ ] T063 Documentation: Update README with quickstart (registration, auth, expense creation, listing)
- [ ] T064 **CRITICAL - Coverage Validation (Artículo VII.3)**: Run `pytest --cov=app --cov-report=term-missing tests/` and verify: (1) services/ coverage ≥90%, (2) overall (app/) coverage ≥80%, (3) omitted files from coverage (main.py, mcp/server.py, mcp/auth.py, logging_config.py) per .pyproject.toml [tool.coverage.run] omit. If thresholds not met, add tests until met.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2 - Can start once foundational ready
- **Phase 4 (US2)**: Depends on Phase 2, builds on US1 (auth required)
- **Phase 5 (US3)**: Depends on Phase 2, builds on US1/US2 (creates gastos for authenticated users)
- **Phase 6 (US4)**: Depends on Phase 5 (lists gastos)
- **Phase 7 (US5)**: Depends on Phase 2, US3 (MCP version of registrar_gasto)
- **Phase 8 (US6)**: Depends on Phase 2, US4 (MCP version of listar_gastos)
- **Phase 9 (Polish)**: Depends on Phases 3-8 (all stories must be implemented)

### User Story Dependencies

- **US1 (Register)**: Independent after Phase 2
- **US2 (Auth)**: Depends on US1 (users must exist to authenticate)
- **US3 (Create Gasto)**: Depends on US1, US2 (need users and auth to create gastos)
- **US4 (List Gasto)**: Depends on US3 (need gastos to list)
- **US5 (MCP Register)**: Depends on US3 (calls same service)
- **US6 (MCP List)**: Depends on US4 (calls same service)

### Within Each Phase

- Tests written FIRST (red), then implementation (green)
- Models before services
- Services before routers
- Unit tests before integration tests
- Integration tests before API tests

### Parallel Opportunities

- **Phase 1**: All [P] tasks can run in parallel (T001-T005)
- **Phase 2**: All [P] tasks can run in parallel (T006-T013)
- **Phase 3**: T014-T016 (tests) can run in parallel; T017-T018 (models/schemas) can run in parallel; then T019-T021 (sequential: repo → service → router)
- **Phase 4**: Similar parallel structure (tests, then models, then service, then router)
- **Phase 5-6**: Similar; once Phase 2 and Phase 3 done, Phase 5 and Phase 7 can overlap (same code path)
- **Phase 7-8**: MCP tools can be implemented in parallel (different files)

---

## Implementation Strategy

### MVP First (Phases 1-6: US1-US4)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1 (Registration)
4. Complete Phase 4: User Story 2 (Authentication)
5. Complete Phase 5: User Story 3 (Create Gasto)
6. Complete Phase 6: User Story 4 (List Gasto)
7. **STOP and VALIDATE**: Run T062, T064 (coverage ≥80%)
8. Deploy MVP (REST API fully functional)

### Incremental Delivery

1. MVP (Phases 1-6): REST API complete
2. Add Phases 7-8: MCP tools
3. Add Phase 9: Polish & final validation
4. Deploy final version

### Parallel Team Strategy

With multiple developers:

1. Pair: Complete Phases 1-2 together (foundation)
2. Once Phase 2 done:
   - Developer A: Phase 3 (US1 Registration)
   - Developer B: Phase 4 (US2 Authentication)
   - Developer C: Phase 5 (US3 Create Gasto)
3. Then:
   - Developer A: Phase 6 (US4 List Gasto)
   - Developer B: Phase 7 (US5 MCP Register)
   - Developer C: Phase 8 (US6 MCP List)
4. All: Phase 9 (polish, validation, coverage)

---

## Definition of Done

### For Each Code Task

1. **Code Written**: Implementation complete, follows Constitution articles (architecture, SOLID, security)
2. **Test Written & Green**: Paired test(s) written, passing, covers happy path and error cases
3. **No Constitution Violations**: Code adheres to Articles I-VIII (layers, DIP, persistence, security, REST, MCP, testing, compatibility)

### For Each Phase

- All tasks in phase complete
- All tests passing
- Coverage thresholds met (if applicable)
- No regressions in prior phases

### For Complete Feature

- Phase 9 complete
- `pytest --cov=app --cov-report=term-missing` ≥80% overall, ≥90% services
- All quickstart.md scenarios validated
- No Constitution violations
- Ready for `/speckit-implement`

---

## Notes

- [P] tasks = different files, can parallelize
- [Story] label = maps task to user story for traceability
- Each user story independently testable and deployable
- Tests MUST be written before or alongside implementation (TDD/BDD)
- Commitment: Every code task has a paired test
- Coverage validation (T064) is mandatory, not optional
- Copied tests from Sessions 6-8 remain unmodified (Artículo VIII)
