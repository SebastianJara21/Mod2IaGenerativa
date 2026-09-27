"""FastAPI application with integrated MCP server (Artículo VI)."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.routers import usuarios, habitos
from app.mcp.server import mcp_server

# Configure logging for exception details (Artículo IV.5)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamable-HTTP: create MCP app before lifespan
# (mcp_server.session_manager is lazy and only exists after calling streamable_http_app())
mcp_app = mcp_server.streamable_http_app()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle including MCP server.

    mcp_app carries its own lifespan (starts the streamable-http session manager).
    FastAPI does NOT start it automatically when mounted with app.mount() —
    we must enter it explicitly, or connections to /mcp fail or hang.
    """
    async with mcp_server.session_manager.run():
        yield


# Create FastAPI application with MCP lifespan
app = FastAPI(
    title="Proyecto Integrador: Habits Tracker",
    description="REST API + MCP Server for habit tracking",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers (Artículo II: Layered architecture)
app.include_router(usuarios.router)
app.include_router(habitos.router)

# Mount real MCP server as sub-application on /mcp path (Artículo VI)
app.mount("/mcp", mcp_app)

# Global exception handler (Artículo IV.5: Uncontrolled exceptions → 500)
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle unexpected exceptions with 500 and internal logging."""
    # Log full exception internally (never expose details to client)
    logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}", exc_info=True)

    # Return generic 500 to client
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
