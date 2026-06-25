import re

import asyncpg


class AsyncpgDatabaseClient:
    _identifier_pattern = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

    def __init__(
        self,
        *,
        user: str,
        password: str,
        host: str,
        port: int,
        database: str,
    ) -> None:
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database

    async def insert(self, table: str, record: dict[str, object]) -> dict:
        if not record:
            raise ValueError("record must contain at least one field")

        table_name = self._quote_qualified_identifier(table)
        columns = [self._quote_identifier(column) for column in record]
        placeholders = [f"${index}" for index in range(1, len(record) + 1)]
        values = list(record.values())

        # Identifiers are validated/quoted; values use parameters.
        query = (
            f"insert into {table_name} ({', '.join(columns)}) "  # nosec B608
            f"values ({', '.join(placeholders)}) "
            "returning *"
        )

        connection = await asyncpg.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        )
        try:
            row = await connection.fetchrow(query, *values)
        finally:
            await connection.close()

        return {
            "table": table,
            "record": record,
            "inserted": True,
            "inserted_record": dict(row) if row else None,
        }

    def _quote_qualified_identifier(self, identifier: str) -> str:
        parts = identifier.split(".")
        if not parts or any(not part for part in parts):
            raise ValueError(f"Invalid database table identifier: {identifier}")

        return ".".join(self._quote_identifier(part) for part in parts)

    def _quote_identifier(self, identifier: str) -> str:
        if not self._identifier_pattern.match(identifier):
            raise ValueError(f"Invalid database identifier: {identifier}")

        return f'"{identifier}"'
