import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from tools import (
    add_clickup_comment,
    complete_clickup_task,
    create_clickup_task,
    find_clickup_lists,
    find_clickup_users,
    get_server_info,
    insert_record,
    send_notification,
)

load_dotenv()

host = os.getenv("MCP_HOST", "127.0.0.1")
port = int(os.getenv("MCP_PORT", "8012"))

mcp = FastMCP(
    "company-chat",
    host=host,
    port=port,
    instructions="""
    This server exposes internal developer workflow tools.
    Use dry_run=true for tools that support it unless the user explicitly asks to execute the action.
    Resolve unknown ClickUp list and assignee IDs with find_clickup_lists and find_clickup_users before creating a task.
    Never send to management, all-company, or customer-facing channels unless explicitly requested.
    """,
)

mcp.tool()(send_notification)
mcp.tool()(insert_record)
mcp.tool()(create_clickup_task)
mcp.tool()(complete_clickup_task)
mcp.tool()(add_clickup_comment)
mcp.tool()(find_clickup_lists)
mcp.tool()(find_clickup_users)
mcp.tool()(get_server_info)


if __name__ == "__main__":
    mcp.run(transport="stdio")
