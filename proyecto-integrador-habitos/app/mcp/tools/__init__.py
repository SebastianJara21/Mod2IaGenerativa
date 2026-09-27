"""MCP tools package."""

# Re-export individual tool functions for backwards compatibility with tests
from app.mcp.tools.habitos import (
    crear_habito_tool,
    listar_habitos_tool,
    marcar_habito_tool,
    eliminar_habito_tool,
)

__all__ = [
    "crear_habito_tool",
    "listar_habitos_tool",
    "marcar_habito_tool",
    "eliminar_habito_tool",
]
