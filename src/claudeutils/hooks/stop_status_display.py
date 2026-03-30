"""Stop hook for displaying status on session interrupt.

Detects "Status." message and displays current CLI status output. Includes loop
guard to prevent redirect cycles when stop hook itself redirects.
"""

import json
import re
import subprocess
import sys
from collections.abc import Callable


def should_trigger(message: str) -> bool:
    """Check if message should trigger status display.

    Returns True if message is exactly "Status." (start of line, period
    required). Multiline messages and partial matches are not treated as
    triggers.
    """
    return bool(re.fullmatch(r"Status\.\Z", message))


def get_status(
    cmd: tuple[str, ...] = ("claudeutils", "_status"),
) -> str:
    """Run status CLI and return output.

    Args:
        cmd: Command tuple to run (default: claudeutils _status)

    Returns:
        Command stdout as string

    Raises:
        subprocess.CalledProcessError: If command fails
    """
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def format_ansi(text: str) -> str:
    """Prepend ANSI reset to each line.

    Ensures status output has consistent formatting by resetting ANSI state at
    the start of each line.
    """
    lines = text.splitlines(keepends=True)
    reset = "\033[0m"
    return reset + reset.join(lines)


def process_hook(
    data: dict[str, object],
    status_fn: Callable[[], str] | None = None,
) -> dict[str, str] | None:
    """Process stop hook request.

    Orchestrates: guard against redirect loops, detect trigger,
    fetch status, format output, return hook response.

    Args:
        data: Hook input dict with last_assistant_message and
              stop_hook_active
        status_fn: Callable to fetch status (default: get_status)

    Returns:
        Hook response dict with systemMessage, or None if not
        triggered or loop guard active
    """
    if data.get("stop_hook_active"):
        return None

    message = data.get("last_assistant_message", "")
    if not isinstance(message, str):
        return None

    if not should_trigger(message):
        return None

    status_fn = status_fn or get_status
    try:
        status_text = status_fn()
    except subprocess.CalledProcessError, OSError, RuntimeError:
        status_text = "Status unavailable"
    formatted = format_ansi(status_text)
    return {
        "systemMessage": formatted,
        "additionalContext": "Status displayed via Stop hook.",
    }


def main() -> None:
    """Read hook input from stdin, process, write response to stdout.

    Input: JSON with last_assistant_message and stop_hook_active.
    Output: JSON response dict or empty object if None returned.
    """
    data = json.loads(input())
    result = process_hook(data)
    json.dump(result or {}, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
