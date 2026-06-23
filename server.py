from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from tools import create_clickup_task, insert_record, send_notification

load_dotenv()

mcp = FastMCP(
    "company-chat",
    instructions="""
    This server exposes internal developer workflow tools.
    Use dry_run=true for tools that support it unless the user explicitly asks to execute the action.
    Never send to management, all-company, or customer-facing channels unless explicitly requested.
    """,
)

mcp.tool()(send_notification)
mcp.tool()(insert_record)
mcp.tool()(create_clickup_task)


if __name__ == "__main__":
    mcp.run(transport="stdio")
