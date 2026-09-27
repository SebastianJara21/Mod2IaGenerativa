# Tasks: Personal Habits Tracker

**Input**: Design documents from `/specs/001-habits-tracker/`

**Prerequisites**: plan.md (completed), spec.md (completed), research.md, data-model.md, contracts/, quickstart.md

**Tests**: MANDATORY per Artículo VII (Constitución). Every code task MUST have corresponding test in green as part of its definition of done.

**Organization**: Tasks grouped by user story (US1, US2, US3, US4) enabling independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Parallelizable (different files, no dependencies on incomplete tasks)
- **[Story]**: User story label (US1, US2, US3, US4) - mandatory for story-specific tasks
- **File paths**: Exact locations for code and tests
- **Definition of Done**: (1) Code written, (2) Test passes (green), (3) No constitution violations

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, database schema

- [ ] T001 Create project structure: `app/`, `tests/`, `migrations/` per plan.md
- [ ] T002 Initialize Python environment: pyproject.toml with FastAPI, SQLAlchemy, pyjwt, passlib[bcrypt], pytest dependencies
- [ ] T003 [P] Create app/config.py (BaseSettings) reading .env: SECRET_KEY, DATABASE_URL, ACCESS_TOKEN_EXPIRE_MINUTES
- [ ] T004 [P] Create .env.example template (no secrets, only variable names)
- [ ] T005 Create app/database.py (SQLAlchemy engine, sessionmaker, conditional connect_args for SQLite vs Postgres)
- [ ] T006 Create app/models/__init__.py (ORM base class, metadata)
- [ ] T007 [P] Create app/models/usuario.py (Usuario ORM model: id, email UNIQUE, password_hash, created_at)
- [ ] T008 [P] Create app/models/habito.py (Habito ORM model: id, usuario_id FK, nombre, frecuencia_objetivo, created_at) + (Marca ORM model: id, habito_id FK, usuario_id FK, fecha, created_at with UNIQUE(habito_id, fecha))
- [ ] T009 Create Alembic migration for initial schema: `migrations/versions/001_initial_schema.py`
- [ ] T010 [P] Create tests/conftest.py (pytest fixtures: in-memory SQLite engine, SessionLocal, db session, app.dependency_overrides)
- [ ] T011 [P] Create tests/unit/test_fixtures.py (verify conftest fixtures work correctly)
- [ ] T012 Create app/utils/crypto.py (passlib password hash/verify wrapper, single bcrypt scheme)
- [ ] T013 [P] Create tests/unit/test_crypto.py (hash/verify round-trip, password mismatch detection)

---

## Phase 2: Foundational (Authentication + Authorization)

**Purpose**: Core auth infrastructure - BLOCKS all user story work

**⚠️ CRITICAL**: No user story implementation can begin until this phase is complete

- [ ] T014 Create app/services/usuarios.py: crear_usuario(email, password), autenticar_usuario(email, password) → JWT, get_current_user(token)
  - **Definition of Done**: (1) Code written, (2) Tests pass (see T015), (3) No constitution violations (uses get_current_user from JWT, never from input)
- [ ] T015 [P] Create tests/unit/test_usuarios_service.py: test_crear_usuario_success, test_crear_usuario_duplicate_email (400), test_autenticar_usuario_success, test_autenticar_usuario_invalid_password (401), test_get_current_user_valid_token, test_get_current_user_invalid_token (401)
  - Uses FakeUsuariosRepository (no unittest.mock)
  - Definition of Done: All tests GREEN, FakeUsuariosRepository injected as parameter
- [ ] T016 Create app/repositories/usuarios.py: UsuariosRepository class with save_usuario(usuario), get_usuario_by_email(email), get_usuario_by_id(id)
  - Definition of Done: (1) Code written, (2) Tests pass (see T017), (3) Uses Session from db fixture
- [ ] T017 [P] Create tests/integration/test_usuarios_repository.py: test_save_usuario, test_get_usuario_by_email (exists + not_exists), test_get_usuario_by_id (exists + not_exists)
  - Uses real in-memory SQLite (from conftest fixture)
  - Definition of Done: All tests GREEN with real DB
- [ ] T018 Create app/schemas/usuario.py (Pydantic): UsuarioCreate (email, password), UsuarioResponse (id, email, created_at - NO password), Token (access_token, token_type)
  - Constraint from spec: email (valid EmailStr), password (required), never expose password_hash
  - Definition of Done: (1) Code written, (2) Validation tests pass
- [ ] T019 Create app/routers/usuarios.py (HTTP layer):
  - POST /usuarios/ (register) → UsuarioCreate → services.crear_usuario → UsuarioResponse (201) or 400/422
  - POST /usuarios/token (login) → OAuth2PasswordRequestForm → services.autenticar_usuario → Token (200) or 401
  - Definition of Done: (1) Code written, (2) API tests pass (see T020), (3) Password never exposed, user_id from JWT
- [ ] T020 [P] Create tests/api/test_usuarios_endpoints.py: test_post_usuarios_success (201), test_post_usuarios_duplicate_email (400), test_post_usuarios_invalid_email (422), test_post_token_success (200, valid JWT), test_post_token_invalid_password (401)
  - Uses app.dependency_overrides for get_db
  - Definition of Done: All tests GREEN with FastAPI TestClient
- [ ] T021 Create app/mcp/auth.py: extract_jwt_from_request(request) extracts Bearer token from Authorization header; adapt get_current_user for MCP streamable-http context
  - Definition of Done: (1) Code written, (2) Tests pass (JWT extraction verified)
- [ ] T022 [P] Create tests/unit/test_mcp_auth.py: test_extract_jwt_valid, test_extract_jwt_missing (None), test_extract_jwt_malformed
  - Definition of Done: All tests GREEN

**Checkpoint**: Authentication + Authorization foundation ready. All subsequent user stories depend on this. Test independently:
```bash
pytest tests/unit/test_usuarios_service.py tests/integration/test_usuarios_repository.py tests/api/test_usuarios_endpoints.py -v
```

---

## Phase 3: User Story 1 - User Registration and Authentication (Priority: P1) 🎯 MVP

**Goal**: Users can register with email/password and log in to obtain JWT token

**Independent Test**: Run US1 end-to-end via quickstart.md scenarios 1 & 2 (Register + Login)

### Implementation for User Story 1

- [ ] T023 Verify Phase 2 (T014-T022) complete: All auth infrastructure in place
  - Definition of Done: `pytest tests/unit/test_usuarios_service.py tests/integration/test_usuarios_repository.py tests/api/test_usuarios_endpoints.py` all GREEN

**Checkpoint**: User Story 1 complete. Users can register and login independently.

```bash
# Verify US1 works:
pytest tests/api/test_usuarios_endpoints.py::test_post_usuarios_success -v
pytest tests/api/test_usuarios_endpoints.py::test_post_token_success -v
```

---

## Phase 4: User Story 2 - Create and List Habits (Priority: P1)

**Goal**: Authenticated users create habits with name + frequency (1-7), and list them with pagination

**Independent Test**: Run US2 end-to-end via quickstart.md scenarios 3 & 4 (Create Habit + List Habits)

### Implementation for User Story 2

- [ ] T024 Create app/services/habitos.py: crear_habito(nombre, frecuencia_objetivo, usuario_id, repo=habitos_repository), listar_habitos(usuario_id, skip, limit, repo=habitos_repository)
  - **Constraints from data-model.md**: 
    - nombre: non-empty, 1-255 chars (str type in SQLAlchemy)
    - frecuencia_objetivo: integer in [1, 7] inclusive (validate in _validar_frecuencia_objetivo)
  - **Definition of Done**: (1) Code written, (2) Tests pass (see T025), (3) DIP: repo injected as parameter (not imported), (4) validation separate from orquestration, (5) No SQLAlchemy imports in services
- [ ] T025 [P] Create tests/unit/test_habitos_service.py: test_crear_habito_success, test_crear_habito_nombre_vacio (422), test_crear_habito_frecuencia_invalida (0, 8 → 400), test_listar_habitos_empty, test_listar_habitos_paginated
  - Uses FakeHabitosRepository (no unittest.mock)
  - Definition of Done: All tests GREEN, repository injected as parameter
- [ ] T026 Create app/repositories/habitos.py: HabitosRepository class with save_habito(habito), get_habitos_by_usuario(usuario_id, skip, limit), get_habito_by_id(id, usuario_id)
  - **Query filtering**: All queries include `usuario_id` filter (ownership enforcement per Artículo IV)
  - Definition of Done: (1) Code written, (2) Tests pass (see T027), (3) All queries include usuario_id filter
- [ ] T027 [P] Create tests/integration/test_habitos_repository.py: test_save_habito, test_get_habitos_by_usuario_empty, test_get_habitos_by_usuario_paginated, test_get_habito_by_id (exists + not_exists), test_get_habito_by_id_cross_user (returns None, ownership check)
  - Uses real in-memory SQLite
  - Definition of Done: All tests GREEN, ownership enforcement verified
- [ ] T028 Create app/schemas/habito.py (Pydantic): HabitoCreate (nombre, frecuencia_objetivo), HabitoResponse (id, nombre, frecuencia_objetivo, usuario_id, created_at), HabitoListResponse (items: List[HabitoResponse], total)
  - Constraint: nombre non-empty (min_length=1)
  - Definition of Done: (1) Code written, (2) Validation tests pass
- [ ] T029 Create app/routers/habitos.py (HTTP layer):
  - POST /habitos/ (create) → HabitoCreate → services.crear_habito → HabitoResponse (201) or 400/401/422
  - GET /habitos/ (list) → query params skip, limit → services.listar_habitos → HabitoListResponse (200) or 401/422
  - Both require authentication (get_current_user dependency)
  - **usuario_id ALWAYS from JWT, never from input** (Artículo IV)
  - Definition of Done: (1) Code written, (2) API tests pass (see T030), (3) usuario_id from JWT (verify in tests), (4) Ownership enforced
- [ ] T030 [P] Create tests/api/test_habitos_endpoints.py: test_post_habitos_success (201), test_post_habitos_nombre_vacio (422), test_post_habitos_frecuencia_invalida (400), test_get_habitos_empty (200), test_get_habitos_paginated (200), test_post_habitos_unauthenticated (401), test_get_habitos_unauthenticated (401)
  - Uses app.dependency_overrides for get_db, repository, get_current_user
  - Definition of Done: All tests GREEN, usuario_id from JWT verified in tests

**Checkpoint**: User Story 2 complete. Users can create and list habits independently. Test US1 + US2:
```bash
pytest tests/api/test_usuarios_endpoints.py tests/api/test_habitos_endpoints.py -v
```

---

## Phase 5: User Story 3 - Mark Daily Habit Completion (Priority: P1)

**Goal**: Users mark habits as completed for a specific date (retroactive allowed, future rejected per FR-11a), prevent duplicates

**Independent Test**: Run US3 end-to-end via quickstart.md scenarios 5, 6, 7, 8 (Mark Today + Retroactive + Reject Future + Duplicate Prevention)

### Implementation for User Story 3

- [ ] T031 Create app/services/habitos.py additions: marcar_habito(habito_id, fecha, usuario_id, repo=habitos_repository)
  - **Constraint from Business Rules (FR-11a)**: fecha must be ≤ today (server's current date)
  - **Constraint from spec**: no duplicate (habito_id, fecha) pairs
  - **Definition of Done**: (1) Code written, (2) Tests pass (see T032), (3) _validar_fecha (FR-11a) separate from marcar_habito, (4) _validar_duplicate_marca separate, (5) DIP: repo injected
- [ ] T032 [P] Create tests/unit/test_habitos_service.py additions: test_marcar_habito_today (success), test_marcar_habito_past (retroactive, success), test_marcar_habito_future (400 "fecha no puede ser posterior a la fecha actual"), test_marcar_habito_duplicate (400 "ya marcado ese día"), test_marcar_habito_nonexistent_habito (404)
  - Uses FakeHabitosRepository with FakeMarca storage
  - Definition of Done: All tests GREEN, fecha validation ≤ today verified, duplicate check verified
- [ ] T033 Create app/schemas/habito.py additions: MarcaCreate (fecha: Optional[date] = today), MarcaResponse (id, habito_id, usuario_id, fecha, created_at)
  - Constraint: fecha is optional, defaults to today
  - Definition of Done: (1) Code written, (2) Date parsing tests pass
- [ ] T034 Create app/routers/habitos.py additions: POST /habitos/{id}/marcar (mark)
  - Path param: id (habito_id)
  - Body: MarcaCreate (fecha optional)
  - Response: MarcaResponse (201) or 400/401/404
  - **Ownership check**: verify habito.usuario_id == current_user_id before marking (Artículo IV)
  - Definition of Done: (1) Code written, (2) API tests pass (see T035), (3) Ownership verified, (4) Future date rejected (400), (5) Duplicate rejected (400)
- [ ] T035 [P] Create tests/api/test_habitos_endpoints.py additions: test_post_marcar_today (201), test_post_marcar_past (201), test_post_marcar_future (400), test_post_marcar_duplicate (400), test_post_marcar_nonexistent (404), test_post_marcar_cross_user (404, ownership), test_post_marcar_unauthenticated (401)
  - Uses app.dependency_overrides
  - **CRITICAL**: Explicit test for FR-11a (future date → 400 "fecha no puede ser posterior a la fecha actual")
  - Definition of Done: All tests GREEN, especially FR-11a test must be included

**Checkpoint**: User Story 3 complete. Users can mark habits with retroactive support + future rejection. Test US1 + US2 + US3:
```bash
pytest tests/api/test_usuarios_endpoints.py tests/api/test_habitos_endpoints.py -v
```

---

## Phase 6: User Story 4 - Delete a Habit (Priority: P2)

**Goal**: Users delete habits (and associated marks). Deletion requires explicit server-side confirmation.

**Independent Test**: Run US4 end-to-end via quickstart.md scenarios 9 (Delete Habit)

### Implementation for User Story 4

- [ ] T036 Create app/services/habitos.py additions: eliminar_habito(habito_id, usuario_id, confirmed=False, repo=habitos_repository)
  - **Confirmation flow**: First call with confirmed=False → return confirmation_required; second call with confirmed=True → execute delete
  - **Ownership check**: verify habito.usuario_id == usuario_id before deletion
  - **Cascade**: Delete all associated Marca entries
  - Definition of Done: (1) Code written, (2) Tests pass (see T037), (3) Ownership verified, (4) Confirmation enforced
- [ ] T037 [P] Create tests/unit/test_habitos_service.py additions: test_eliminar_habito_unconfirmed (confirmation_required), test_eliminar_habito_confirmed (success), test_eliminar_habito_cross_user (ownership check), test_eliminar_habito_nonexistent (404)
  - Uses FakeHabitosRepository
  - Definition of Done: All tests GREEN, confirmation logic verified, ownership verified
- [ ] T038 Create app/routers/habitos.py additions: DELETE /habitos/{id} (delete)
  - Path param: id (habito_id)
  - Response: 204 (deleted) or 401/403/404
  - **Ownership check**: verify habito.usuario_id == current_user_id before deleting
  - **HTTP 403 vs 404**: Use 403 if explicitly identifying resource, else 404 for security (see contracts/REST_API.md)
  - Definition of Done: (1) Code written, (2) API tests pass (see T039), (3) Ownership verified, (4) Correct HTTP code
- [ ] T039 [P] Create tests/api/test_habitos_endpoints.py additions: test_delete_habitos_success (204), test_delete_habitos_cross_user (403 or 404), test_delete_habitos_nonexistent (404), test_delete_habitos_unauthenticated (401)
  - Uses app.dependency_overrides
  - Definition of Done: All tests GREEN, ownership enforcement verified

**Checkpoint**: User Story 4 complete. Users can delete habits independently. Test full feature:
```bash
pytest tests/api/test_usuarios_endpoints.py tests/api/test_habitos_endpoints.py -v
```

---

## Phase 7: MCP Server Integration

**Purpose**: Wire up MCP tools (criar_habito, marcar_habito, listar_habitos, eliminar_habito) within FastAPI app

- [ ] T040 Create app/mcp/tools.py: Tool definitions for each of the 4 tools
  - Each tool: description (specific, not generic), parameters, success/error response
  - **Definition of Done**: (1) Code written, (2) Tests pass (see T041-T044), (3) Each tool calls services/ directly (no logic reimplementation)
- [ ] T041 [P] Create tests/unit/test_mcp_tools.py: test_criar_habito_tool_success, test_criar_habito_tool_invalid_frequency (400), test_criar_habito_tool_unauthenticated
  - Uses FakeHabitosRepository + FakeUsuariosRepository
  - Definition of Done: All tests GREEN
- [ ] T042 [P] Create tests/unit/test_mcp_tools.py additions: test_marcar_habito_tool_success, test_marcar_habito_tool_future_date (400 FR-11a), test_marcar_habito_tool_duplicate (400), test_marcar_habito_tool_unauthenticated
  - **CRITICAL**: Explicit test for FR-11a in MCP context
  - Definition of Done: All tests GREEN
- [ ] T043 [P] Create tests/unit/test_mcp_tools.py additions: test_listar_habitos_tool_success, test_listar_habitos_tool_pagination, test_listar_habitos_tool_unauthenticated
  - Definition of Done: All tests GREEN
- [ ] T044 [P] Create tests/unit/test_mcp_tools.py additions: test_eliminar_habito_tool_unconfirmed (confirmation prompt), test_eliminar_habito_tool_confirmed (success), test_eliminar_habito_tool_cross_user (error), test_eliminar_habito_tool_unauthenticated
  - Definition of Done: All tests GREEN
- [ ] T045 Create app/mcp/server.py: MCP server setup (streamable-http transport), register all 4 tools
  - **Definition of Done**: (1) Code written, (2) Tests pass (see T046)
- [ ] T046 Create tests/unit/test_mcp_server.py: test_mcp_server_initialization, test_mcp_server_tools_registered
  - Definition of Done: All tests GREEN
- [ ] T047 Integrate MCP server into app/main.py: Create MCP server instance, ensure get_current_user uses JWT from MCP session
  - **Definition of Done**: (1) Code written, (2) Integration test passes (see T048)
- [ ] T048 Create tests/integration/test_mcp_integration.py: End-to-end MCP tool calls via streamable-http context
  - Definition of Done: All tests GREEN, MCP tools callable with JWT auth

**Checkpoint**: MCP server integrated. Tools callable. Test:
```bash
pytest tests/unit/test_mcp_tools.py tests/unit/test_mcp_server.py tests/integration/test_mcp_integration.py -v
```

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final touches, validation, coverage verification

- [ ] T049 [P] Create tests/api/test_ownership_enforcement.py: Comprehensive cross-user access denial tests across all endpoints
  - Verify 404 returns for non-owned habits (never 403 to prevent enumeration)
  - Definition of Done: All tests GREEN
- [ ] T050 [P] Create tests/api/test_error_cases.py: Collect all error cases from spec (6 explicit error cases from Business Rules section)
  - Test 1: Duplicate mark same day (400)
  - Test 2: Frequency out of range (400)
  - Test 3: Unauthenticated (401)
  - Test 4: Cross-user access (404)
  - Test 5: Non-existent habit (404)
  - Test 6: **Future date (400 FR-11a)** — CRITICAL
  - Definition of Done: All 6 tests GREEN
- [ ] T051 Run quickstart.md validation: Execute all 10 scenarios from quickstart.md
  - Scenarios 1-10 from quickstart.md (Register, Login, Create, List, Mark Today, Retroactive, Future Reject, Duplicate Prevention, Delete, Ownership)
  - Definition of Done: All scenarios pass end-to-end
- [ ] T052 [P] Create docs/API_USAGE.md: User guide for REST endpoints
- [ ] T053 [P] Create docs/MCP_TOOLS_USAGE.md: User guide for MCP tools
- [ ] T054 Code cleanup: Remove debug logging, ensure consistent formatting
- [ ] T055 **FINAL: Run pytest --cov=app --cov-report=term-missing and verify coverage thresholds**
  - **Artículo VII.3 Requirements**:
    - `app/services/` coverage ≥ 90%
    - `app/services/ + app/repositories/ + app/routers/ + app/utils/` coverage ≥ 70%
    - Exclusions in [tool.coverage.run] omit: `main.py`, `mcp/server.py`, `mcp/auth.py`
  - Definition of Done: Both thresholds met, report generated
  - **CRITICAL**: This task MUST complete successfully before feature is considered done

**Checkpoint**: All tests pass, coverage verified, quickstart validates end-to-end.

```bash
# Final validation:
pytest tests/ -v --cov=app --cov-report=term-missing
```

**Feature Complete**: All phases done, all tests GREEN, coverage verified.

---

## Dependencies & Execution Order

### Phase Dependencies

1. **Setup (Phase 1)**: No dependencies - START HERE
2. **Foundational (Phase 2)**: DEPENDS on Setup (T001-T013) - BLOCKS all user stories
3. **User Story 1 (Phase 3)**: DEPENDS on Foundational (T014-T022)
4. **User Story 2 (Phase 4)**: DEPENDS on Foundational + US1 (independent of each other for testing)
5. **User Story 3 (Phase 5)**: DEPENDS on Foundational + US1 + US2 (independent testing)
6. **User Story 4 (Phase 6)**: DEPENDS on Foundational + US1 + US2 + US3 (independent testing)
7. **MCP Server (Phase 7)**: DEPENDS on all user stories (T031-T048)
8. **Polish (Phase 8)**: DEPENDS on all above (T049-T055)

### Critical Blocking Points

- **BLOCK-1**: Setup must complete (T001-T013) before anything else
- **BLOCK-2**: Foundational must complete (T014-T022) before any user story
- **BLOCK-3**: T055 (coverage verification) must pass before feature delivery

### Within Each User Story

- Models/Entities before Services
- Services before Routers/Endpoints
- Code before Tests (but write tests FIRST, make them FAIL, then implement)
- Ownership verification in ALL tests

---

## Parallel Opportunities

### After Setup Completes

All Foundational tasks marked [P] (T003, T004, T007, T008, T010, T011, T013) can run in parallel

### After Foundational Completes

- **US1 (Registration/Auth)**: T023 (verification only, depends on Phase 2)
- **US2 (Create/List)**: T024-T030 can run in parallel by team
- **US3 (Mark)**: T031-T035 can run in parallel
- **US4 (Delete)**: T036-T039 can run in parallel
- **MCP Server**: T040-T048 after US2/US3/US4 complete

### Parallel Opportunities Within Stories

**User Story 2 Example**:
```
T024 (criar_habito service)
T025 (test crear_habito)  — can start as T024 is written
T026 (habitos repository) — can start in parallel with T024
T027 (test repository)     — can start as T026 is written
T028 (schemas)             — can start in parallel
T029 (router)              — depends on T024, T026, T028
T030 (test router)         — can start as T029 is written
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Setup (T001-T013) → foundation ready
2. Complete Foundational (T014-T022) → auth ready
3. Complete US1 (T023) → users can register/login
4. Complete US2 (T024-T030) → users can create/list habits
5. Complete US3 (T031-T035) → users can mark habits (with retroactive + future rejection)
6. **STOP and VALIDATE**: Test via quickstart scenarios 1-8
7. Deploy MVP (US1-3) — this is a complete feature

### Incremental Delivery

After MVP validation:
8. Add US4 (T036-T039) → delete capability
9. Add MCP Server (T040-T048) → programmatic access
10. Polish (T049-T055) → documentation + coverage

### Parallel Team Strategy

With 3+ developers after Setup + Foundational:
- Dev A: US2 (Create/List habits) — T024-T030
- Dev B: US3 (Mark habits) — T031-T035
- Dev C: US4 (Delete) — T036-T039
- Dev D: MCP integration — T040-T048 (after others deliver)
- Dev A/B/C/D: Polish — T049-T055

---

## Definition of Done Checklist (Per Task)

Every code task MUST satisfy:

1. **Code Written**: File created/modified at specified path
2. **Test Passes**: Corresponding test(s) GREEN (pytest output)
3. **No Violations**: Code follows all 7 articles of Constitución
   - Architecture: correct layer (router/service/repo/util)
   - DIP: dependencies injected (no direct imports of services/repos)
   - Ownership: usuario_id from JWT, never from input
   - Security: passwords hashed, tokens signed, .env-based config
   - Validation: Pydantic before services
   - Error handling: Proper HTTP codes (401/403/404/400/422)
   - Testing: Fake repositories, no unittest.mock

**Special Note on FR-11a**: Task T035 must include explicit test for future date rejection (400 "fecha no puede ser posterior a la fecha actual"). This requirement was added after initial spec and is critical to NOT skip in implementation.

**Coverage Requirement**: Task T055 must verify coverage thresholds:
- services/ ≥ 90%
- services + repositories + routers + utils ≥ 70%

---

## Notes

- [P] = parallelizable (different files, no blocking dependencies)
- Each user story is independently testable
- Commit after each logical group or checkpoint
- Stop at any checkpoint to validate independently
- Avoid: vague tasks, same-file conflicts, hidden dependencies
- **CRITICAL**: Do not skip T055 (coverage verification) — it's a gate for feature completion

---

**Next Steps**: Start with Phase 1 (Setup). When complete, proceed to Phase 2 (Foundational). User stories can then proceed in parallel.
