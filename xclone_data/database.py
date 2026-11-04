"""SQLite database setup for XClone's tweet store."""

import sqlite3
from pathlib import Path

DEFAULT_DATABASE_PATH = Path("data") / "xclone.sqlite3"


def initialize_database(database_path: str | Path = DEFAULT_DATABASE_PATH) -> None:
    """Create the database directory and tweets table when absent."""
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tweets (
                tweet_id TEXT PRIMARY KEY,
                tweet_text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                source_platform TEXT NOT NULL,
                is_reply INTEGER NOT NULL CHECK (is_reply IN (0, 1)),
                conversation_id TEXT
            )
            """
        )