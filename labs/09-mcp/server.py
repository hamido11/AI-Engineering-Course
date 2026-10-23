"""E2/Ship-It - minimal MCP server exposing the Lab-08 order tools.

Run:      python server.py            (stdio transport; an MCP host launches it)
Inspect:  npx @modelcontextprotocol/inspector python server.py
"""
try:                                              # mcp 2.x renamed FastMCP -> MCPServer
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:                               # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server

mcp = _Server("order-tools")

ORDERS = {"A1001": {"status": "shipped", "eta": "2026-08-12"},
          "A1002": {"status": "processing", "eta": None}}


@mcp.tool()
def get_order_status(order_id: str) -> dict:
    """Look up the shipping status of an order (ids look like A1001)."""
    if order_id not in ORDERS:
        return {"error": f"unknown order id {order_id!r}"}
    return ORDERS[order_id]


@mcp.tool()
def draft_refund(order_id: str, reason: str) -> dict:
    """Draft (never execute) a refund request for human review."""
    return {"draft": True, "order_id": order_id, "reason": reason,
            "note": "Execution requires human approval outside this server."}


if __name__ == "__main__":
    mcp.run()          # stdio transport by default
