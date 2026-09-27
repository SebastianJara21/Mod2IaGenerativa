# REST API Contract: Personal Habits Tracker

## Base URL

```
http://localhost:8000  (development)
https://api.habitos.example.com  (production)
```

## Authentication

All endpoints marked **[Auth]** require a valid JWT token in the Authorization header:

```http
Authorization: Bearer <JWT_TOKEN>
```

Token obtained from `POST /usuarios/token`. If token is missing, invalid, or expired → 401 Unauthorized.

---

## Endpoints

### 1. POST /usuarios/

**Purpose**: Register a new user account.

**Auth**: No (public endpoint)

**Request**:
```json
{
  "email": "user@example.com",
  "password": "secure_password_123"
}
```

**Request Schema** (Pydantic):
- `email`: String, email format, required
- `password`: String, min 8 characters, required

**Response 201 (Created)**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2026-09-27T10:30:00Z"
}
```

**Response Schema** (UsuarioResponse):
- `id`: Integer
- `email`: String (never expose password_hash)
- `created_at`: ISO 8601 datetime

**Error 400 (Bad Request)**:
```json
{
  "detail": "email duplicado"
}
```

**Error 422 (Unprocessable Entity)**:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

**Notes**:
- Email must be unique (checked at DB level); duplicate returns 400
- Password is hashed with bcrypt; never returned in response
- Passwords never logged or exposed in errors

---

### 2. POST /usuarios/token

**Purpose**: Authenticate a user and obtain a JWT token.

**Auth**: No (public endpoint)

**Request** (form-encoded, OAuth2 PasswordRequestForm):
```
username=user@example.com&password=secure_password_123
```

Alternatively (JSON, if client prefers):
```json
{
  "username": "user@example.com",
  "password": "secure_password_123"
}
```

**Response 200 (OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Response Schema** (Token):
- `access_token`: String (JWT)
- `token_type`: "bearer" (literal)

**Error 401 (Unauthorized)**:
```json
{
  "detail": "credenciales inválidas"
}
```

**Notes**:
- Uses OAuth2 password flow (username field accepts email)
- Token valid for `ACCESS_TOKEN_EXPIRE_MINUTES` (configurable, default 30 minutes)
- Token never infinite; HS256 signed with SECRET_KEY

---

### 3. POST /habitos/

**Purpose**: Create a new habit for the authenticated user.

**Auth**: [Auth required]

**Request**:
```json
{
  "nombre": "Exercise",
  "frecuencia_objetivo": 3
}
```

**Request Schema** (HabitoCreate):
- `nombre`: String (1-255 chars), non-empty, required
- `frecuencia_objetivo`: Integer (1-7), required

**Response 201 (Created)**:
```json
{
  "id": 101,
  "nombre": "Exercise",
  "frecuencia_objetivo": 3,
  "usuario_id": 1,
  "created_at": "2026-09-27T10:35:00Z"
}
```

**Response Schema** (HabitoResponse):
- `id`: Integer
- `nombre`: String
- `frecuencia_objetivo`: Integer
- `usuario_id`: Integer (implicit from JWT; never accepted as input)
- `created_at`: ISO 8601 datetime

**Error 400 (Bad Request)**:
```json
{
  "detail": "frecuencia_objetivo must be between 1 and 7"
}
```

**Error 401 (Unauthorized)**:
```json
{
  "detail": "Not authenticated"
}
```

**Error 422 (Unprocessable Entity)**:
```json
{
  "detail": [
    {
      "loc": ["body", "nombre"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.string.too_short"
    }
  ]
}
```

**Notes**:
- `usuario_id` always taken from JWT token; input parameter ignored/rejected
- Frequencies outside [1, 7] are business rule error (400), not validation (422)
- Habit names are stored as-is; trimming optional (implementation detail)

---

### 4. GET /habitos/

**Purpose**: List all habits for the authenticated user with pagination.

**Auth**: [Auth required]

**Query Parameters**:
- `skip`: Integer, default 0 (offset for pagination)
- `limit`: Integer, default 20 (page size)

**Request Example**:
```http
GET /habitos/?skip=0&limit=10
Authorization: Bearer <JWT>
```

**Response 200 (OK)**:
```json
{
  "items": [
    {
      "id": 101,
      "nombre": "Exercise",
      "frecuencia_objetivo": 3,
      "usuario_id": 1,
      "created_at": "2026-09-27T10:35:00Z"
    },
    {
      "id": 102,
      "nombre": "Read",
      "frecuencia_objetivo": 7,
      "usuario_id": 1,
      "created_at": "2026-09-27T10:36:00Z"
    }
  ],
  "total": 2
}
```

**Response Schema** (HabitoListResponse):
- `items`: List of HabitoResponse objects
- `total`: Integer (total count, including skipped)

**Error 401 (Unauthorized)**:
```json
{
  "detail": "Not authenticated"
}
```

**Error 422 (Unprocessable Entity)**:
```json
{
  "detail": [
    {
      "loc": ["query", "skip"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```

**Notes**:
- Always filtered by `usuario_id` from JWT (no cross-user data leak)
- Pagination always applied; `skip` and `limit` are defaults if omitted
- Invalid pagination values (negative, non-integer) return 422

---

### 5. POST /habitos/{id}/marcar

**Purpose**: Mark a habit as completed for a specific date (or today if not specified).

**Auth**: [Auth required]

**Path Parameters**:
- `id`: Integer (habit ID)

**Request** (optional body):
```json
{
  "fecha": "2026-09-26"
}
```

Or empty body (defaults to today):
```json
{}
```

**Request Schema** (MarcaCreate):
- `fecha`: Date (YYYY-MM-DD format), optional, defaults to server's current date

**Response 201 (Created)**:
```json
{
  "id": 201,
  "habito_id": 101,
  "usuario_id": 1,
  "fecha": "2026-09-26",
  "created_at": "2026-09-27T10:40:00Z"
}
```

**Response Schema** (MarcaResponse):
- `id`: Integer
- `habito_id`: Integer
- `usuario_id`: Integer (from JWT)
- `fecha`: Date (YYYY-MM-DD)
- `created_at`: ISO 8601 datetime

**Error 400 (Bad Request)**:
```json
{
  "detail": "ya marcado ese día"
}
```
or
```json
{
  "detail": "fecha no puede ser posterior a la fecha actual"
}
```

**Error 401 (Unauthorized)**:
```json
{
  "detail": "Not authenticated"
}
```

**Error 404 (Not Found)**:
```json
{
  "detail": "Hábito no encontrado"
}
```

**Notes**:
- `usuario_id` taken from JWT; verifies ownership before marking
- Duplicate marks on same date (habito_id, fecha) → 400
- Future dates → 400 "fecha no puede ser posterior a la fecha actual" (FR-11a)
- Past dates (retroactive marking) are allowed
- Non-existent habit → 404 (never leaks whether habit exists to non-owner)

---

### 6. DELETE /habitos/{id}

**Purpose**: Delete a habit and all its associated marks.

**Auth**: [Auth required]

**Path Parameters**:
- `id`: Integer (habit ID)

**Request**:
```http
DELETE /habitos/101
Authorization: Bearer <JWT>
```

**Response 204 (No Content)**:
```
(empty body)
```

**Error 401 (Unauthorized)**:
```json
{
  "detail": "Not authenticated"
}
```

**Error 403 (Forbidden)**:
```json
{
  "detail": "Forbidden"
}
```

(Only if API explicitly identifies the resource as belonging to another user; standard practice for DELETE is to return 403 when user is authenticated but not owner)

**Error 404 (Not Found)**:
```json
{
  "detail": "Hábito no encontrado"
}
```

(Returned if habit doesn't exist OR doesn't belong to authenticated user, making it indistinguishable from non-existence)

**Notes**:
- Soft delete vs. hard delete: Specification allows cascading Marca deletion; implementation choice
- `usuario_id` verified before deletion; returns 403 if not owner, or 404 to avoid identity leak
- Habit must exist and belong to authenticated user

---

## Error Handling

All errors return appropriate HTTP status codes and JSON bodies:

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | GET successful |
| 201 | Created | POST /usuarios/, POST /habitos/, POST /habitos/{id}/marcar |
| 204 | No Content | DELETE /habitos/{id} successful |
| 400 | Bad Request | Business rule violation (duplicate mark, invalid frequency, future date) |
| 401 | Unauthorized | Missing/invalid JWT token |
| 403 | Forbidden | Authenticated but not authorized (not owner of resource) |
| 404 | Not Found | Habit doesn't exist or doesn't belong to user |
| 422 | Unprocessable Entity | Validation error (invalid email, out-of-range number, etc.) |
| 500 | Internal Server Error | Unhandled exception (never exposes stack trace; generic "Error interno del servidor") |

**Error Response Format** (generic 400/404/403):
```json
{
  "detail": "Error message"
}
```

**Error Response Format** (validation 422):
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "error message",
      "type": "error_type"
    }
  ]
}
```

---

## Security Notes

1. **Passwords**: Never logged, never returned in responses, hashed with bcrypt
2. **Ownership**: Enforced at service layer; usuario_id from JWT, never from input
3. **404 Strategy**: Non-existent or non-owned resources both return 404 to avoid enumeration
4. **Token Expiry**: Configurable; never infinite
5. **HTTPS**: Required in production (not enforced here, but assumed)

---

## Versioning

Current version: v1 (no version suffix in paths; versioning via Accept header or URL prefix optional for future)

---

**Contract Status**: Final. Ready for implementation and testing.
