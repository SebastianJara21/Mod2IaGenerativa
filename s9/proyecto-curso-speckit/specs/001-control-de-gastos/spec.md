# Feature Specification: Sistema de Control de Gastos Personales

**Feature Branch**: `001-control-de-gastos`

**Created**: 2026-09-23

**Status**: Draft

## Clarifications

### Session 2026-09-23

- Q: ¿Límite de 500 por categoría: per-calendar-month o cumulative? → A: Cumulative forever (no reset) — mandated by Compatibility Contract function signature `total_por_categoria(db, usuario_id, categoria) -> float` which has no date parameters
- Q: ¿Incluir PATCH/DELETE para update/delete de gastos? → A: No — only POST (create) and GET (read/list); no update/delete operations in this feature

---

## User Scenarios & Testing

### User Story 1 - Registro de Usuario (Priority: P1)

Un usuario nuevo puede crear una cuenta en el sistema con su email y contraseña. Esta es la funcionalidad fundamental sin la cual nadie puede acceder al sistema.

**Why this priority**: P1 - Sin autenticación y registro no hay sistema. Es la puerta de entrada.

**Independent Test**: Un nuevo usuario puede registrarse con email y contraseña, y luego usar esas credenciales para obtener un token JWT que le permite hacer solicitudes autenticadas.

**Acceptance Scenarios**:

1. **Given** un usuario sin cuenta, **When** hace POST a /usuarios/ con email único y contraseña, **Then** recibe 201 con los datos del usuario (sin exposición de contraseña)
2. **Given** un usuario intenta registrarse con un email ya existente, **When** hace POST a /usuarios/, **Then** recibe 400 "email duplicado"
3. **Given** un usuario envía datos inválidos (campo faltante, formato incorrecto), **When** hace POST a /usuarios/, **Then** recibe 422 validación

---

### User Story 2 - Autenticación y Obtención de Token (Priority: P1)

Un usuario registrado puede autenticarse e obtener un token JWT que le permite acceder a endpoints protegidos.

**Why this priority**: P1 - Sin autenticación no hay control de gastos por usuario; es fundamental para el aislamiento de datos.

**Independent Test**: Un usuario con credenciales válidas puede obtener un JWT válido; con credenciales inválidas recibe 401.

**Acceptance Scenarios**:

1. **Given** un usuario registrado con email y contraseña válidas, **When** hace POST a /usuarios/token con username y password, **Then** recibe 200 con un JWT válido
2. **Given** un usuario intenta autenticarse con contraseña incorrecta, **When** hace POST a /usuarios/token, **Then** recibe 401 credenciales inválidas
3. **Given** un usuario sin token intenta acceder a /gastos/, **When** hace GET sin Authorization header, **Then** recibe 401

---

### User Story 3 - Registrar Gasto (Priority: P1)

Un usuario autenticado puede registrar un nuevo gasto con descripción, monto y categoría válida.

**Why this priority**: P1 - Es el core del sistema; sin poder registrar gastos no hay funcionalidad.

**Independent Test**: Un usuario autenticado puede crear un gasto con monto > 0 y categoría válida, y verifica que el gasto se registra sin exceder el límite de categoría.

**Acceptance Scenarios**:

1. **Given** usuario autenticado, **When** POST a /gastos/ con descripción, monto > 0, categoría válida (comida, transporte, entretenimiento, otros), **Then** recibe 201 con el gasto creado
2. **Given** usuario intenta registrar gasto con monto ≤ 0, **When** POST a /gastos/, **Then** recibe 400 validación
3. **Given** usuario intenta usar categoría inexistente, **When** POST a /gastos/, **Then** recibe 400 "categoría inválida"
4. **Given** la suma de gastos en una categoría es 450 y el usuario intenta agregar 100, **When** POST a /gastos/, **Then** recibe 400 "límite excedido" (máximo 500 por categoría)
5. **Given** usuario intenta registrar gasto sin autenticación, **When** POST a /gastos/ sin token, **Then** recibe 401

---

### User Story 4 - Listar Gastos Propios (Priority: P1)

Un usuario autenticado puede ver el listado paginado de sus gastos, no los de otros usuarios.

**Why this priority**: P1 - Necesario para que el usuario vea qué ha gastado. También verifica el aislamiento de datos (seguridad crítica).

**Independent Test**: Un usuario autenticado obtiene su listado con paginación; intentar acceder a gastos de otro usuario mediante parámetro en la URL no cambia lo que ve.

**Acceptance Scenarios**:

1. **Given** usuario autenticado con 15 gastos en BD, **When** GET /gastos/ con skip=0 limit=20, **Then** recibe 200 con lista de sus 15 gastos
2. **Given** usuario autenticado con gastos, **When** GET /gastos/ con skip=0 limit=5, **Then** recibe lista de 5 gastos (paginación)
3. **Given** usuario autenticado sin gastos, **When** GET /gastos/, **Then** recibe 200 con lista vacía
4. **Given** usuario intenta GET /gastos/ con skip negativo o limit inválido, **When** hace la solicitud, **Then** recibe 422 validación
5. **Given** usuario A intenta ver gastos pasando usuario_id de usuario B en la solicitud, **When** GET /gastos/, **Then** recibe solo sus gastos (usuario A), nunca los de B

---

### User Story 5 - Tool MCP: Registrar Gasto (Priority: P2)

Un cliente MCP autenticado puede usar la tool `registrar_gasto` para crear gastos con las mismas reglas de negocio.

**Why this priority**: P2 - Amplía las formas en que se puede registrar un gasto (CLI, agentes, etc.) sin reimplementar lógica.

**Independent Test**: Llamar a la tool devuelve los mismos errores y éxitos que el endpoint REST; verifica reutilización de lógica.

**Acceptance Scenarios**:

1. **Given** cliente MCP autenticado, **When** llama `registrar_gasto("compra", 50.5, "comida")`, **Then** devuelve el gasto creado
2. **Given** cliente MCP llama con categoría inválida, **When** `registrar_gasto("gasto", 100, "shopping")`, **Then** devuelve error estructurado con detalle
3. **Given** la suma de "comida" es 480, **When** `registrar_gasto("almuerzo", 50, "comida")`, **Then** devuelve error "límite excedido"

---

### User Story 6 - Tool MCP: Listar Gastos (Priority: P2)

Un cliente MCP autenticado puede usar la tool `listar_gastos` para obtener gastos propios con paginación.

**Why this priority**: P2 - Complementa la funcionalidad REST para MCP.

**Independent Test**: Llamar a la tool devuelve los mismos gastos que GET /gastos/ con los mismos parámetros.

**Acceptance Scenarios**:

1. **Given** cliente MCP autenticado, **When** llama `listar_gastos(skip=0, limit=20)`, **Then** devuelve lista de gastos del usuario autenticado
2. **Given** cliente MCP sin autenticación (fallback a usuario demo), **When** llama `listar_gastos()`, **Then** devuelve gastos del usuario demo

---

### Edge Cases

- ¿Qué sucede cuando se intenta registrar un gasto con descripción vacía? → Error de validación (422)
- ¿Cómo maneja el sistema dos usuarios creados con el mismo email? → 400 en la creación del segundo (email duplicado)
- ¿Qué pasa si la sesión MCP pierde autenticación? → Las tools fallecen con error de autorización
- ¿Qué ocurre al intentar acceder a /gastos/ de otro usuario directamente? → Se filtra por usuario del JWT, nunca por parámetro URL

---

## Requirements

### Functional Requirements

- **FR-001**: Sistema MUST permitir registro de usuario con email único y contraseña (hashed con bcrypt, nunca expuesta)
- **FR-002**: Sistema MUST validar contraseña según estándares de seguridad (presente, no vacía, etc.)
- **FR-003**: Sistema MUST generar JWT válido con HS256 al autenticar usuario
- **FR-004**: Sistema MUST permitir registrar gasto con descripción, monto > 0, categoría válida (comida, transporte, entretenimiento, otros)
- **FR-005**: Sistema MUST rechazar gastos con monto ≤ 0 (error 400 "monto inválido")
- **FR-006**: Sistema MUST rechazar categorías inexistentes (error 400 "categoría inválida", NO excepción genérica)
- **FR-007**: Sistema MUST validar límite máximo de 500 por categoría; rechazar gasto que lo exceda (error 400 "límite excedido")
- **FR-008**: Sistema MUST filtrar gastos por usuario autenticado; un usuario NUNCA verá gastos de otro usuario sin importar parámetros de solicitud
- **FR-009**: Sistema MUST soportar paginación GET /gastos/ con skip y limit (defaults: skip=0, limit=20)
- **FR-010**: Sistema MUST exponer tools MCP `registrar_gasto` y `listar_gastos` con misma lógica que REST
- **FR-011**: Sistema MUST resolver identidad del usuario en MCP desde token JWT (streamable-http) o usuario demo (stdio, fallback documentado)
- **FR-012**: Sistema MUST devolver estructura clara de error en MCP ({"error": "..."}) nunca excepción no controlada
- **FR-013**: Sistema MUST responder 401 Unauthorized cuando falta o es inválido el token JWT
- **FR-014**: Sistema MUST responder 422 en errores de validación de schema (datos mal formados, tipos incorrectos)
- **FR-015**: Sistema MUST responder 201 Created en registro exitoso (usuarios, gastos)
- **FR-016**: Sistema MUST responder 200 OK en listados exitosos
- **FR-017**: Sistema MUST logear errores internos sin exponer detalles al cliente (500 genérico)

### Key Entities

- **Usuario**: id (único), email (único), hashed_password. Atributos sin exposición de contraseña en respuestas.
- **Gasto**: id (único), descripción (no vacía), monto (> 0), categoría (enum: comida, transporte, entretenimiento, otros), usuario_id (FK), fecha/timestamp.

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: Usuario puede registrarse y autenticarse en menos de 30 segundos (ciclo completo)
- **SC-002**: Sistema rechaza gasto fuera de reglas en menos de 500ms (validación rápida)
- **SC-003**: Listado de gastos se entrega en menos de 1 segundo incluso con 10,000 gastos históricos
- **SC-004**: 100% de gastos filtrados correctamente por usuario (zero cross-contamination de datos)
- **SC-005**: Todas las categorías válidas (4) son aceptadas consistentemente; categorías inválidas reciben 400
- **SC-006**: Límite de 500 por categoría se valida correctamente en 100% de casos
- **SC-007**: Tools MCP devuelven estructuras consistentes con REST API (mismo gasto creado, mismos errores)
- **SC-008**: Contraseña nunca aparece en logs, respuestas HTTP, ni en trazas de error
- **SC-009**: Cualquier error interno (no de negocio) retorna 500 genérico sin detalles de implementación

---

## Assumptions

- Las contraseñas se validan como "presente y no vacía" (longitud mínima/máxima no especificada → se usa estándar industrial)
- Email válido se valida con regex estándar; resolucionismo sobre existencia (no enviamos confirmación)
- SQLite se usa en desarrollo; el diseño de DB permite migración a Postgres sin cambios en services/routers
- JWT expira según `ACCESS_TOKEN_EXPIRE_MINUTES` (configurable en .env, no infinito)
- El usuario autenticado en MCP se obtiene del token JWT (streamable-http); fallback a usuario demo solo si `stdio` sin identidad propagable
- **Límite de categoría es ACUMULATIVO SIN RESET**: La suma de TODOS los gastos históricos del usuario en una categoría no puede exceder 500. No hay reset mensual ni rolling window — es cumulative para siempre (determinado por la firma fija de Compatibility Contract: `total_por_categoria(db, usuario_id, categoria) -> float` sin parámetros de fecha)
- Descripción vacía es rechazada (validación básica, no solo monto)
- El proyecto reutiliza tests de las Sesiones 6-8 sin modificar sus aserciones → las firmas de función son un contrato fijo
- **Alcance limitado a CRUD básico**: Solo POST (create), GET (read/list). No hay PATCH (update) ni DELETE (delete) en esta feature — son futures separadas

---

## API Contract (Reference)

| Método | Ruta              | Auth | Request                          | Éxito         | Errores esperados                          |
|--------|-------------------|------|-----------------------------------|---------------|---------------------------------------------|
| POST   | /usuarios/        | No   | email, password                   | 201 Usuario   | 400 email duplicado, 422 validación         |
| POST   | /usuarios/token   | No   | username, password (form)         | 200 token JWT | 401 credenciales inválidas                  |
| POST   | /gastos/          | Sí   | descripcion, monto, categoria     | 201 Gasto     | 400 categoría inválida, 400 límite excedido, 401, 422 |
| GET    | /gastos/          | Sí   | query: skip, limit                | 200 lista     | 401, 422 (skip/limit inválidos)             |

---

## Compatibility Contract (Non-negotiable)

These function signatures and exception types from Sessions 6-8 tests are immutable:

- `app/services/gastos.py`:
  - `CategoriaInvalidaError` exception class
  - `LimiteExcedidoError` exception class
  - `LIMITE_POR_CATEGORIA = 500.0` constant
  - `registrar_gasto(db, usuario_id, descripcion, monto, categoria, repo=gastos_repository) -> dict`
  - `listar_gastos(db, usuario_id, skip=0, limit=20, repo=gastos_repository) -> list[dict]`
  
- `app/repositories/gastos.py` (module with functions, NOT a class):
  - `guardar(db, usuario_id, descripcion, monto, categoria) -> dict`
  - `listar(db, usuario_id, skip=0, limit=20) -> list[dict]`
  - `total_por_categoria(db, usuario_id, categoria) -> float`
  
- `app/repositories/usuarios.py`:
  - `obtener_por_email(db, email) -> Usuario | None`
  - `guardar(db, email, hashed_password) -> Usuario`
  
- `app.database.get_db`, `app.dependencies.get_current_user`, `app.dependencies.get_gastos_repo`
- `app.models.usuario.Usuario(id=..., email=..., hashed_password=...)`
- `tests/__init__.py` must exist and export `RepositorioFalso` from `tests.test_gastos`

---

## Error Test Cases (Explicit)

These must be validated by tests:

1. Registrar gasto con monto negativo o cero → 400
2. Registrar gasto con categoría inexistente → 400 "categoría inválida"
3. Registrar gasto que excede límite de 500 en su categoría → 400 "límite excedido"
4. Listar o registrar gastos sin token → 401
5. Intentar listar gastos de otro usuario pasando su ID en parámetros → filtrarse por usuario del JWT, nunca por parámetro
