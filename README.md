# WashChatBot

## Local tweet data pipeline

The data pipeline uses Python's standard library and SQLite. Initialize and
populate the local database with 15 synthetic tweets:

```sh
python -m xclone_data
```

This creates `data/xclone.sqlite3`, which is ignored by Git. Run the tests with:

```sh
python -m unittest discover -s tests
```

Generate a rule-based profile from the stored tweets with:

```sh
python -m xclone_data.analyze
```

The generated `data/personality_profile.json` is ignored by Git. The analyzer
reports measurable text patterns separately from interpretations and labels
the bundled sample as synthetic data.

## OpenAI response engine

Install the OpenAI Python SDK:

```sh
python -m pip install -r requirements.txt
```

Set `OPENAI_API_KEY` in your environment; the key is never stored in the
project. Optionally set `OPENAI_MODEL` to choose another supported model (the
default is `gpt-4.1-mini`). On macOS or Linux, for example:

```sh
export OPENAI_API_KEY="your-api-key"
export OPENAI_MODEL="gpt-4.1-mini"
python -m xclone_data.chat
```

The CLI sends one message to the OpenAI Responses API and displays the result
as an AI simulation. The engine reads the existing
`data/personality_profile.json` without changing it, and does not send
conversation history unless the caller supplies it to `generate_response`.

Run the automated tests with:

```sh
python -m unittest discover -s tests
```

All response-engine tests mock the OpenAI client; they do not make API calls or
incur charges. Run `python -m xclone_data.chat` separately when you intend to
make a live API request.

## Streamlit chat interface

With dependencies installed and `OPENAI_API_KEY` set, start the interface from
the project root:

```sh
streamlit run app.py
```

Conversation messages are kept in Streamlit session state and can be cleared
from the sidebar. The interface displays responses as plain text and shows
the profile's synthetic-data notice.