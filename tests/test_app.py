"""Tests for the XClone Streamlit interface and conversation flow."""

import unittest
from pathlib import Path
from unittest.mock import Mock

from streamlit.testing.v1 import AppTest

from app import respond_to_message

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


class ChatInterfaceTests(unittest.TestCase):
    def test_message_reaches_backend_with_prior_history_and_saves_reply(self) -> None:
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hey!"},
        ]
        generator = Mock(return_value="A mocked AI reply")

        response = respond_to_message("What's up?", history, generator)

        self.assertEqual(response, "A mocked AI reply")
        generator.assert_called_once_with("What's up?", [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hey!"},
        ])
        self.assertEqual(history[-2:], [
            {"role": "user", "content": "What's up?"},
            {"role": "assistant", "content": "A mocked AI reply"},
        ])

    def test_failed_response_keeps_user_message_without_fabricating_reply(self) -> None:
        history: list[dict[str, str]] = []
        generator = Mock(side_effect=RuntimeError("unavailable"))

        with self.assertRaisesRegex(RuntimeError, "unavailable"):
            respond_to_message("Are you there?", history, generator)

        self.assertEqual(history, [{"role": "user", "content": "Are you there?"}])

    def test_app_starts_and_clear_button_clears_session_history(self) -> None:
        app = AppTest.from_file(str(APP_PATH)).run()

        self.assertEqual(app.title[0].value, "XClone")
        self.assertEqual(app.caption[0].value, "AI Personality Simulation")
        self.assertEqual(app.session_state["messages"], [])

        app.session_state["messages"] = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "mocked reply"},
        ]
        app.run()
        app.button[0].click().run()

        self.assertEqual(app.session_state["messages"], [])
        self.assertFalse(app.exception)

    def test_app_displays_saved_messages_as_text(self) -> None:
        app = AppTest.from_file(str(APP_PATH))
        app.session_state["messages"] = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "<script>unsafe()</script>"},
        ]
        app.run()

        rendered_text = [element.value for element in app.text]
        self.assertIn("You: hello", rendered_text)
        self.assertIn("XClone (AI simulation): <script>unsafe()</script>", rendered_text)
        self.assertFalse(app.exception)


if __name__ == "__main__":
    unittest.main()
