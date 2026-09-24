"""FastAPI application factory and initialization.

Sets up:
- FastAPI app with error handling
- Database initialization
- Middleware for logging
- MCP server mounting (future)
- Routers registration (future)
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.database import Base, engine
from app.logging_config import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager.

    Runs startup code before app starts, shutdown code after app stops.
    Per Artículo III (Persistence): Initialize database on startup.
    """
    # Startup: create all tables
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")

    # TODO: Mount MCP server here (when mcp/server.py is implemented)

    yield

    # Shutdown: cleanup (if needed)
    logger.info("Shutting down...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Control de Gastos",
        description="Personal expense tracking system",
        version="1.0.0",
        lifespan=lifespan
    )

    # Error handler for unhandled exceptions
    # Per Artículo IV.5: Return 500 generic, log details internally
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Catch unhandled exceptions and return generic 500 response."""
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Error interno del servidor"}
        )

    # Register routers
    from app.routers import usuarios
    app.include_router(usuarios.router)

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "ok"}

    return app


# Global app instance
app = create_app()
