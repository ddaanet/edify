"""Tests for userpromptsubmit-shortcuts hook."""

import importlib.util
import json
from io import StringIO
from pathlib import Path

import pytest


# Import hook module using importlib (filename contains hyphen)
HOOK_PATH = Path(__file__).parent.parent / "agent-core" / "hooks" / "userpromptsubmit-shortcuts.py"
spec = importlib.util.spec_from_file_location("hook_module", HOOK_PATH)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


def call_hook(prompt: str) -> dict:
    """Call hook with prompt, return parsed output or empty dict if exit 0."""
    import sys
    from unittest.mock import patch

    hook_input = {"prompt": prompt}
    input_data = json.dumps(hook_input)

    # Capture stdout and stderr
    captured_stdout = StringIO()
    captured_stderr = StringIO()

    with patch("sys.stdin", StringIO(input_data)):
        with patch("sys.stdout", captured_stdout):
            with patch("sys.stderr", captured_stderr):
                try:
                    hook.main()
                except SystemExit as e:
                    if e.code == 0:
                        # Silent pass-through
                        return {}
                    raise

    # Parse output
    output_str = captured_stdout.getvalue()
    if not output_str:
        return {}

    return json.loads(output_str)


class TestLongFormAliases:
    """Test long-form directive aliases."""

    def test_long_form_aliases(self):
        """Test that discuss: and pending: produce same output as d: and p:."""
        # Test discuss: vs d:
        output_discuss = call_hook("discuss: some topic")
        output_d = call_hook("d: some topic")

        # Both should have same additionalContext
        assert "hookSpecificOutput" in output_discuss
        assert "hookSpecificOutput" in output_d
        assert output_discuss["hookSpecificOutput"]["additionalContext"] == output_d["hookSpecificOutput"]["additionalContext"]

        # Both should have same systemMessage
        assert output_discuss["systemMessage"] == output_d["systemMessage"]

        # Test pending: vs p:
        output_pending = call_hook("pending: new task")
        output_p = call_hook("p: new task")

        # Both should have same additionalContext
        assert "hookSpecificOutput" in output_pending
        assert "hookSpecificOutput" in output_p
        assert output_pending["hookSpecificOutput"]["additionalContext"] == output_p["hookSpecificOutput"]["additionalContext"]

        # Both should have same systemMessage
        assert output_pending["systemMessage"] == output_p["systemMessage"]
