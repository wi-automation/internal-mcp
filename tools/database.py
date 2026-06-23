from database import get_database_client
from database.permissions import PERMITTED_TABLE_OPERATIONS
from literals import DatabaseInstance


def is_operation_permitted(
    database: DatabaseInstance,
    table: str,
    operation: str,
) -> bool:
    permitted_tables = PERMITTED_TABLE_OPERATIONS.get(database, {})
    permitted_operations = permitted_tables.get(table, set())

    return operation in permitted_operations


async def insert_record(
    database: DatabaseInstance,
    table: str,
    record: dict[str, object],
    dry_run: bool = True,
) -> dict:
    """
    Insert a record into the configured database.

    database: Configured database instance to use.
    table: Target database table.
    record: Column/value data to insert.
    dry_run: If true, only preview the insert payload without writing.
    """

    payload = {
        "database": database,
        "table": table,
        "record": record,
    }

    if not is_operation_permitted(database, table, "insert"):
        return {
            "ok": False,
            "error": f"Operation not permitted: insert on table {table}",
        }

    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "payload": payload,
        }

    try:
        database_client = get_database_client(database)
        result = await database_client.insert(table=table, record=record)
    except ValueError as error:
        return {
            "ok": False,
            "error": str(error),
        }

    return {
        "ok": True,
        "dry_run": False,
        "result": result,
    }
