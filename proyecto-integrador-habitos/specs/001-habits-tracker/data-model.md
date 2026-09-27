# Data Model: Personal Habits Tracker

## Entity Relationship Diagram (ERD)

```
┌─────────────┐
│   Usuario   │
├─────────────┤
│ id (PK)     │
│ email (UQ)  │
│ password_hash
│ created_at  │
└────────┬────┘
         │ 1
         │
         │ N
    ┌────┴────────────┐
    │                 │
    ▼                 ▼
┌──────────┐      ┌─────────┐
│  Habito  │      │  Marca  │
├──────────┤      ├─────────┤
│ id (PK)  │      │ id (PK) │
│ usuario_ │      │ habito_ │
│   id(FK) │◄─────┤   id(FK)│
│ nombre   │      │ usuario_│
│ frecuen- │      │   id(FK)│
│   cia_   │      │ fecha   │
│ objetivo │      │ created_│
│ created_ │      │   at    │
│   at     │      └─────────┘
└──────────┘

Relationships:
- Usuario 1:N Habito (FK: Habito.usuario_id → Usuario.id)
- Habito 1:N Marca (FK: Marca.habito_id → Habito.id)
- Usuario 1:N Marca (FK: Marca.usuario_id → Usuario.id) [denormalization for ownership queries]
```

---

## Entity: Usuario

**Purpose**: Represents an authenticated user account. All habits and marks belong to a usuario.

**Fields**:

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | Integer | PRIMARY KEY, AUTO INCREMENT | Unique user identifier |
| email | String (254) | UNIQUE, NOT NULL | Email address (validated by pydantic.EmailStr) |
| password_hash | String (255) | NOT NULL | Hashed password (bcrypt output, ~60 chars) |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Account creation timestamp (UTC) |

**Validation Rules**:
- `email`: Non-empty, valid email format (RFC 5322, per pydantic.EmailStr), globally unique
- `password_hash`: Non-empty, output of passlib bcrypt hash (minimum 60 characters)
- `created_at`: Automatically set to server time at creation; immutable

**Lifecycle**:
- Created: POST /usuarios/ (only operation)
- Read: Identified via JWT token (usuario_id extracted from token)
- Update: Not supported in v1
- Delete: Cascade deletes Habito and Marca (out of scope for v1 but noted for schema design)

**Denormalization/Indexes**:
- INDEX on `email` (used by GET /usuarios/token authentication flow)

---

## Entity: Habito

**Purpose**: Represents a personal goal (habit) that a user tracks. Each habit has a target frequency (days per week) that users attempt to meet.

**Fields**:

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | Integer | PRIMARY KEY, AUTO INCREMENT | Unique habit identifier |
| usuario_id | Integer | FOREIGN KEY (Usuario.id), NOT NULL | Owner of this habit |
| nombre | String (255) | NOT NULL | Habit name/description (e.g., "Exercise") |
| frecuencia_objetivo | Integer | NOT NULL, CHECK (1-7) | Target days per week (1=min, 7=daily) |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Habit creation timestamp (UTC) |

**Validation Rules**:
- `usuario_id`: Must reference existing Usuario; no NULL
- `nombre`: Non-empty string (1-255 chars), trimmed, no leading/trailing whitespace
- `frecuencia_objetivo`: Integer in range [1, 7] (inclusive); error 400 if out of range
- `created_at`: Automatically set at creation; immutable

**Lifecycle**:
- Created: POST /habitos/ (requires authentication, usuario_id from JWT)
- Read: GET /habitos/ (filtered by usuario_id from JWT, paginated)
- Mark: POST /habitos/{id}/marcar (creates Marca entry, requires ownership verification)
- Delete: DELETE /habitos/{id} (requires ownership, cascades Marca deletion)
- Update: Not supported in v1 (frecuencia_objetivo immutable; to change, delete + recreate)

**Ownership Enforcement**:
- All queries include `WHERE usuario_id = <current_user_id>` (from JWT)
- No endpoint accepts `usuario_id` as input parameter
- DELETE operation verifies ownership before deletion

**Denormalization/Indexes**:
- INDEX on `(usuario_id, created_at)` for efficient listing with pagination

---

## Entity: Marca

**Purpose**: Records a single completion event for a habit on a specific date. Enables retroactive marking (past dates) and prevents duplicate marks on the same day.

**Fields**:

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | Integer | PRIMARY KEY, AUTO INCREMENT | Unique mark identifier |
| habito_id | Integer | FOREIGN KEY (Habito.id), NOT NULL | Reference to habit being marked |
| usuario_id | Integer | FOREIGN KEY (Usuario.id), NOT NULL | Cache of habit's owner (denormalization) |
| fecha | Date | NOT NULL | Date on which habit was completed (YYYY-MM-DD, no time) |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Server timestamp when mark was recorded (UTC) |

**Validation Rules**:
- `habito_id`: Must reference existing Habito; no NULL
- `usuario_id`: Must match Habito.usuario_id; no NULL (denormalization for ownership queries)
- `fecha`: 
  - Must be a valid date (YYYY-MM-DD format)
  - Must be ≤ today (server's current date) — **FR-11a: No future dates allowed**
  - Retroactive marking (past dates) is allowed
  - Error 400 if fecha is in the future: "fecha no puede ser posterior a la fecha actual"
- `created_at`: Automatically set at creation; immutable
- **Unique Constraint**: UNIQUE(habito_id, fecha) — prevent duplicate marks on same habit for same day

**Lifecycle**:
- Created: POST /habitos/{id}/marcar (requires ownership + fecha validation)
- Read: Included in GET /habitos/ response (aggregated marks for each habit, or separate endpoint)
- Delete: Cascade deleted when Habito is deleted; no direct delete endpoint in v1
- Update: Not supported; to correct, delete + recreate

**Ownership Enforcement**:
- usuario_id denormalized from Habito for efficient queries
- All mark operations verify ownership via JWT usuario_id
- Queries filtered by (habito_id, usuario_id)

**Denormalization/Indexes**:
- INDEX on `(habito_id, fecha)` for duplicate check (UNIQUE constraint enforces)
- INDEX on `(usuario_id, fecha)` for querying user's marks across all habits

---

## State Transitions

### Usuario State Machine

```
[Unregistered] 
    │ POST /usuarios/ (create)
    ▼
[Registered] ◄────── (no state changes in v1)
    │ (implicit: authorized via JWT token)
```

### Habito State Machine

```
[Not Exists]
    │ POST /habitos/ (create)
    ▼
[Active] ◄────── (immutable; no state transitions except deletion)
    │ DELETE /habitos/ (delete)
    ▼
[Deleted] (cascade deletes Marca)
```

### Marca State Machine

```
[Not Created]
    │ POST /habitos/{id}/marcar (create)
    ▼
[Recorded] ◄────── (immutable; no state changes except deletion)
    │ (implicit: when Habito deleted)
    ▼
[Deleted] (cascade)
```

---

## Constraints Summary

| Constraint | Scope | Enforcement | Rationale |
|-----------|-------|-------------|-----------|
| email UNIQUE | Usuario | DB + validation | Prevent duplicate accounts |
| usuario_id FK | Habito, Marca | DB | Referential integrity |
| frecuencia_objetivo ∈ [1,7] | Habito | Validation (FR-007) | Business rule |
| nombre non-empty | Habito | Validation (FR-006) | Usability |
| fecha ≤ today | Marca | Validation (FR-11a) | Business rule (no future marking) |
| (habito_id, fecha) UNIQUE | Marca | DB | Prevent duplicate marks |
| usuario_id ownership | All queries | Service + Router | Security (Artículo IV) |

---

## Schema Notes

**SQLAlchemy ORM Models Location**: `app/models/`
- `app/models/usuario.py`: Usuario model definition
- `app/models/habito.py`: Habito + Marca model definitions (can be combined)

**Alembic Versioning**: `migrations/versions/`
- Initial migration: Creates Usuario, Habito, Marca tables with constraints and indexes
- No schema updates planned for v1 (entities fixed)

**Database Compatibility**:
- SQLite (development): `:memory:` for tests, file-based for local dev
- PostgreSQL (production): Full ACID compliance, concurrent connections
- No database-specific SQL used; SQLAlchemy abstracts differences

---

## Example Queries (SQLAlchemy ORM)

```python
# Get all habits for a user (paginated)
habitos = db.query(Habito).filter(Habito.usuario_id == usuario_id).offset(skip).limit(limit).all()

# Get marks for a habit on a specific date
marca = db.query(Marca).filter(
    Marca.habito_id == habito_id,
    Marca.usuario_id == usuario_id,
    Marca.fecha == fecha
).first()

# Check for duplicate mark (before creating new Marca)
existing = db.query(Marca).filter(
    Marca.habito_id == habito_id,
    Marca.fecha == fecha
).first()
if existing:
    raise BusinessError("ya marcado ese día")

# Get all marks for a habit (for stats/charts, future)
marks = db.query(Marca).filter(Marca.habito_id == habito_id).all()
```

---

**Schema Status**: Ready for implementation. All entities, constraints, and relationships defined. No ambiguities remaining.
