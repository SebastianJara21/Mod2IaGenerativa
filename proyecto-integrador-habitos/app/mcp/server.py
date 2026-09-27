"""MCP Server for habit management tools (Artículo VI - real server implementation)."""

from mcp.server.fastmcp import FastMCP
from app.mcp.tools import habitos

# Create real MCP server instance using FastMCP with streamable_http support
# streamable_http_path="/" means the app will register routes at root (/),
# and we mount it at "/mcp" in FastAPI (so routes end up at /mcp)
mcp_server = FastMCP("habitos-tracker", streamable_http_path="/")

# Register tools through tools.habitos module
habitos.register(mcp_server)

if __name__ == "__main__":
    mcp_server.run()
