# REST API Contract: Sistema de Control de Gastos

**Date**: 2026-09-23  
**Base URL**: `http://localhost:8000` (development) or configured production domain  
**Version**: 1.0.0

---

## Overview

Public REST API exposed by FastAPI. Authentication via JWT (Bearer token). All responses include appropriate HTTP status codes and error structures. No CORS, cookies, or session-based auth.

---

## Authentication

### Bearer Token (JWT)

All protected endpoints require an `Authorization` header with a valid JWT:

```
Authorization: Bearer <access_token>
```

**Token Type**: JWT (HS256-signed)  
**Expiry**: Configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` (.env); never infinite  
**Refresh**: Not supported in v1 (future feature)

---

## Endpoints

### 1. Register User — `POST /usuarios/`

**Authentication**: None (public)

**Request**: `{"email": "user@example.com", "password": "secure_password"}`

**Success** (201): `{"id": 1, "email": "user@example.com", "created_at": "2026-09-23T12:00:00Z"}`

**Errors**: 400 (email duplicado), 422 (validation)

---

### 2. Authenticate — `POST /usuarios/token`

**Authentication**: None (public)

**Request** (form): `username=user@example.com&password=secure_password`

**Success** (200): `{"access_token": "eyJ...", "token_type": "bearer"}`

**Errors**: 401 (invalid credentials), 422 (validation)

---

### 3. Register Expense — `POST /gastos/`

**Authentication**: Required (Bearer JWT)

**Request**: `{"descripcion": "text", "monto": 25.50, "categoria": "comida"}`

**Success** (201): `{"id": 1, "usuario_id": 1, "descripcion": "text", "monto": 25.50, "categoria": "comida", "created_at": "2026-09-23T12:00:00Z"}`

**Errors**: 401 (auth), 400 (categoría inválida, límite excedido), 422 (validation), 500 (server error)

---

### 4. List Expenses — `GET /gastos/?skip=0&limit=20`

**Authentication**: Required (Bearer JWT)

**Query Params**: `skip` (default 0), `limit` (default 20)

**Success** (200): Array of gasto objects

**Errors**: 401 (auth), 422 (invalid skip/limit)

---

## Status Codes

| Code | Meaning | Used When |
|------|---------|-----------|
| 200 | OK | List/read succeed |
| 201 | Created | User/expense created |
| 400 | Bad Request | Business rule violation (invalid category, limit exceeded) |
| 401 | Unauthorized | Missing/invalid JWT |
| 422 | Unprocessable Entity | Schema validation failure |
| 500 | Server Error | Unhandled exception |

---

## Data Types

- **Email**: RFC 5321 format (EmailStr validation)
- **Monto**: Decimal > 0 (e.g., 25.50)
- **Categoría**: One of ["comida", "transporte", "entretenimiento", "otros"] (case-sensitive)
- **Timestamp**: ISO 8601 UTC (e.g., 2026-09-23T12:00:00Z)

---

## Constraints

1. **User Isolation**: Each user only sees their own expenses
2. **Category Limit**: Cumulative per category per user ≤ 500.0
3. **No Updates/Deletes**: v1 supports only CREATE (POST) and READ (GET)
4. **Password Never Exposed**: Never in responses or logs

---

## Pagination

- `skip`: Offset from beginning (0-indexed)
- `limit`: Max records to return
- Default: skip=0, limit=20
- Returns only user's expenses (filtered by JWT)

---

## Error Examples

### Invalid Category (400)
```json
{"detail": "categoría inválida"}
```

### Limit Exceeded (400)
```json
{"detail": "límite excedido"}
```

### Schema Validation (422)
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

### Internal Error (500)
```json
{"detail": "Error interno del servidor"}
```

Details logged internally, never exposed to client.
