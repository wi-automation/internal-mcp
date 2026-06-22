import os
from pprint import pformat

import httpx


class DiscordNotificationProvider:
    max_content_length = 2000

    allowed_channels = {
        "dev",
    }

    def __init__(self) -> None:
        self.base_url = os.getenv("DISCORD_WEBHOOK_OK")

    async def send(self, payload: dict) -> dict:
        if not self.base_url:
            raise ValueError("DISCORD_WEBHOOK_OK is missing")

        discord_payload = self._to_discord_payload(payload)

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                self.base_url,
                json=discord_payload,
            )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise ValueError(
                f"Discord webhook returned {error.response.status_code}: "
                f"{error.response.text}"
            ) from error

        if not response.content:
            return {
                "status_code": response.status_code,
            }

        return response.json()

    def _to_discord_payload(self, payload: dict) -> dict:
        content = self._format_content(payload)
        return {
            "content": content[: self.max_content_length],
        }

    def _format_content(self, payload: dict) -> str:
        lines = [
            f"**{payload['title']}**",
            payload["summary"],
            f"Kind: {payload['kind']}",
            f"Risk: {payload['risk_level']}",
        ]

        details = payload.get("details") or {}
        if details:
            lines.extend(
                [
                    "",
                    "Details:",
                    f"```text\n{pformat(details, sort_dicts=True)}\n```",
                ]
            )

        return "\n".join(lines)
