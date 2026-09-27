# Feature Specification: Personal Habits Tracker

**Feature Branch**: `001-habits-tracker`

**Created**: 2026-09-27

**Status**: Draft

**Input**: Personal habit tracking system with user authentication, habit creation, daily marking, and enforcement of frequency objectives.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Registration and Authentication (Priority: P1)

A user creates an account with email and password, then logs in to obtain a session token.

**Why this priority**: Authentication is the foundation; no other functionality is accessible without it. Every user must be able to register and log in.

**Independent Test**: Can be tested by registering a new user, logging in with credentials, and verifying token issuance. Delivers foundational access control.

**Acceptance Scenarios**:

1. **Given** no account exists for email "user@example.com", **When** POST /usuarios/ with email and password, **Then** 201 response with user object (password never exposed).
2. **Given** account exists with email "user@example.com", **When** POST /usuarios/ with same email, **Then** 400 error "email duplicado".
3. **Given** account exists with correct password, **When** POST /usuarios/token with email and password, **Then** 200 response with valid JWT token.
4. **Given** account exists with wrong password, **When** POST /usuarios/token, **Then** 401 error "credenciales inválidas".

---

### User Story 2 - Create and List Habits (Priority: P1)

A user creates habits with a name and frequency objective (days per week), then views their habit list.

**Why this priority**: Core feature; user must be able to define habits before marking them. Listing enables tracking progress.

**Independent Test**: Can be tested by creating a habit with valid name and frequency, retrieving the list, and verifying the habit appears. Delivers the ability to define personal goals.

**Acceptance Scenarios**:

1. **Given** user is authenticated and has no habits, **When** POST /habitos/ with name="Exercise" and frecuencia_objetivo=3, **Then** 201 response with Habito object containing id, name, frequency, usuario_id.
2. **Given** user is authenticated and has 2 habits, **When** GET /habitos/ with skip=0 and limit=10, **Then** 200 response with list of 2 habits (ordered, paginated).
3. **Given** user is authenticated, **When** POST /habitos/ with name="" (empty), **Then** 422 validation error.
4. **Given** user is authenticated, **When** POST /habitos/ with frecuencia_objetivo=0 or 8, **Then** 400 error "frecuencia_objetivo must be between 1 and 7".
5. **Given** user is unauthenticated, **When** POST /habitos/ with valid data, **Then** 401 error "authentication required".

---

### User Story 3 - Mark Daily Habit Completion (Priority: P1)

A user marks a habit as completed for a given date, recording progress toward their frequency objective.

**Why this priority**: Core value; marking habits is the primary user interaction. Must prevent duplicate marks on same day.

**Independent Test**: Can be tested by marking a habit with a specific date, verifying the mark record is created, and attempting a duplicate mark to confirm rejection. Delivers progress tracking.

**Acceptance Scenarios**:

1. **Given** user is authenticated and habit exists, **When** POST /habitos/{id}/marcar with fecha="2026-09-27", **Then** 201 response with Marca object (habito_id, fecha, created_at).
2. **Given** user is authenticated and habit is already marked on "2026-09-27", **When** POST /habitos/{id}/marcar with fecha="2026-09-27", **Then** 400 error "ya marcado ese día".
3. **Given** user is authenticated and habit exists, **When** POST /habitos/{id}/marcar without fecha (default today), **Then** 201 response with Marca using today's date.
4. **Given** user is authenticated, **When** POST /habitos/{id}/marcar for non-existent id, **Then** 404 error.
5. **Given** user is authenticated and owns Habit A, **When** POST /habitos/{habitoB_id}/marcar (habitoB belongs to another user), **Then** 404 error (appears non-existent to prevent identity leakage).

---

### User Story 4 - Delete a Habit (Priority: P2)

A user deletes a habit to stop tracking it. Deletion requires confirmation to prevent accidents.

**Why this priority**: Important for data management but not blocking core tracking. Requires explicit confirmation to avoid destructive mistakes.

**Independent Test**: Can be tested by deleting a habit with confirmation and verifying it no longer appears in the list. Delivers cleanup capability.

**Acceptance Scenarios**:

1. **Given** user is authenticated and owns a habit, **When** DELETE /habitos/{id}, **Then** 204 No Content response (habit removed).
2. **Given** user is authenticated and owns a habit, **When** MCP tool `eliminar_habito` is called, **Then** tool requests explicit confirmation before executing deletion.
3. **Given** user is authenticated but does not own a habit, **When** DELETE /habitos/{other_user_habit_id}, **Then** 403 Forbidden (explicit rejection for identified resource).
4. **Given** user is authenticated, **When** DELETE /habitos/{non_existent_id}, **Then** 404 error.

---

### Edge Cases

- How does the system handle leap year dates? (Assumption: standard date handling, no special rules)
- What if frequency_objetivo is changed after marks have been recorded? (Assumption: frequency is not editable in v1; to change, delete and recreate)
- What if a user deletes an account? (Assumption: out of scope for v1; handled separately via user management)

## Business Rules *(mandatory)*

**Date Restrictions for Marks:**
- A mark's fecha (date) cannot be in the future relative to the server's current date. Attempting to mark a habit with a future date MUST return a 400 error "fecha no puede ser posterior a la fecha actual" (date cannot be later than today).
- Marking a habit with a past date (retroactive marking) IS allowed — users may record that they completed a habit on a previous day if they forgot to mark it immediately.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow unauthenticated users to register via POST /usuarios/ (email, password → 201 with user object)
- **FR-002**: System MUST reject duplicate email registrations (400 "email duplicado")
- **FR-003**: System MUST authenticate users via POST /usuarios/token with email/password (form-encoded) returning JWT
- **FR-004**: System MUST validate JWT tokens and enforce 401 on missing/invalid authentication
- **FR-005**: System MUST allow authenticated users to create habits (POST /habitos/ with nombre, frecuencia_objetivo)
- **FR-006**: System MUST validate nombre is non-empty (422 validation error)
- **FR-007**: System MUST validate frecuencia_objetivo is integer between 1 and 7 inclusive (400 error if invalid)
- **FR-008**: System MUST list user's habits via GET /habitos/ with skip/limit pagination (200 response)
- **FR-009**: System MUST mark a habit as completed for a date via POST /habitos/{id}/marcar (201 Marca object)
- **FR-010**: System MUST prevent duplicate marks on the same habit for the same day (400 "ya marcado ese día")
- **FR-011**: System MUST default marca date to today if not provided
- **FR-011a**: System MUST reject marks with a fecha (date) in the future (later than server's current date) with 400 error "fecha no puede ser posterior a la fecha actual"; marks with past dates are allowed (retroactive marking)
- **FR-012**: System MUST enforce ownership: any operation (view, mark, delete) on a habit MUST verify usuario_id from JWT matches
- **FR-013**: System MUST delete a habit via DELETE /habitos/{id} (204 No Content)
- **FR-014**: System MUST return 404 for non-existent habits (never leak that habit exists to non-owner)
- **FR-015**: System MUST return 401 for unauthenticated requests to protected endpoints
- **FR-016**: MCP tool `crear_habito(nombre, frecuencia_objetivo)` MUST behave identically to POST /habitos/
- **FR-017**: MCP tool `marcar_habito(habito_id, fecha)` MUST behave identically to POST /habitos/{id}/marcar
- **FR-018**: MCP tool `listar_habitos(skip=0, limit=20)` MUST behave identically to GET /habitos/
- **FR-019**: MCP tool `eliminar_habito(habito_id)` MUST request explicit server-side confirmation before deletion
- **FR-020**: System MUST never expose password fields in responses (all user objects omit password)

### Key Entities

- **Usuario**: email (unique), password_hash (never exposed), created_at. Represents an authenticated user account.
- **Habito**: nombre (non-empty string), frecuencia_objetivo (1–7 integer), usuario_id (FK), created_at. Represents a personal goal to be tracked.
- **Marca**: habito_id (FK), fecha (date), usuario_id (FK), created_at. Represents a single completion event for a habit on a specific date.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can register and log in within 2 interactions, obtaining a valid JWT token
- **SC-002**: Authenticated users can create a habit within 1 API call with correct field validation
- **SC-003**: Users cannot mark the same habit twice on the same day (system rejects with 400 error)
- **SC-004**: Users can list their habits with pagination (skip/limit) in under 1 second
- **SC-005**: Users cannot access, modify, or delete another user's habits (ownership enforced for all operations)
- **SC-006**: API returns appropriate HTTP status codes and error messages (401, 404, 400, 422) as specified
- **SC-007**: All MCP tools produce identical behavior to their corresponding REST endpoints
- **SC-008**: Deletion of habits requires explicit confirmation (MCP server-side, no accidental data loss)

## Explicit Error Cases *(mandatory testing)*

These specific error scenarios must have dedicated tests:

1. Marcar the same habit as completed twice on the same day → 400 "ya marcado ese día"
2. Create a habit with frecuencia_objetivo outside range (0, 8, or invalid) → 400 "frecuencia_objetivo must be between 1 and 7"
3. List or create habits without valid JWT token → 401 "authentication required"
4. Attempt to delete or mark a habit belonging to another user by passing their habit's id → 404 (appears non-existent to prevent ownership leakage); OR 403 if the API explicitly identifies the resource but denies access
5. Mark or delete a non-existent habit → 404 "not found"
6. Marcar a habit with a fecha (date) in the future → 400 "fecha no puede ser posterior a la fecha actual" (date cannot be later than today)

## Assumptions

- **Authentication method**: Users authenticate via email/password; JWT tokens are valid for a configurable duration (never infinite).
- **Time zone handling**: Dates are handled as date-only (no time component); system assumes user's local timezone or UTC (implementation detail for v1).
- **Frequency immutability**: Habits cannot be edited after creation in v1; to change frequency, user deletes and recreates.
- **Mark history**: All marks are retained indefinitely; no automatic purging or archival.
- **Concurrency**: System assumes low concurrent user load; scaling concerns (caching, database optimization) are out of scope for v1.
- **MCP session identity**: MCP tools always operate on the authenticated user in the MCP session; no cross-user impersonation is supported.
- **Email validation**: Email addresses are validated as non-empty strings in v1; no confirmation email or double opt-in required.
- **Error visibility**: Unauthenticated or unauthorized users see generic 404/401 errors; internal errors return 500 with generic message (never stack traces).
