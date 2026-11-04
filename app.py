"""Streamlit chat interface for the XClone AI personality simulation."""

import json
from pathlib import Path
from typing import Any, Callable

import streamlit as st

from xclone_data.response_engine import (
    APIAuthenticationError,
    APIRequestError,
    APIRateLimitError,
    MissingAPIKeyError,
    PersonalityProfileError,
    ResponseEngineError,
    generate_response,
)

PROFILE_PATH = Path(__file__).resolve().parent / "data" / "personality_profile.json"
ResponseGenerator = Callable[[str, list[dict[str, str]]], str]


def load_profile_summary() -> dict[str, Any]:
    """Read the existing personality profile without changing it."""
    try:
        with PROFILE_PATH.open(encoding="utf-8") as profile_file:
            profile = json.load(profile_file)
    except (OSError, json.JSONDecodeError) as error:
        raise PersonalityProfileError("The personality profile could not be loaded.") from error

    if not isinstance(profile, dict):
        raise PersonalityProfileError("The personality profile must contain a JSON object.")
    return profile


def respond_to_message(
    user_message: str,
    messages: list[dict[str, str]],
    response_generator: ResponseGenerator = generate_response,
) -> str:
    """Send a new user turn with prior history and save the resulting exchange."""
    history = list(messages)
    messages.append({"role": "user", "content": user_message})
    response = response_generator(user_message, history)
    if not isinstance(response, str) or not response.strip():
        raise APIRequestError("The response engine returned an empty response.")
    messages.append({"role": "assistant", "content": response})
    return response


def _show_engine_error(error: ResponseEngineError) -> None:
    if isinstance(error, MissingAPIKeyError):
        message = "The OpenAI API key is not configured. Set OPENAI_API_KEY and restart the app."
    elif isinstance(error, APIAuthenticationError):
        message = "OpenAI rejected the configured credentials. Check OPENAI_API_KEY."
    elif isinstance(error, APIRateLimitError):
        message = "The OpenAI rate limit was reached. Please wait a moment and try again."
    elif isinstance(error, (APIRequestError, PersonalityProfileError)):
        message = f"XClone could not complete the request: {error}"
    else:
        message = "XClone is temporarily unavailable. Please try again."
    st.error(message)


def main() -> None:
    st.set_page_config(page_title="XClone", page_icon="💬", layout="centered")
    st.title("XClone")
    st.caption("AI Personality Simulation")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.header("Personality profile")
        try:
            profile = load_profile_summary()
        except PersonalityProfileError as error:
            st.error(str(error))
        else:
            st.caption(f"Posts analyzed: {profile.get('tweet_count', 'unknown')}")
            topics = profile.get("frequently_discussed_topics", {}).get("topics", [])
            topic_names = [
                topic.get("topic")
                for topic in topics
                if isinstance(topic, dict) and isinstance(topic.get("topic"), str)
            ]
            if topic_names:
                st.write("Observed topics: " + ", ".join(topic_names))
            st.info("This profile is based on synthetic tweet data, not the real person's history.")

        if st.button("Clear conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    for message in st.session_state.messages:
        label = "XClone (AI simulation)" if message["role"] == "assistant" else "You"
        with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else None):
            st.text(f"{label}: {message['content']}")

    user_message = st.chat_input("Message XClone")
    if user_message:
        with st.chat_message("user"):
            st.text(f"You: {user_message}")

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("XClone is thinking..."):
                try:
                    response = respond_to_message(user_message, st.session_state.messages)
                except ResponseEngineError as error:
                    _show_engine_error(error)
                except (TypeError, ValueError):
                    st.error("The message or conversation history was invalid. Please try again.")
                else:
                    st.text(f"XClone (AI simulation): {response}")


if __name__ == "__main__":
    main()
