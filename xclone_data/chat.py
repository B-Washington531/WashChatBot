"""Send one message to the XClone response engine from the command line."""

import sys

from .response_engine import ResponseEngineError, generate_response


def main() -> int:
    """Prompt for one message and print the AI-generated response."""
    try:
        user_message = input("You: ")
        response = generate_response(user_message, [])
    except (ResponseEngineError, TypeError, ValueError) as error:
        print(f"XClone error: {error}", file=sys.stderr)
        return 1
    except EOFError:
        print("No message was provided.", file=sys.stderr)
        return 1

    print(f"XClone (AI simulation): {response}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
