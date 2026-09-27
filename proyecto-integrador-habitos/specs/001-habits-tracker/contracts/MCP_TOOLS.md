# MCP Tools Contract: Personal Habits Tracker

## Overview

MCP (Model Context Protocol) tools provide programmatic access to habit tracking functionality via the official "mcp" SDK with streamable-http transport. All tools operate on the authenticated user in the MCP session; no cross-user access or impersonation is supported.

Each tool duplicates the behavior of its corresponding REST endpoint (see contracts/REST_API.md) but in a tool-friendly format.

---

## Authentication

Tools authenticate the user via JWT token passed in the MCP session context (extracted from the `Authorization` header during HTTP request). The `get_current_user` function is reused to verify the JWT and extract `usuario_id`.

If authentication fails or token is missing/invalid → error response with message "Not authenticated".

---

## Tools

### 1. crear_habito

**Description**: Create a new habit for the authenticated user with a target frequency.

**Parameters**:
- `nombre` (string, required): Name of the habit (1-255 characters, non-empty)
- `frecuencia_objetivo` (integer, required): Target frequency in days per week (1-7 inclusive)

**Success Response**:
```json
{
  "id": 101,
  "nombre": "Exercise",
  "frecuencia_objetivo": 3,
  "usuario_id": 1,
  "created_at": "2026-09-27T10:35:00Z"
}
```

**Error Response** (duplicate name or similar):
```json
{
  "error": "nombre ya existe para este usuario"
}
```

**Error Response** (frequency out of range):
```json
{
  "error": "frecuencia_objetivo must be between 1 and 7"
}
```

**Error Response** (authentication failure):
```json
{
  "error": "Not authenticated"
}
```

**Equivalence**: Identical to `POST /habitos/` (REST endpoint)

**Notes**:
- `usuario_id` is always taken from the authenticated session; input parameter is ignored
- Frequencies outside [1, 7] are business logic errors (not validation errors)
- Habit name must be non-empty; validation errors are returned as structured format

---

### 2. marcar_habito

**Description**: Mark a habit as completed for a specific date (or today if not specified). Retroactive marking (past dates) is allowed; future dates are rejected.

**Parameters**:
- `habito_id` (integer, required): ID of the habit to mark
- `fecha` (string, optional): Date in YYYY-MM-DD format. Defaults to server's current date if omitted.

**Success Response**:
```json
{
  "id": 201,
  "habito_id": 101,
  "usuario_id": 1,
  "fecha": "2026-09-26",
  "created_at": "2026-09-27T10:40:00Z"
}
```

**Error Response** (duplicate mark on same date):
```json
{
  "error": "ya marcado ese día"
}
```

**Error Response** (future date):
```json
{
  "error": "fecha no puede ser posterior a la fecha actual"
}
```

**Error Response** (habit not found or not owned):
```json
{
  "error": "Hábito no encontrado"
}
```

**Error Response** (authentication failure):
```json
{
  "error": "Not authenticated"
}
```

**Equivalence**: Identical to `POST /habitos/{id}/marcar` (REST endpoint)

**Notes**:
- `usuario_id` is inferred from authentication; not accepted as input
- Duplicate marks on the same date are rejected (400-level error)
- Future dates are rejected per FR-11a
- Retroactive marking (past dates) is allowed
- If habit doesn't exist or belongs to another user → "Hábito no encontrado" (security)

---

### 3. listar_habitos

**Description**: List all habits for the authenticated user with pagination support.

**Parameters**:
- `skip` (integer, optional): Offset for pagination. Defaults to 0.
- `limit` (integer, optional): Maximum number of habits to return. Defaults to 20.

**Success Response**:
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

**Error Response** (invalid pagination):
```json
{
  "error": "skip and limit must be non-negative integers"
}
```

**Error Response** (authentication failure):
```json
{
  "error": "Not authenticated"
}
```

**Equivalence**: Identical to `GET /habitos/?skip=X&limit=Y` (REST endpoint)

**Notes**:
- Always filtered by authenticated user's `usuario_id`
- Pagination defaults: `skip=0`, `limit=20`
- `total` includes all habits, not just the returned page
- No cross-user data leak possible

---

### 4. eliminar_habito

**Description**: Delete a habit and all associated marks. **Requires explicit server-side confirmation before execution** to prevent accidental data loss.

**Parameters**:
- `habito_id` (integer, required): ID of the habit to delete

**Confirmation Flow** (2-step process):

**Step 1 - Request with confirmation=false (or omitted)**:
```json
{
  "habito_id": 101
}
```

**Step 1 - Server Response** (confirmation prompt):
```json
{
  "status": "confirmation_required",
  "message": "¿Confirmar eliminación del hábito 'Exercise'? Se eliminarán también todos los registros (marcas) asociados.",
  "habit_name": "Exercise",
  "habit_id": 101
}
```

**Step 2 - Confirmed Request**:
```json
{
  "habito_id": 101,
  "confirm": true
}
```

**Step 2 - Success Response**:
```json
{
  "status": "deleted",
  "id": 101,
  "message": "Hábito 'Exercise' eliminado."
}
```

**Error Response** (habit not found or not owned):
```json
{
  "error": "Hábito no encontrado"
}
```

**Error Response** (authentication failure):
```json
{
  "error": "Not authenticated"
}
```

**Equivalence**: Corresponds to `DELETE /habitos/{id}` (REST endpoint) with explicit server-side confirmation (not client-side)

**Notes**:
- **Server-side confirmation**: The MCP server requires an explicit `confirm: true` parameter before executing deletion; the Claude model cannot decide unilaterally
- No soft delete requirement; hard delete is acceptable
- Cascades to delete all associated Marca records
- Ownership verified before deletion
- Returns 404 if habit doesn't exist or belongs to another user

---

## Error Format

All tools return errors in a consistent format:

```json
{
  "error": "<error message>"
}
```

Error messages are specific and actionable (e.g., "ya marcado ese día", not generic "Error").

For validation errors (schema-level), errors may include structured details:

```json
{
  "error": "Validation failed",
  "details": [
    {
      "field": "frecuencia_objetivo",
      "message": "must be between 1 and 7"
    }
  ]
}
```

---

## Transport

- **Protocol**: streamable-http (part of official mcp SDK)
- **Auth**: JWT extracted from Authorization header in HTTP context
- **Format**: JSON request/response

---

## Security Notes

1. **User Isolation**: All tools operate only on authenticated user's data; no cross-user access
2. **Ownership Verification**: Every tool verifies that the resource (habit, mark) belongs to the authenticated user
3. **Confirmation**: Destructive operations (delete) require explicit server-side confirmation
4. **Error Messages**: Avoid leaking information; non-existent or unauthorized resources return generic "not found"

---

## Tool Usage Examples

### Example 1: Create a habit

```
Tool: crear_habito
Parameters: {
  "nombre": "Meditate",
  "frecuencia_objetivo": 7
}

Response: {
  "id": 105,
  "nombre": "Meditate",
  "frecuencia_objetivo": 7,
  "usuario_id": 1,
  "created_at": "2026-09-27T11:00:00Z"
}
```

### Example 2: Mark a habit for today

```
Tool: marcar_habito
Parameters: {
  "habito_id": 101
}

Response: {
  "id": 202,
  "habito_id": 101,
  "usuario_id": 1,
  "fecha": "2026-09-27",
  "created_at": "2026-09-27T11:05:00Z"
}
```

### Example 3: Mark a habit for yesterday (retroactive)

```
Tool: marcar_habito
Parameters: {
  "habito_id": 101,
  "fecha": "2026-09-26"
}

Response: {
  "id": 203,
  "habito_id": 101,
  "usuario_id": 1,
  "fecha": "2026-09-26",
  "created_at": "2026-09-27T11:05:30Z"
}
```

### Example 4: Delete a habit (with confirmation)

```
Tool: eliminar_habito
Parameters: {
  "habito_id": 101
}

Response (Step 1): {
  "status": "confirmation_required",
  "message": "¿Confirmar eliminación del hábito 'Exercise'? Se eliminarán también todos los registros (marcas) asociados.",
  "habit_name": "Exercise",
  "habit_id": 101
}

[User provides confirmation]

Tool: eliminar_habito
Parameters: {
  "habito_id": 101,
  "confirm": true
}

Response (Step 2): {
  "status": "deleted",
  "id": 101,
  "message": "Hábito 'Exercise' eliminado."
}
```

---

**Contract Status**: Final. Ready for implementation and integration with MCP server.
