from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from notification_providers.clickup import ClickUpNotificationProvider
from tools.clickup import update_clickup_task_status


class ClickUpStatusTests(IsolatedAsyncioTestCase):
    async def test_provider_updates_named_status(self) -> None:
        provider = ClickUpNotificationProvider()
        provider.get_task_statuses = AsyncMock(
            return_value=[{"status": "Development"}, {"status": "Complete"}]
        )
        provider._request = AsyncMock(
            return_value={"id": "abc", "status": "Development"}
        )

        result = await provider.update_task_status("abc", "development")

        self.assertEqual(result["status"], "Development")
        provider._request.assert_awaited_once_with(
            "PUT", "/task/abc", {"status": "Development"}
        )

    async def test_provider_rejects_unavailable_status(self) -> None:
        provider = ClickUpNotificationProvider()
        provider.get_task_statuses = AsyncMock(
            return_value=[{"status": "Development"}, {"status": "Complete"}]
        )
        provider._request = AsyncMock()

        with self.assertRaisesRegex(
            ValueError, "Available statuses: Development, Complete"
        ):
            await provider.update_task_status("abc", "Review")

        provider._request.assert_not_awaited()

    async def test_get_task_statuses_uses_home_list(self) -> None:
        provider = ClickUpNotificationProvider()
        provider.get_task = AsyncMock(return_value={"list": {"id": "list-123"}})
        provider.get_list = AsyncMock(
            return_value={"statuses": [{"status": "Development"}]}
        )

        statuses = await provider.get_task_statuses("abc")

        self.assertEqual(statuses, [{"status": "Development"}])
        provider.get_list.assert_awaited_once_with("list-123")

    async def test_tool_defaults_to_dry_run(self) -> None:
        result = await update_clickup_task_status("abc", "Development")

        self.assertEqual(
            result,
            {
                "ok": True,
                "dry_run": True,
                "payload": {"task_id": "abc", "status": "Development"},
                "note": "Status availability is validated only when dry_run is false.",
            },
        )

    async def test_tool_rejects_empty_status(self) -> None:
        result = await update_clickup_task_status("abc", "  ")

        self.assertEqual(result, {"ok": False, "error": "ClickUp status is required"})
