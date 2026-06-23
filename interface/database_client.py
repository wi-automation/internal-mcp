from typing import Protocol


class DatabaseClient(Protocol):
    async def insert(self, table: str, record: dict[str, object]) -> dict:
        pass
