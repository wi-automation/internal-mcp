from pathlib import Path
from tomllib import load

PROJECT_FILE = Path(__file__).resolve().parents[1] / "pyproject.toml"


def get_server_info() -> dict[str, str]:
    """Return identifying information about the running MCP server."""

    with PROJECT_FILE.open("rb") as project_file:
        project = load(project_file)

    return {
        "name": project["project"]["name"],
        "version": project["project"]["version"],
    }
