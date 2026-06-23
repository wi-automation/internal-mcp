import os

from database.client import AsyncpgDatabaseClient
from interface.database_client import DatabaseClient
from literals import DatabaseInstance


def get_database_client(database: DatabaseInstance) -> DatabaseClient:
    if database != "scraper":
        raise ValueError(f"Unsupported database instance: {database}")

    return AsyncpgDatabaseClient(
        user=_required_env("DB_SCRAPER_USER"),
        password=_required_env("DB_SCRAPER_PASSWORD"),
        host=_required_env("DB_SCRAPER_HOST"),
        port=_required_int_env("DB_SCRAPER_PORT"),
        database=_required_env("DB_SCRAPER_NAME"),
    )


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} is missing")

    return value


def _required_int_env(name: str) -> int:
    value = _required_env(name)
    try:
        return int(value)
    except ValueError as error:
        raise ValueError(f"{name} must be an integer") from error
