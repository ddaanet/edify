"""Shared helpers for UserPromptSubmit hook tests."""

import importlib.util
import json
from io import StringIO
from pathlib import Path
from typing import Any
from unittest.mock import patch

# Import hook module using importlib (filename contains hyphen)
HOOK_PATH = (
    Path(__file__).parent.parent
    / "agent-core"
    / "hooks"
    / "userpromptsubmit-shortcuts.py"
)
spec = importlib.util.spec_from_file_location("hook_module", HOOK_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Failed to load hook module from {HOOK_PATH}")
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


def call_hook(prompt: str) -> dict[str, Any]:
    """Call hook with prompt, return parsed output or empty dict if exit 0."""
    hook_input = {"prompt": prompt}
    input_data = json.dumps(hook_input)

    captured_stdout = StringIO()
    captured_stderr = StringIO()

    with (
        patch("sys.stdin", StringIO(input_data)),
        patch("sys.stdout", captured_stdout),
        patch("sys.stderr", captured_stderr),
    ):
        try:
            hook.main()
        except SystemExit as e:
            if e.code == 0:
                return {}
            raise

    output_str = captured_stdout.getvalue()
    if not output_str:
        return {}

    result = json.loads(output_str)
    if not isinstance(result, dict):
        return {}
    return result
