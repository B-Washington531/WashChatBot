"""Generate and save a profile for the tweets in the local database."""

from .personality import DEFAULT_PROFILE_PATH, generate_personality_profile, save_personality_profile
from .tweets import get_tweets


def main() -> None:
    profile = generate_personality_profile(get_tweets())
    save_personality_profile(profile, DEFAULT_PROFILE_PATH)
    print(f"Personality profile saved to {DEFAULT_PROFILE_PATH}.")


if __name__ == "__main__":
    main()