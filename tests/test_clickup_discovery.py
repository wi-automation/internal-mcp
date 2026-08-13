from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from notification_providers.clickup import ClickUpNotificationProvider


class ClickUpUserDiscoveryTests(IsolatedAsyncioTestCase):
    async def test_find_users_matches_username_and_email(self) -> None:
        provider = ClickUpNotificationProvider()
        provider.get_workspaces = AsyncMock(
            return_value=[
                {
                    "id": "123",
                    "name": "Engineering",
                    "members": [
                        {
                            "user": {
                                "id": 456,
                                "username": "Ada Lovelace",
                                "email": "ada@example.com",
                            },
                            "role": 2,
                        }
                    ],
                }
            ]
        )

        by_name = await provider.find_users("lovelace")
        by_email = await provider.find_users("ADA@EXAMPLE")

        self.assertEqual(by_name, by_email)
        self.assertEqual(by_name[0]["id"], 456)
        self.assertEqual(by_name[0]["workspace_id"], "123")

    async def test_find_users_rejects_empty_query(self) -> None:
        provider = ClickUpNotificationProvider()

        with self.assertRaisesRegex(ValueError, "user query is required"):
            await provider.find_users("  ")
