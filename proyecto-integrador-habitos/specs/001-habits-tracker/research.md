# Research Artifacts: Personal Habits Tracker

## Technology Integration Research

### 1. pyjwt + passlib[bcrypt] Integration

**Decision**: Use pyjwt (PyJWT 2.8+) for JWT signing/verification with HS256, combined with passlib 1.7.4 + bcrypt<4.1 for password hashing.

**Rationale**: 
- PyJWT is the official, standard JWT library for Python; single library avoids decision paralysis
- passlib with bcrypt is industry standard for password hashing; CryptContext(schemes=["bcrypt"]) ensures single scheme
- bcrypt<4.1 constraint: passlib 1.7.4 has runtime compatibility issues with bcrypt 4.1+, so pin bcrypt <4.1

**Implementation Pattern**:
```python
from passlib.context import CryptContext
from pyjwt import encode, decode

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In services/usuarios.py
def crear_usuario(email: str, password: str):
    hashed = pwd_context.hash(password)
    # Save Usuario(email=email, password_hash=hashed)

def autenticar_usuario(email: str, password: str) -> str:
    usuario = get from DB
    if pwd_context.verify(password, usuario.password_hash):
        token = encode({"sub": usuario.id}, SECRET_KEY, algorithm="HS256")
        return token
```

**Alternatives Considered**:
- argon2: More modern, but requires additional dependency (argon2-cffi); bcrypt adequate for v1
- Multiple schemes in CryptContext: Complexity without benefit; single bcrypt scheme sufficient

---

### 2. pydantic_settings.BaseSettings for .env

**Decision**: Use pydantic_settings.BaseSettings to load SECRET_KEY, DATABASE_URL, ACCESS_TOKEN_EXPIRE_MINUTES from .env file at startup.

**Rationale**:
- Pydantic v2 best practice; integrates naturally with FastAPI dependency injection
- Prevents accidental .env commits (declared in .gitignore)
- Environment-specific config without code changes

**Implementation Pattern**:
```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

**Alternatives Considered**:
- Plain os.environ: No validation, no defaults; BaseSettings provides structure
- python-dotenv: Deprecated in favor of pydantic_settings (Pydantic v2)

---

### 3. SQLAlchemy sessionmaker + Alembic Versioning

**Decision**: Use SQLAlchemy sessionmaker with conditional connect_args for SQLite (check_same_thread=False for testing) and Alembic for schema versioning.

**Rationale**:
- SQLAlchemy ORM abstracts DB, supports SQLite (dev) and Postgres (prod) with single codebase
- Alembic provides explicit versioning, rollback capability, audit trail
- connect_args conditional: SQLite single-threaded by design; in-memory DB for tests needs special handling

**Implementation Pattern**:
```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

# In routers: get_db yields SessionLocal(), services never touch Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Alternatives Considered**:
- Raw SQL: No, violates Artículo III (no concatenated SQL)
- SQLModel: Hybrid model/schema; Pydantic + SQLAlchemy separate models cleaner for this scope

---

### 4. pytest Fixtures for In-Memory SQLite

**Decision**: Use pytest fixtures to provide an in-memory SQLite DB (`:memory:`) for all unit and integration tests, with automatic cleanup between tests.

**Rationale**:
- In-memory DB provides isolation (each test is independent, no pollution)
- Fast (no disk I/O), perfect for pyramid base (many unit tests)
- Fixture-based injection simplifies test setup, follows pytest best practices

**Implementation Pattern**:
```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from app.models import Base

@pytest.fixture(scope="function")
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    yield db
    db.close()

@pytest.fixture
def fake_habitos_repo(db):
    return HabitosRepository(db)

# Usage in test: def test_crear_habito(fake_habitos_repo): ...
```

**Alternatives Considered**:
- pytest-postgresql: Requires external service; in-memory SQLite sufficient for v1
- unittest.mock: Forbidden by Artículo VII (must use fake repos with real contract)

---

### 5. app.dependency_overrides for FastAPI Tests

**Decision**: Use FastAPI's app.dependency_overrides to substitute get_db, repositories, and get_current_user in tests without mocking.

**Rationale**:
- Maintains real service logic (no mocking); only DB and auth context are swapped
- Tests API behavior end-to-end with real request/response processing
- Follows Artículo VII.5 (dependency injection for testing)

**Implementation Pattern**:
```python
# tests/api/conftest.py
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def test_client(db):
    def override_get_db():
        yield db
    
    def override_get_current_user():
        return Usuario(id=999, email="test@example.com")
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    yield TestClient(app)
    
    app.dependency_overrides.clear()
```

**Alternatives Considered**:
- unittest.mock.patch: Violates Artículo VII (no unittest.mock for dependency injection)
- testclient + live app: Requires DB spinup, slower; dependency_overrides provides speed + safety

---

### 6. MCP streamable-http Integration

**Decision**: Embed MCP server (streamable-http transport) within the same FastAPI app using the official "mcp" SDK. Extract JWT from Authorization header in HTTP request context.

**Rationale**:
- Single process simplifies deployment (no separate MCP server)
- streamable-http allows Claude to call tools via HTTP over structured stdio
- JWT extraction from header integrates with existing FastAPI auth (reuse get_current_user)

**Implementation Pattern**:
```python
# app/mcp/auth.py
def extract_jwt_from_request(request):
    # In streamable-http context, parse Authorization: Bearer <token>
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None

# app/mcp/tools.py — each tool definition calls services directly:
@tool
def crear_habito(nombre: str, frecuencia_objetivo: int):
    jwt_token = extract_jwt_from_request(current_request)
    usuario_id = get_current_user(token=jwt_token)
    return services.habitos.crear_habito(nombre, frecuencia_objetivo, repo=habitos_repository)
```

**Alternatives Considered**:
- Separate MCP server: Additional process, more complex deployment
- Custom auth in tools: JWT extraction already standardized in get_current_user; reuse

---

### 7. Fake Repository Pattern (No unittest.mock)

**Decision**: Create FakeHabitosRepository and FakeUsuariosRepository classes that implement the same interface as real repositories but use in-memory lists/dicts.

**Rationale**:
- Adheres to Artículo VII (forbidden: unittest.mock for dependency injection)
- Verifiable behavior (fake repo is real code, not mocking magic)
- Simple to audit, debug, and extend

**Implementation Pattern**:
```python
# app/repositories/habitos.py
class HabitosRepository:
    def __init__(self, session):
        self.session = session
    
    def save(self, habito): ...
    def get_by_id(self, id, usuario_id): ...

# tests/fakes/habitos_fake.py
class FakeHabitosRepository:
    def __init__(self):
        self.habitos = {}
    
    def save(self, habito):
        self.habitos[habito.id] = habito
    
    def get_by_id(self, id, usuario_id):
        h = self.habitos.get(id)
        return h if h and h.usuario_id == usuario_id else None

# Usage in unit test:
def test_crear_habito():
    fake_repo = FakeHabitosRepository()
    result = services.habitos.crear_habito("Exercise", 3, repo=fake_repo)
    assert result.nombre == "Exercise"
```

**Alternatives Considered**:
- Mock: Forbidden by Artículo VII
- Real DB in unit tests: Slow, creates test interdependencies; fake repos provide isolation

---

## Summary

All 7 research items resolved. No blockers for Phase 1 design. Technology stack finalized:
- Auth: pyjwt + passlib[bcrypt]
- Config: pydantic_settings.BaseSettings
- ORM: SQLAlchemy + Alembic
- Testing: pytest + in-memory SQLite + app.dependency_overrides + fake repos
- MCP: Official SDK, streamable-http, JWT extraction

Ready for data-model.md, contracts, and quickstart.md generation.
