"""Tests for rule-based personality profile generation."""

import json
import tempfile
import unittest
from pathlib import Path

from xclone_data.personality import generate_personality_profile, save_personality_profile
from xclone_data.synthetic_data import SYNTHETIC_TWEETS


class PersonalityProfileTests(unittest.TestCase):
    def test_profile_contains_evidence_labeled_analysis(self) -> None:
        profile = generate_personality_profile(SYNTHETIC_TWEETS)

        self.assertEqual(profile["tweet_count"], 15)
        self.assertEqual(profile["dataset_context"]["classification"], "synthetic sample data")
        self.assertIsNotNone(profile["communication_style"]["measured_patterns"]["average_words"])
        self.assertTrue(profile["frequently_discussed_topics"]["topics"])
        self.assertEqual(profile["debate_style"]["status"], "unknown")
        self.assertTrue(profile["humor_characteristics"]["observable_cues"])
        self.assertTrue(profile["representative_examples"])

    def test_empty_dataset_returns_unknown_interpretations(self) -> None:
        profile = generate_personality_profile([])

        self.assertEqual(profile["tweet_count"], 0)
        self.assertIsNone(profile["communication_style"]["measured_patterns"]["average_words"])
        self.assertEqual(profile["frequently_discussed_topics"]["status"], "unknown")
        self.assertEqual(profile["humor_characteristics"]["status"], "unknown")
        self.assertEqual(profile["debate_style"]["status"], "unknown")
        self.assertEqual(profile["representative_examples"], [])

    def test_malformed_input_raises_without_echoing_tweet_content(self) -> None:
        with self.assertRaisesRegex(TypeError, "Tweet record"):
            generate_personality_profile([{"text": "not a Tweet record"}])
        with self.assertRaisesRegex(TypeError, "iterable"):
            generate_personality_profile(None)

    def test_empty_tweet_text_is_rejected(self) -> None:
        tweet_type = type(SYNTHETIC_TWEETS[0])
        malformed = tweet_type("bad-text", "  ", "2025-01-01T00:00:00Z", "twitter", False)

        with self.assertRaisesRegex(ValueError, "non-empty text"):
            generate_personality_profile([malformed])

    def test_profile_is_saved_as_utf8_json(self) -> None:
        profile = generate_personality_profile(SYNTHETIC_TWEETS)
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "nested" / "profile.json"
            saved_path = save_personality_profile(profile, output_path)

            with saved_path.open(encoding="utf-8") as profile_file:
                loaded = json.load(profile_file)

        self.assertEqual(loaded, profile)
        self.assertIn("not the real owner's personality", loaded["dataset_context"]["notice"])


if __name__ == "__main__":
    unittest.main()