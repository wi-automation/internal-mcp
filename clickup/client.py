class StubClickUpClient:
    async def create_task(self, payload: dict[str, object]) -> dict:
        return {
            "task": payload,
            "created": False,
            "stub": True,
            "message": "ClickUp task creation is stubbed. Add configuration and real client logic.",
        }
