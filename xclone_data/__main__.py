"""Initialize the local database and import the synthetic sample posts."""

from .database import DEFAULT_DATABASE_PATH, initialize_database
from .synthetic_data import SYNTHETIC_TWEETS
from .tweets import get_tweets, import_tweets


def main() -> None:
    initialize_database(DEFAULT_DATABASE_PATH)
    import_tweets(SYNTHETIC_TWEETS, DEFAULT_DATABASE_PATH)
    print(f"Database ready with {len(get_tweets(DEFAULT_DATABASE_PATH))} synthetic tweets.")


if __name__ == "__main__":
    main()