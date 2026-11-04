"""Import and retrieve tweet records from SQLite."""

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .database import DEFAULT_DATABASE_PATH, initialize_database


@dataclass(frozen=True)
class Tweet:
    """A post with its original text and available conversation metadata."""

    tweet_id: str
    text: str
    created_at: str
    source_platform: str
    is_reply: bool
    conversation_id: str | None = None


def import_tweets(
    tweets: Iterable[Tweet],
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> int:
    """Insert new tweets, leaving existing tweet IDs unchanged.

    Returns the number of records inserted. Tweet text is stored verbatim.
    """
    initialize_database(database_path)
    inserted = 0
    with sqlite3.connect(database_path) as connection:
        for tweet in tweets:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO tweets (
                    tweet_id, tweet_text, created_at, source_platform,
                    is_reply, conversation_id
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    tweet.tweet_id,
                    tweet.text,
                    tweet.created_at,
                    tweet.source_platform,
                    int(tweet.is_reply),
                    tweet.conversation_id,
                ),
            )
            inserted += cursor.rowcount
    return inserted


def get_tweets(database_path: str | Path = DEFAULT_DATABASE_PATH) -> list[Tweet]:
    """Return all stored tweets ordered by timestamp and ID."""
    initialize_database(database_path)
    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT tweet_id, tweet_text, created_at, source_platform,
                   is_reply, conversation_id
            FROM tweets
            ORDER BY created_at, tweet_id
            """
        ).fetchall()

    return [
        Tweet(
            tweet_id=row[0],
            text=row[1],
            created_at=row[2],
            source_platform=row[3],
            is_reply=bool(row[4]),
            conversation_id=row[5],
        )
        for row in rows
    ]