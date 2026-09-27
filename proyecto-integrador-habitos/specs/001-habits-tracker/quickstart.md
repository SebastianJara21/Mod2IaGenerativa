# Quickstart: Personal Habits Tracker Validation Guide

This guide provides runnable validation scenarios to verify the Personal Habits Tracker feature works end-to-end. Use this to test each core user journey before, during, and after implementation.

**Prerequisites**:
- FastAPI app running on `http://localhost:8000` (or adjust BASE_URL)
- SQLite database (`:memory:` or file-based for testing)
- Python 3.10+ with requests library installed

---

## Setup

### 1. Start the FastAPI Server

```bash
cd app/
uvicorn main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 2. Verify the Server is Running

```bash
curl -X GET http://localhost:8000/docs
```

Expected output: Swagger UI HTML (status 200)

---

## Test Scenarios

Each scenario is independently testable and demonstrates core functionality. Run them in order or skip to the ones relevant for your validation.

### Scenario 1: User Registration

**Objective**: Verify user registration with email/password returns 201 and user object (no password exposed).

**Command**:
```bash
curl -X POST http://localhost:8000/usuarios/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "password123"
  }'
```

**Expected Response** (201 Created):
```json
{
  "id": 1,
  "email": "alice@example.com",
  "created_at": "2026-09-27T12:00:00Z"
}
```

**Validation Points**:
- Status code is 201
- Response includes `id`, `email`, `created_at`
- `password` is NOT in response
- Subsequent calls with same email return 400 "email duplicado"

**Next**: Proceed to Scenario 2

---

### Scenario 2: User Login

**Objective**: Verify login with email/password returns JWT token.

**Command**:
```bash
curl -X POST http://localhost:8000/usuarios/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice@example.com&password=password123"
```

**Expected Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIn0.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ",
  "token_type": "bearer"
}
```

**Validation Points**:
- Status code is 200
- `access_token` is a valid JWT (can be decoded)
- `token_type` is "bearer"
- Invalid password returns 401 "credenciales inválidas"

**Save Token**: Store the `access_token` value for subsequent tests:
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Next**: Proceed to Scenario 3

---

### Scenario 3: Create a Habit

**Objective**: Verify authenticated user can create a habit with name and frequency.

**Command**:
```bash
curl -X POST http://localhost:8000/habitos/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "nombre": "Exercise",
    "frecuencia_objetivo": 3
  }'
```

**Expected Response** (201 Created):
```json
{
  "id": 101,
  "nombre": "Exercise",
  "frecuencia_objetivo": 3,
  "usuario_id": 1,
  "created_at": "2026-09-27T12:05:00Z"
}
```

**Validation Points**:
- Status code is 201
- Response includes `id`, `nombre`, `frecuencia_objetivo`, `usuario_id`, `created_at`
- `usuario_id` matches the authenticated user (from JWT)
- Frequency outside [1, 7] returns 400 "frecuencia_objetivo must be between 1 and 7"
- Empty name returns 422 validation error
- Request without token returns 401

**Save Habit ID**: Store the `id` for subsequent tests:
```bash
HABITO_ID=101
```

**Next**: Proceed to Scenario 4

---

### Scenario 4: List Habits

**Objective**: Verify authenticated user can list their habits with pagination.

**Command**:
```bash
curl -X GET "http://localhost:8000/habitos/?skip=0&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response** (200 OK):
```json
{
  "items": [
    {
      "id": 101,
      "nombre": "Exercise",
      "frecuencia_objetivo": 3,
      "usuario_id": 1,
      "created_at": "2026-09-27T12:05:00Z"
    }
  ],
  "total": 1
}
```

**Validation Points**:
- Status code is 200
- Response includes `items` (list) and `total` (count)
- Only habits belonging to authenticated user are returned
- Pagination works: `skip=0&limit=1` returns only 1 item
- Invalid pagination (e.g., `skip=abc`) returns 422

**Next**: Proceed to Scenario 5

---

### Scenario 5: Mark Today's Habit

**Objective**: Verify marking a habit as completed for today (default date).

**Command**:
```bash
curl -X POST "http://localhost:8000/habitos/$HABITO_ID/marcar" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{}'
```

**Expected Response** (201 Created):
```json
{
  "id": 201,
  "habito_id": 101,
  "usuario_id": 1,
  "fecha": "2026-09-27",
  "created_at": "2026-09-27T12:10:00Z"
}
```

**Validation Points**:
- Status code is 201
- `fecha` is today's date (YYYY-MM-DD format)
- Response includes `id`, `habito_id`, `usuario_id`, `fecha`, `created_at`
- Marking the same habit again today returns 400 "ya marcado ese día"
- Marking without authentication returns 401

**Next**: Proceed to Scenario 6

---

### Scenario 6: Retroactive Marking (Past Date)

**Objective**: Verify user can mark a habit for a past date (retroactive marking is allowed).

**Command**:
```bash
curl -X POST "http://localhost:8000/habitos/$HABITO_ID/marcar" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "fecha": "2026-09-26"
  }'
```

**Expected Response** (201 Created):
```json
{
  "id": 202,
  "habito_id": 101,
  "usuario_id": 1,
  "fecha": "2026-09-26",
  "created_at": "2026-09-27T12:11:00Z"
}
```

**Validation Points**:
- Status code is 201 (past date is allowed)
- `fecha` is the requested past date
- Marking the same habit on the same past date again returns 400 "ya marcado ese día"

**Next**: Proceed to Scenario 7

---

### Scenario 7: Reject Future Date

**Objective**: Verify marking a habit for a future date is rejected (FR-11a).

**Command**:
```bash
curl -X POST "http://localhost:8000/habitos/$HABITO_ID/marcar" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "fecha": "2026-09-28"
  }'
```

**Expected Response** (400 Bad Request):
```json
{
  "detail": "fecha no puede ser posterior a la fecha actual"
}
```

**Validation Points**:
- Status code is 400 (not 201)
- Error message is specific: "fecha no puede ser posterior a la fecha actual"
- No Marca record created for future date

**Next**: Proceed to Scenario 8

---

### Scenario 8: Duplicate Mark Prevention

**Objective**: Verify same habit cannot be marked twice on the same day.

**Command** (mark today again):
```bash
curl -X POST "http://localhost:8000/habitos/$HABITO_ID/marcar" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "fecha": "2026-09-27"
  }'
```

**Expected Response** (400 Bad Request):
```json
{
  "detail": "ya marcado ese día"
}
```

**Validation Points**:
- Status code is 400
- Error message is "ya marcado ese día"
- No duplicate Marca record created

**Next**: Proceed to Scenario 9

---

### Scenario 9: Delete a Habit

**Objective**: Verify deleting a habit removes it from the user's list.

**Command**:
```bash
curl -X DELETE "http://localhost:8000/habitos/$HABITO_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response** (204 No Content):
```
(empty body)
```

**Validation Points**:
- Status code is 204
- Response body is empty
- Subsequent GET /habitos/ no longer includes the deleted habit
- Subsequent DELETE on same habit returns 404

**Verification**: List habits again to confirm deletion:
```bash
curl -X GET "http://localhost:8000/habitos/" \
  -H "Authorization: Bearer $TOKEN"
```

Expected: `"items": []`, `"total": 0`

**Next**: Proceed to Scenario 10

---

### Scenario 10: Ownership Enforcement

**Objective**: Verify user cannot access another user's habits.

**Setup**: Register a second user and get their token:
```bash
curl -X POST http://localhost:8000/usuarios/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bob@example.com",
    "password": "password456"
  }'

curl -X POST http://localhost:8000/usuarios/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=bob@example.com&password=password456"
```

Save Bob's token as `TOKEN_BOB` and his user ID (from JWT decode) as `BOB_ID`.

**Create a habit for Alice (first user)** and save its ID as `ALICE_HABIT_ID`:
```bash
curl -X POST http://localhost:8000/habitos/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "nombre": "Yoga",
    "frecuencia_objetivo": 2
  }'
# Response: { "id": 103, ... }  <- ALICE_HABIT_ID = 103
```

**Bob attempts to mark Alice's habit**:
```bash
curl -X POST "http://localhost:8000/habitos/$ALICE_HABIT_ID/marcar" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_BOB" \
  -d '{
    "fecha": "2026-09-27"
  }'
```

**Expected Response** (404 Not Found):
```json
{
  "detail": "Hábito no encontrado"
}
```

**Validation Points**:
- Status code is 404 (not 403 — ownership is hidden for security)
- Bob cannot access Alice's habit
- Bob's list (GET /habitos/) never shows Alice's habits

**Conclusion**: Ownership enforcement prevents cross-user data access.

---

## Test Summary Table

| Scenario | Endpoint | Method | Expected Status | Key Assertion |
|----------|----------|--------|-----------------|---------------|
| 1. Register | /usuarios/ | POST | 201 | Email unique, password hidden |
| 2. Login | /usuarios/token | POST | 200 | JWT token returned |
| 3. Create Habit | /habitos/ | POST | 201 | Frequency validated [1-7] |
| 4. List Habits | /habitos/ | GET | 200 | Paginated, user-filtered |
| 5. Mark Today | /habitos/{id}/marcar | POST | 201 | Date defaults to today |
| 6. Mark Past | /habitos/{id}/marcar | POST | 201 | Retroactive marking allowed |
| 7. Mark Future | /habitos/{id}/marcar | POST | 400 | Future date rejected (FR-11a) |
| 8. Duplicate | /habitos/{id}/marcar | POST | 400 | Same date, same habit rejected |
| 9. Delete | /habitos/{id} | DELETE | 204 | Habit removed from list |
| 10. Ownership | /habitos/{id}/marcar | POST | 404 | Cross-user access denied |

---

## Automation Script

For CI/CD integration, use pytest or similar to automate these scenarios:

```bash
# Run all scenarios with pytest
pytest tests/api/test_scenarios.py -v

# Or use curl in a shell script:
bash tests/scripts/validate-quickstart.sh
```

(Specific implementation of test scripts depends on test framework chosen; see tasks.md for test breakdown)

---

## Data Model Reference

For detailed schema information, see [data-model.md](data-model.md).

For detailed endpoint specifications, see [contracts/REST_API.md](contracts/REST_API.md) and [contracts/MCP_TOOLS.md](contracts/MCP_TOOLS.md).

---

## Troubleshooting

### 401 Unauthorized on Protected Endpoints

**Symptom**: GET /habitos/ returns 401 even with token.

**Check**:
1. Is TOKEN variable set? `echo $TOKEN`
2. Is token valid (not expired)? Decode with `jwt.io` or Python `jwt.decode()`
3. Is Authorization header format correct? `Authorization: Bearer <token>` (space-separated)

### 422 Validation Error on POST /usuarios/

**Symptom**: Email looks valid but returns 422.

**Check**:
1. Email format is valid (pydantic.EmailStr requirements)
2. No typos in JSON field names (`email`, not `Email` or `e_mail`)
3. Content-Type header is `application/json`

### 404 on DELETE /habitos/{id}

**Symptom**: Habit was created but DELETE returns 404.

**Check**:
1. Habit ID is correct (copy from CREATE response)
2. You are using the same token (same user)
3. Habit was not already deleted

---

**Validation Complete**: All 10 scenarios pass → Feature is ready for production.

**Next Steps**: See [tasks.md](../../../tasks.md) for implementation task breakdown (Phase 2).
