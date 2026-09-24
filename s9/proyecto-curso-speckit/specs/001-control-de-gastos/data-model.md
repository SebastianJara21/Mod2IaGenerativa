# Data Model: Sistema de Control de Gastos

**Date**: 2026-09-23  
**Phase**: Phase 1 — Design & Contracts

---

## Overview

Two core entities: **Usuario** (authentication/authorization) and **Gasto** (expense records). Relationship: one-to-many (one usuario has many gastos). User isolation enforced via usuario_id foreign key (no cross-user data leaks).

---

## Entity: Usuario

### Purpose
Represents an authenticated user in the system. Stores identity and credentials (hashed).

### Fields

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | Integer (PK) | Auto-increment | Primary key |
| `email` | String(255) | Unique, not null, valid RFC 5321 | Used for login (case-insensitive comparison recommended) |
| `hashed_password` | String(255) | Not null | bcrypt hash; never plain text in DB or responses |
| `created_at` | DateTime | Not null, default=now | Audit trail |
| `updated_at` | DateTime | Not null, default=now, on update | Audit trail |

### SQLAlchemy Model

```python
# app/models/usuario.py
class Usuario(Base):
    __tablename__ = "usuarios"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship: Usuario → Gastos (one-to-many)
    gastos: Mapped[list["Gasto"]] = relationship("Gasto", back_populates="usuario")
```

### Pydantic Schemas

```python
# app/schemas/usuario.py

class UsuarioCreate(BaseModel):
    email: EmailStr
    password: str  # min 1 char (constitutional assumption)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@example.com",
                "password": "mi_contraseña_segura"
            }
        }

class UsuarioOut(BaseModel):
    id: int
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "usuario@example.com",
                "created_at": "2026-09-23T12:00:00Z"
            }
        }
    
    # Note: hashed_password NEVER exposed in responses
```

### Business Rules

1. **Email Uniqueness**: No two usuarios with same email (database unique constraint)
2. **Email Validation**: Must be valid RFC 5321 email (Pydantic EmailStr)
3. **Password Hashing**: Always hashed with bcrypt (passlib.context.CryptContext) before storage
4. **Password Never Exposed**: Hashed password never returned in API responses, logs, or error messages
5. **Created/Updated Audit**: Timestamps automatically managed; never user-supplied

---

## Entity: Gasto

### Purpose
Represents an expense record belonging to a usuario. Includes description, amount, and category with validation rules and category limits.

### Fields

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | Integer (PK) | Auto-increment | Primary key |
| `usuario_id` | Integer (FK) | Not null, references usuarios(id) | User ownership (isolation) |
| `descripcion` | String(255) | Not null, min 1 char | Expense description |
| `monto` | Decimal(10,2) | Not null, > 0 | Amount in local currency |
| `categoria` | Enum/String(50) | Not null, in ["comida", "transporte", "entretenimiento", "otros"] | Fixed set of categories |
| `created_at` | DateTime | Not null, default=now | Expense date (user cannot override) |
| `updated_at` | DateTime | Not null, default=now, on update | Audit trail |

### SQLAlchemy Model

```python
# app/models/gasto.py
from enum import Enum

class CategoriaEnum(str, Enum):
    COMIDA = "comida"
    TRANSPORTE = "transporte"
    ENTRETENIMIENTO = "entretenimiento"
    OTROS = "otros"

class Gasto(Base):
    __tablename__ = "gastos"
    __table_args__ = (
        ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    categoria: Mapped[CategoriaEnum] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship: Gasto → Usuario (many-to-one)
    usuario: Mapped[Usuario] = relationship("Usuario", back_populates="gastos")
```

### Pydantic Schemas

```python
# app/schemas/gasto.py
from enum import Enum

class CategoriaEnum(str, Enum):
    COMIDA = "comida"
    TRANSPORTE = "transporte"
    ENTRETENIMIENTO = "entretenimiento"
    OTROS = "otros"

class GastoCreate(BaseModel):
    descripcion: str = Field(..., min_length=1, max_length=255)
    monto: Decimal = Field(..., gt=0)  # > 0 (Decimal for financial precision)
    categoria: CategoriaEnum
    
    class Config:
        json_schema_extra = {
            "example": {
                "descripcion": "Comida en restaurante",
                "monto": "25.50",
                "categoria": "comida"
            }
        }

class GastoOut(BaseModel):
    id: int
    usuario_id: int  # Included for reference; always matches authenticated user
    descripcion: str
    monto: Decimal
    categoria: CategoriaEnum
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "usuario_id": 1,
                "descripcion": "Comida en restaurante",
                "monto": "25.50",
                "categoria": "comida",
                "created_at": "2026-09-23T12:00:00Z"
            }
        }
```

### Business Rules

1. **Descripción Required**: Not empty, max 255 chars
2. **Monto Validation**: Must be > 0 (Decimal type for financial precision, avoids float rounding issues)
3. **Categoría Fixed Set**: Only ["comida", "transporte", "entretenimiento", "otros"]
   - Invalid category → CategoriaInvalidaError (400 in HTTP, not 422)
4. **Límite por Categoría (Cumulative, No Reset)**:
   - Sum of all gastos for user in a category cannot exceed 500.0
   - Calculation: `total_por_categoria(db, usuario_id, categoria) + new_monto > 500.0` → LimiteExcedidoError (400)
   - Cumulative forever (no reset per month; per Compatibility Contract)
5. **Usuario Isolation**: usuario_id ALWAYS from JWT token (get_current_user), NEVER from request body/URL/query
   - Any query filtering gastos MUST include `WHERE usuario_id = <authenticated_user_id>`
   - Violating this rule = security breach (Article IV.4)
6. **Created Audit**: created_at set to current timestamp when gasto is created; user cannot override
7. **No Update/Delete in Scope**: Only create and read in this feature; update/delete are future features

---

## Relationships

### Usuario ↔ Gasto

```
Usuario (1) ──── (Many) Gasto
  id (PK)           usuario_id (FK)
  
Cascade delete: If usuario deleted, all gastos deleted
```

### Cardinality Ratios

- One usuario can have 0 to many gastos
- Each gasto belongs to exactly one usuario
- No gasto can exist without a usuario

---

## Validation Rules Summary

| Constraint | Enforced At | Error Type | HTTP Status |
|-----------|------------|-----------|------------|
| Email uniqueness | Database (UNIQUE) | IntegrityError → 400 | 400 |
| Email validity | Pydantic (EmailStr) | ValidationError | 422 |
| Password present | Pydantic | ValidationError | 422 |
| Descripción non-empty | Pydantic (min_length=1) | ValidationError | 422 |
| Monto > 0 | Pydantic (gt=0) | ValidationError | 422 |
| Categoría in enum | Pydantic (CategoriaEnum) | ValidationError | 422 |
| Categoría in business set | Service (validar_categoria) | CategoriaInvalidaError | 400 |
| Límite ≤ 500 | Service (registrar_gasto) | LimiteExcedidoError | 400 |
| Usuario isolation | Router/Service (get_current_user) | 403 (if different user's ID passed) | 403 |

---

## State Transitions

### Usuario
- **Created** → **Active** (on registration)
- **Active** → **Inactive** (future feature; not in scope)

### Gasto
- **Created** → **Recorded** (on POST /gastos/ success)
- **Recorded** → **[end of scope]** (no update/delete in v1)

---

## Database Schema

### Alembic Migration (auto-generated by SQLAlchemy)

```sql
-- Pseudo-SQL; actual migration generated by alembic upgrade head
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE gastos (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    usuario_id INTEGER NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    CHECK (monto > 0),
    CHECK (categoria IN ('comida', 'transporte', 'entretenimiento', 'otros'))
);

CREATE INDEX idx_gastos_usuario_id ON gastos(usuario_id);
CREATE INDEX idx_gastos_categoria ON gastos(usuario_id, categoria);
```

---

## Testing Data Model

### RepositorioFalso (for unit tests)

```python
# tests/test_gastos.py
class RepositorioFalso:
    """Fake repository for unit testing services without database."""
    
    def __init__(self):
        self.gastos = {}  # {(usuario_id, gasto_id): gasto_dict}
        self.usuarios = {}
    
    def guardar(self, db, usuario_id, descripcion, monto, categoria) -> dict:
        """Stores a gasto in memory; returns dict with id."""
        gasto_id = max([k[1] for k in self.gastos.keys()] or [0]) + 1
        gasto = {
            "id": gasto_id,
            "usuario_id": usuario_id,
            "descripcion": descripcion,
            "monto": monto,
            "categoria": categoria,
            "created_at": datetime.utcnow()
        }
        self.gastos[(usuario_id, gasto_id)] = gasto
        return gasto
    
    def total_por_categoria(self, db, usuario_id, categoria) -> float:
        """Returns sum of gastos for user in category."""
        return sum(
            g["monto"] for g in self.gastos.values()
            if g["usuario_id"] == usuario_id and g["categoria"] == categoria
        )
    
    def listar(self, db, usuario_id, skip=0, limit=20) -> list[dict]:
        """Returns paginated gastos for user."""
        user_gastos = [g for g in self.gastos.values() if g["usuario_id"] == usuario_id]
        return user_gastos[skip:skip+limit]
```

---

## Coverage by Phase

- **Phase 0 (Research)**: Technology rationales, compatibility contracts
- **Phase 1 (Design)**: This document — entity definitions, relationships, validation
- **Phase 2 (Tasks)**: `/speckit-tasks` generates task breakdown
- **Phase 3 (Implement)**: Code generation, testing, coverage validation
