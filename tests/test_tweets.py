"""Tests for the SQLite tweet pipeline."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from xclone_data.database import initialize_database
from xclone_data.synthetic_data import SYNTHETIC_TWEETS
from xclone_data.tweets import Tweet, get_tweets, import_tweets


class TweetStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "tweets.sqlite3"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_initialize_creates_database_and_tweet_schema(self) -> None:
        initialize_database(self.database_path)

        with sqlite3.connect(self.database_path) as connection:
            table = connection.execute(
                "SELECT name FROM sqlite_master WHERE type = ? AND name = ?",
                ("table", "tweets"),
            ).fetchone()
        self.assertEqual(table, ("tweets",))

    def test_import_and_retrieve_synthetic_tweets_verbatim(self) -> None:
        inserted = import_tweets(SYNTHETIC_TWEETS, self.database_path)
        stored = get_tweets(self.database_path)

        self.assertEqual(inserted, 15)
        self.assertEqual(stored, sorted(SYNTHETIC_TWEETS, key=lambda tweet: (tweet.created_at, tweet.tweet_id)))
        self.assertEqual(stored[1].text, "Coach said 'one more drill' and somehow we did seven 😂")
        self.assertIsNone(stored[2].conversation_id)

    def test_duplicate_tweet_ids_are_ignored(self) -> None:
        original = Tweet("duplicate-id", "Original wording!", "2025-02-01T00:00:00Z", "twitter", False)
        conflicting_duplicate = Tweet("duplicate-id", "Changed wording", "2025-02-02T00:00:00Z", "twitter", True)

        self.assertEqual(import_tweets([original], self.database_path), 1)
        self.assertEqual(import_tweets([conflicting_duplicate], self.database_path), 0)
        self.assertEqual(get_tweets(self.database_path), [original])


if __name__ == "__main__":
    unittest.main()