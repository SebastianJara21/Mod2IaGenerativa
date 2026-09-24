# Quickstart: Sistema de Control de Gastos

**Date**: 2026-09-23  
**Phase**: Phase 1 — Validation Guide

This guide demonstrates how to validate that the feature works end-to-end. It assumes the implementation is complete (post `/speckit-implement`).

---

## Prerequisites

1. **Python 3.8+** with virtual environment activated
2. **Dependencies installed**: `pip install -r requirements.txt` (includes FastAPI, SQLAlchemy, pyjwt, pytest, httpx, etc.)
3. **Database initialized**: `alembic upgrade head` (creates tables in SQLite `.env` DATABASE_URL)
4. **Environment configured**: `.env` file with:
   ```env
   SECRET_KEY=<generated via `openssl rand -hex 32`>
   DATABASE_URL=sqlite:///./gastos.db
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```
5. **Tests available**: `tests/` directory with test suite

---

## Scenario 1: User Registration & Authentication

### Use Case
A new user registers, then authenticates to get a JWT token.

### Steps

1. **Start the app** (in one terminal):
   ```bash
   uvicorn app.main:app --reload
   ```
   Server listens on `http://localhost:8000`

2. **Register a user** (curl or Postman):
   ```bash
   curl -X POST http://localhost:8000/usuarios/ \
     -H "Content-Type: application/json" \
     -d '{"email": "alice@example.com", "password": "secure123"}'
   ```
   
   **Expected Response** (201 Created):
   ```json
   {
     "id": 1,
     "email": "alice@example.com",
     "created_at": "2026-09-23T12:34:56Z"
   }
   ```
   
   **Note**: No `hashed_password` in response (security)

3. **Authenticate user** (get JWT):
   ```bash
   curl -X POST http://localhost:8000/usuarios/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=alice@example.com&password=secure123"
   ```
   
   **Expected Response** (200 OK):
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer"
   }
   ```
   
   Save `access_token` for use in subsequent requests.

### Validation Criteria

- ✓ User registration returns 201 with user data (no password)
- ✓ Duplicate email registration returns 400 "email duplicado"
- ✓ Invalid email format returns 422 (validation error)
- ✓ Authentication with correct credentials returns JWT
- ✓ Authentication with wrong password returns 401

---

## Scenario 2: Register Expense (Happy Path)

### Use Case
An authenticated user registers expenses in different categories, respecting the 500-limit per category.

### Steps

1. **Register first gasto** (comida, monto=100):
   ```bash
   TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # from Scenario 1
   
   curl -X POST http://localhost:8000/gastos/ \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "descripcion": "Almuerzo en restaurante",
       "monto": 100.50,
       "categoria": "comida"
     }'
   ```
   
   **Expected Response** (201 Created):
   ```json
   {
     "id": 1,
     "usuario_id": 1,
     "descripcion": "Almuerzo en restaurante",
     "monto": 100.50,
     "categoria": "comida",
     "created_at": "2026-09-23T12:35:00Z"
   }
   ```

2. **Register another gasto** (comida, monto=300):
   ```bash
   curl -X POST http://localhost:8000/gastos/ \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "descripcion": "Cena familiar",
       "monto": 300.00,
       "categoria": "comida"
     }'
   ```
   
   **Expected Response** (201 Created)
   
   **Total for "comida"**: 100.50 + 300.00 = 400.50 (< 500 ✓)

3. **Register transporte gasto**:
   ```bash
   curl -X POST http://localhost:8000/gastos/ \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "descripcion": "Uber a oficina",
       "monto": 25.00,
       "categoria": "transporte"
     }'
   ```
   
   **Expected Response** (201 Created)
   
   **Total for "transporte"**: 25.00 (< 500 ✓)

### Validation Criteria

- ✓ Gasto created with monto > 0 returns 201
- ✓ Gasto includes all fields in response (id, usuario_id, all inputs, created_at)
- ✓ Multiple gastos in same category accumulate
- ✓ Different categories tracked independently

---

## Scenario 3: Boundary & Error Cases

### Case 3a: Invalid Category

```bash
curl -X POST http://localhost:8000/gastos/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "descripcion": "Compras online",
    "monto": 50.00,
    "categoria": "shopping"
  }'
```

**Expected Response** (400 Bad Request):
```json
{
  "detail": "categoría inválida"
}
```

**Validation**: Invalid category returns 400 (business error), not 422 (validation error)

---

### Case 3b: Monto ≤ 0

```bash
curl -X POST http://localhost:8000/gastos/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "descripcion": "Gasto inválido",
    "monto": 0,
    "categoria": "comida"
  }'
```

**Expected Response** (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "loc": ["body", "monto"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

**Validation**: Monto validation error returns 422 (schema), not 400

---

### Case 3c: Limit Exceeded

1. **Create gastos totaling 450 in "entretenimiento"**:
   ```bash
   # Gasto 1: 250
   # Gasto 2: 200
   # Total: 450
   ```

2. **Attempt gasto exceeding limit**:
   ```bash
   curl -X POST http://localhost:8000/gastos/ \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "descripcion": "Concierto",
       "monto": 100.00,
       "categoria": "entretenimiento"
     }'
   ```
   
   **Expected Response** (400 Bad Request):
   ```json
   {
     "detail": "límite excedido"
   }
   ```

**Validation**: Adding 100 to 450 = 550 > 500 → rejected

---

### Case 3d: Missing Authentication

```bash
curl -X POST http://localhost:8000/gastos/ \
  -H "Content-Type: application/json" \
  -d '{
    "descripcion": "Test",
    "monto": 50.00,
    "categoria": "comida"
  }'
```

**Expected Response** (401 Unauthorized):
```json
{
  "detail": "Not authenticated"
}
```

**Validation**: No token → 401

---

### Case 3e: Empty Description

```bash
curl -X POST http://localhost:8000/gastos/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "descripcion": "",
    "monto": 50.00,
    "categoria": "comida"
  }'
```

**Expected Response** (422 Unprocessable Entity)

**Validation**: Empty string rejected at schema level

---

## Scenario 4: List Gastos (with Pagination & User Isolation)

### Use Case
User lists their gastos; pagination works; cross-user access blocked.

### Steps

1. **List user's gastos** (no pagination):
   ```bash
   curl -X GET http://localhost:8000/gastos/ \
     -H "Authorization: Bearer $TOKEN"
   ```
   
   **Expected Response** (200 OK):
   ```json
   [
     {
       "id": 1,
       "usuario_id": 1,
       "descripcion": "Almuerzo en restaurante",
       "monto": 100.50,
       "categoria": "comida",
       "created_at": "2026-09-23T12:35:00Z"
     },
     {
       "id": 2,
       "usuario_id": 1,
       "descripcion": "Cena familiar",
       "monto": 300.00,
       "categoria": "comida",
       "created_at": "2026-09-23T12:36:00Z"
     },
     ...
   ]
   ```

2. **Paginate results** (skip=0, limit=2):
   ```bash
   curl -X GET "http://localhost:8000/gastos/?skip=0&limit=2" \
     -H "Authorization: Bearer $TOKEN"
   ```
   
   **Expected Response**: First 2 gastos

3. **Paginate next page** (skip=2, limit=2):
   ```bash
   curl -X GET "http://localhost:8000/gastos/?skip=2&limit=2" \
     -H "Authorization: Bearer $TOKEN"
   ```
   
   **Expected Response**: Gastos 3-4

### Validation Criteria

- ✓ List returns only authenticated user's gastos
- ✓ skip/limit pagination works correctly
- ✓ Invalid skip (negative) returns 422
- ✓ Invalid limit (non-numeric) returns 422
- ✓ User cannot see another user's gastos (even if they somehow knew the ID)

---

## Scenario 5: MCP Tools (Optional, CLI/Agent Integration)

### Use Case
A CLI or AI agent calls MCP tools instead of HTTP endpoints.

### Steps

1. **Start MCP server** (if running in streamable-http mode):
   - MCP server runs in FastAPI lifespan
   - Tools available: `registrar_gasto`, `listar_gastos`

2. **Register gasto via MCP tool**:
   ```
   Tool: registrar_gasto
   Arguments: {
     "descripcion": "Gasolina",
     "monto": 45.00,
     "categoria": "transporte"
   }
   MCP Transport: streamable-http (with Authorization header)
   ```
   
   **Expected**: Gasto created, same as REST endpoint

3. **List gastos via MCP tool**:
   ```
   Tool: listar_gastos
   Arguments: {
     "skip": 0,
     "limit": 20
   }
   ```
   
   **Expected**: List returned, same as GET /gastos/

### Validation Criteria

- ✓ Tools call services (no logic duplication)
- ✓ MCP errors match REST errors (CategoriaInvalidaError, LimiteExcedidoError)
- ✓ User identity resolved from token (not from parameter)

---

## Scenario 6: Test Execution

### Run All Tests

```bash
pytest tests/ -v
```

**Expected Output**: All tests pass, coverage meets thresholds

### Run Unit Tests Only

```bash
pytest tests/unit/ -v
```

**Coverage Check**: services/ ≥90%

### Run Integration Tests

```bash
pytest tests/integration/ -v
```

**Uses in-memory SQLite database** (no file created)

### Run API Tests

```bash
pytest tests/api/ -v
```

**Uses TestClient** (httpx); tests HTTP contract

### Coverage Report

```bash
pytest --cov=app --cov-report=term-missing tests/
```

**Expected**: Overall coverage ≥80%, services ≥90%

---

## Clean Up

```bash
# Stop server
Ctrl+C

# Remove test database
rm gastos.db

# Deactivate virtual environment
deactivate
```

---

## Troubleshooting

| Issue | Diagnosis | Solution |
|-------|-----------|----------|
| "No module named 'app'" | Virtual env not activated | `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows) |
| "ImportError: cannot import name 'get_current_user'" | Implementation missing | Ensure `app/dependencies.py` exists and exports get_current_user |
| "Table already exists" (on alembic upgrade) | Multiple migrations applied | Use `alembic downgrade base` then `alembic upgrade head` |
| "401 Not authenticated" | Token missing or expired | Generate new token via `/usuarios/token` |
| Coverage < 80% | Insufficient test coverage | Add tests for uncovered services; check pytest-cov report |

---

## Success Criteria (From Specification)

All scenarios above validate these success criteria:

- ✓ **SC-001**: User registration + auth in <30 seconds
- ✓ **SC-002**: Validation rejects invalid gastos in <500ms
- ✓ **SC-003**: Listing 10k gastos in <1 second
- ✓ **SC-004**: 100% data isolation (zero cross-user gastos)
- ✓ **SC-005**: All 4 categories accepted; invalid rejected with 400
- ✓ **SC-006**: 500-limit enforced in 100% of cases
- ✓ **SC-007**: MCP tools match REST behavior
- ✓ **SC-008**: Password never exposed
- ✓ **SC-009**: Internal errors return 500 generic

---

## Next Steps

- Phase 2: `/speckit-tasks` generates implementation task breakdown
- Phase 3: Implementation phase (`/speckit-implement`) generates code, runs tests, validates coverage
- Phase 4: Deployment (outside Spec Kit scope)
