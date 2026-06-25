import os
from pprint import pformat

import httpx


class MattermostNotificationProvider:
    max_content_length = 16383

    allowed_channels = {
        "dev",
    }

    def __init__(self) -> None:
        webhook_id = os.getenv("MATTERMOST_WH_API_KEY")
        webhook_url = os.getenv("MATTERMOST_WH_API_URL")
        self.base_url = f"{webhook_url}/{webhook_id}" if webhook_id else None

    async def send(self, payload: dict) -> dict:
        if not self.base_url:
            raise ValueError("MATTERMOST_WH_API_KEY is missing")

        mattermost_payload = self._to_mattermost_payload(payload)

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                self.base_url,
                json=mattermost_payload,
            )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise ValueError(
                f"Mattermost webhook returned {error.response.status_code}: "
                f"{error.response.text}"
            ) from error

        if not response.content:
            return {
                "status_code": response.status_code,
            }

        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.json()

        return {
            "status_code": response.status_code,
            "text": response.text,
        }

    def _to_mattermost_payload(self, payload: dict) -> dict:
        text = self._format_text(payload)
        return {
            "text": text[: self.max_content_length],
        }

    def _format_text(self, payload: dict) -> str:
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
