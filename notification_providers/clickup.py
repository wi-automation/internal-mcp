import os

import httpx


class ClickUpNotificationProvider:
    """Create and complete tasks through the ClickUp API."""

    def __init__(self) -> None:
        self.api_token = os.getenv("CLICKUP_API_TOKEN")
        self.base_url = os.getenv(
            "CLICKUP_API_URL", "https://api.clickup.com/api/v2"
        ).rstrip("/")
        self.completed_status = os.getenv("CLICKUP_COMPLETED_STATUS", "complete")

    async def create_task(self, payload: dict[str, object]) -> dict:
        list_id = payload.get("list_id")
        if not list_id:
            raise ValueError("ClickUp list_id is required")

        task_payload = {
            key: value
            for key, value in payload.items()
            if key != "list_id" and value is not None
        }

        custom_fields = task_payload.get("custom_fields")
        if isinstance(custom_fields, dict):
            task_payload["custom_fields"] = [
                {"id": field_id, "value": value}
                for field_id, value in custom_fields.items()
            ]

        return await self._request(
            "POST",
            f"/list/{list_id}/task",
            task_payload,
        )

    async def get_workspaces(self) -> list[dict]:
        response = await self._request("GET", "/team")
        return response.get("teams", [])

    async def get_spaces(self, workspace_id: str) -> list[dict]:
        response = await self._request(
            "GET",
            f"/team/{workspace_id}/space",
            params={"archived": "false"},
        )
        return response.get("spaces", [])

    async def get_folders(self, space_id: str) -> list[dict]:
        response = await self._request(
            "GET",
            f"/space/{space_id}/folder",
            params={"archived": "false"},
        )
        return response.get("folders", [])

    async def get_folderless_lists(self, space_id: str) -> list[dict]:
        response = await self._request(
            "GET",
            f"/space/{space_id}/list",
            params={"archived": "false"},
        )
        return response.get("lists", [])

    async def find_lists(self, name: str) -> list[dict[str, object]]:
        """Find accessible ClickUp lists or lists inside matching folders."""
        if not name.strip():
            raise ValueError("ClickUp list name is required")

        query = name.casefold()
        matches = []

        for workspace in await self.get_workspaces():
            for space in await self.get_spaces(str(workspace["id"])):
                for folder in await self.get_folders(str(space["id"])):
                    folder_matches = query in folder["name"].casefold()
                    for clickup_list in folder.get("lists", []):
                        if folder_matches or query in clickup_list["name"].casefold():
                            matches.append(
                                self._list_location(
                                    clickup_list,
                                    workspace,
                                    space,
                                    folder,
                                )
                            )

                for clickup_list in await self.get_folderless_lists(str(space["id"])):
                    if query in clickup_list["name"].casefold():
                        matches.append(
                            self._list_location(clickup_list, workspace, space)
                        )

        return matches

    async def find_users(self, query: str) -> list[dict[str, object]]:
        """Find accessible ClickUp users by username or email address."""
        if not query.strip():
            raise ValueError("ClickUp user query is required")

        normalized_query = query.casefold()
        matches = []

        for workspace in await self.get_workspaces():
            for member in workspace.get("members", []):
                user = member.get("user", {})
                username = str(user.get("username") or "")
                email = str(user.get("email") or "")
                if normalized_query not in username.casefold() and (
                    normalized_query not in email.casefold()
                ):
                    continue

                matches.append(
                    {
                        "id": user.get("id"),
                        "username": username,
                        "email": email,
                        "role": member.get("role"),
                        "workspace": workspace.get("name"),
                        "workspace_id": workspace.get("id"),
                    }
                )

        return matches

    async def get_task(self, task_id: str) -> dict:
        if not task_id.strip():
            raise ValueError("ClickUp task_id is required")

        return await self._request("GET", f"/task/{task_id}")

    async def get_list(self, list_id: str) -> dict:
        if not list_id.strip():
            raise ValueError("ClickUp list_id is required")

        return await self._request("GET", f"/list/{list_id}")

    async def get_task_statuses(self, task_id: str) -> list[dict[str, object]]:
        """Return the statuses configured for a task's home List."""
        task = await self.get_task(task_id)
        task_list = task.get("list") or {}
        list_id = str(task_list.get("id") or "")
        if not list_id:
            raise ValueError("ClickUp task response did not include a home list ID")

        clickup_list = await self.get_list(list_id)
        statuses = clickup_list.get("statuses")
        if not isinstance(statuses, list):
            raise ValueError("ClickUp list response did not include statuses")

        return statuses

    async def complete_task(
        self,
        task_id: str,
        comment: str | None = None,
    ) -> dict:
        if not task_id:
            raise ValueError("ClickUp task_id is required")

        task = await self.update_task_status(task_id, self.completed_status)

        result = {"task": task}
        if comment:
            result["comment"] = await self.add_comment(task_id, comment)

        return result

    async def update_task_status(self, task_id: str, status: str) -> dict:
        """Set a ClickUp task to a named status available in its list."""
        if not task_id.strip():
            raise ValueError("ClickUp task_id is required")
        if not status.strip():
            raise ValueError("ClickUp status is required")

        statuses = await self.get_task_statuses(task_id)
        matching_status = next(
            (
                item
                for item in statuses
                if str(item.get("status") or "").casefold() == status.casefold()
            ),
            None,
        )
        if matching_status is None:
            available = [
                str(item.get("status")) for item in statuses if item.get("status")
            ]
            raise ValueError(
                f"ClickUp status '{status}' is not available for this task. "
                f"Available statuses: {', '.join(available)}"
            )

        resolved_status = str(matching_status["status"])

        return await self._request(
            "PUT",
            f"/task/{task_id}",
            {"status": resolved_status},
        )

    async def add_comment(self, task_id: str, comment: str) -> dict:
        if not task_id:
            raise ValueError("ClickUp task_id is required")
        if not comment.strip():
            raise ValueError("ClickUp comment is required")

        return await self._request(
            "POST",
            f"/task/{task_id}/comment",
            {"comment_text": comment, "notify_all": False},
        )

    async def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, object] | None = None,
        params: dict[str, str] | None = None,
    ) -> dict:
        if not self.api_token:
            raise ValueError("CLICKUP_API_TOKEN is missing")

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.request(
                method,
                f"{self.base_url}{path}",
                headers={"Authorization": self.api_token},
                json=payload,
                params=params,
            )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise ValueError(
                f"ClickUp API returned {error.response.status_code}: "
                f"{error.response.text}"
            ) from error

        if not response.content:
            return {"status_code": response.status_code}

        return response.json()

    @staticmethod
    def _list_location(
        clickup_list: dict,
        workspace: dict,
        space: dict,
        folder: dict | None = None,
    ) -> dict[str, object]:
        return {
            "id": clickup_list["id"],
            "name": clickup_list["name"],
            "folder": folder["name"] if folder else None,
            "folder_id": folder["id"] if folder else None,
            "space": space["name"],
            "space_id": space["id"],
            "workspace": workspace["name"],
            "workspace_id": workspace["id"],
        }
