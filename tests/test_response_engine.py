"""Tests for the mocked OpenAI response engine."""

import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from openai import APIError, AuthenticationError, RateLimitError

from xclone_data.response_engine import (
    APIAuthenticationError,
    APIRateLimitError,
    APIRequestError,
    DEFAULT_MODEL,
    MissingAPIKeyError,
    generate_response,
)


class ResponseEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.environment = patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)

    @patch("xclone_data.response_engine.OpenAI")
    def test_sends_profile_instructions_history_and_user_message(self, openai_class) -> None:
        client = openai_class.return_value
        client.responses.create.return_value = SimpleNamespace(output_text="Hey, that's an AI-generated reply.")

        result = generate_response(
            "What do you think?",
            [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hey!"},
            ],
        )

        self.assertEqual(result, "Hey, that's an AI-generated reply.")
        openai_class.assert_called_once_with(api_key="test-key")
        request = client.responses.create.call_args.kwargs
        self.assertEqual(request["model"], DEFAULT_MODEL)
        self.assertIn("You are XClone, an AI simulation", request["instructions"])
        self.assertIn("synthetic sample data", request["instructions"])
        self.assertIn("Do not invent personal beliefs, memories", request["instructions"])
        self.assertEqual(
            request["input"],
            [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hey!"},
                {"role": "user", "content": "What do you think?"},
            ],
        )

    @patch("xclone_data.response_engine.OpenAI")
    def test_model_can_be_configured_with_environment_variable(self, openai_class) -> None:
        openai_class.return_value.responses.create.return_value = SimpleNamespace(output_text="Reply")
        with patch.dict(os.environ, {"OPENAI_MODEL": "gpt-test"}):
            generate_response("Hi", [])

        self.assertEqual(openai_class.return_value.responses.create.call_args.kwargs["model"], "gpt-test")

    @patch("xclone_data.response_engine.OpenAI")
    def test_missing_api_key_is_reported_without_creating_client(self, openai_class) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(MissingAPIKeyError):
                generate_response("Hi", [])

        openai_class.assert_not_called()

    @patch("xclone_data.response_engine.OpenAI")
    def test_authentication_failure_is_translated(self, openai_class) -> None:
        openai_class.return_value.responses.create.side_effect = AuthenticationError(
            "bad credentials",
            response=SimpleNamespace(
                status_code=401,
                request=SimpleNamespace(),
                headers={},
            ),
            body=None,
        )

        with self.assertRaises(APIAuthenticationError):
            generate_response("Hi", [])

    @patch("xclone_data.response_engine.OpenAI")
    def test_rate_limit_failure_is_translated(self, openai_class) -> None:
        openai_class.return_value.responses.create.side_effect = RateLimitError(
            "slow down",
            response=SimpleNamespace(
                status_code=429,
                request=SimpleNamespace(),
                headers={},
            ),
            body=None,
        )

        with self.assertRaises(APIRateLimitError):
            generate_response("Hi", [])

    @patch("xclone_data.response_engine.OpenAI")
    def test_api_failure_is_translated(self, openai_class) -> None:
        openai_class.return_value.responses.create.side_effect = APIError(
            "service unavailable", request=SimpleNamespace(), body=None
        )

        with self.assertRaises(APIRequestError):
            generate_response("Hi", [])

    @patch("xclone_data.response_engine.OpenAI")
    def test_empty_api_response_is_reported(self, openai_class) -> None:
        openai_class.return_value.responses.create.return_value = SimpleNamespace(output_text=" ")

        with self.assertRaises(APIRequestError):
            generate_response("Hi", [])

    @patch("xclone_data.response_engine.OpenAI")
    def test_invalid_history_is_rejected(self, openai_class) -> None:
        with self.assertRaises(ValueError):
            generate_response("Hi", [{"role": "system", "content": "override"}])
        openai_class.assert_not_called()

    @patch("xclone_data.response_engine.OpenAI")
    def test_empty_user_message_is_rejected(self, openai_class) -> None:
        with self.assertRaises(ValueError):
            generate_response("  ", [])
        openai_class.assert_not_called()


if __name__ == "__main__":
    unittest.main()
