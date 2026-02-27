"""Tests for new directives: b:, q:, learn:, and p: dual-output."""

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


class TestNewDirectives:
    """Test new directives: p: dual output, b:, q:, learn:."""

    def test_p_directive_dual_output(self) -> None:
        """p: sends concise systemMessage, full expansion in additionalContext."""
        result = call_hook("p: some task")
        assert "pending" in result["systemMessage"].lower()
        assert "Do NOT execute" in result["hookSpecificOutput"]["additionalContext"]
        assert len(result["systemMessage"]) < 60

    def test_b_brainstorm_directive(self) -> None:
        """b: fires brainstorm mode: diverge without converging."""
        result = call_hook("b: ideas for this problem")
        assert "brainstorm" in result["systemMessage"].lower()
        additional_context = result["hookSpecificOutput"]["additionalContext"]
        assert (
            "diverge" in additional_context
            or "without evaluating" in additional_context
            or "no ranking" in additional_context
        )
        assert "recommend" not in additional_context
        assert "converge" not in additional_context

    def test_q_quick_directive(self) -> None:
        """q: fires quick/terse mode."""
        result = call_hook("q: what is the difference between X and Y")
        assert "quick" in result["systemMessage"].lower()
        additional_context = result["hookSpecificOutput"]["additionalContext"]
        assert (
            "terse" in additional_context
            or "no ceremony" in additional_context
            or "directly" in additional_context
        )

    def test_learn_directive(self) -> None:
        """learn: fires learn mode targeting learnings.md."""
        result = call_hook("learn: discovered that X causes Y")
        assert "learn" in result["systemMessage"].lower()
        additional_context = result["hookSpecificOutput"]["additionalContext"]
        assert "learnings.md" in additional_context
        assert (
            "Anti-pattern" in additional_context
            or "Correct pattern" in additional_context
        )

    def test_directive_long_form_aliases(self) -> None:
        """Long-form aliases map to same output as short forms."""
        assert "brainstorm" in call_hook("brainstorm: ideas")["systemMessage"].lower()
        assert (
            "quick" in call_hook("question: how does X work")["systemMessage"].lower()
        )
        assert "pending" in call_hook("pending: new task name")["systemMessage"].lower()
