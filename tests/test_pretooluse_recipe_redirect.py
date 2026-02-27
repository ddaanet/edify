"""Tests for pretooluse-recipe-redirect hook."""

import importlib.util
import json
import types
from io import StringIO
from pathlib import Path
from typing import Any
from unittest.mock import patch

HOOK_PATH = (
    Path(__file__).parent.parent
    / "agent-core"
    / "hooks"
    / "pretooluse-recipe-redirect.py"
)


def _load_hook() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(
        "pretooluse_recipe_redirect", HOOK_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load hook module from {HOOK_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def call_hook(hook_input: dict[str, Any]) -> dict[str, Any]:
    """Call hook with tool input dict.

    Returns parsed JSON output or empty dict on exit 0 with no output.
    """
    hook = _load_hook()
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
                output_str = captured_stdout.getvalue()
                if not output_str:
                    return {}
                result = json.loads(output_str)
                return result if isinstance(result, dict) else {}
            raise

    output_str = captured_stdout.getvalue()
    if not output_str:
        return {}
    result = json.loads(output_str)
    return result if isinstance(result, dict) else {}


class TestScriptLoads:
    """Verify script file exists and loads without errors."""

    def test_script_loads(self) -> None:
        """Hook path resolves and module imports without error."""
        assert HOOK_PATH.exists()
        _load_hook()


class TestPassThrough:
    """Verify non-redirect commands produce no output (silent pass-through)."""

    def test_unknown_command_silent_passthrough(self) -> None:
        """Non-redirect commands exit 0 with empty output."""
        assert (
            call_hook({"tool_name": "Bash", "tool_input": {"command": "echo hello"}})
            == {}
        )
        assert (
            call_hook({"tool_name": "Bash", "tool_input": {"command": "pytest tests/"}})
            == {}
        )
        assert (
            call_hook({"tool_name": "Bash", "tool_input": {"command": "just test"}})
            == {}
        )

    def test_missing_command_field_passthrough(self) -> None:
        """Missing tool_input or command key produces no output."""
        assert call_hook({"tool_name": "Bash", "tool_input": {}}) == {}
        assert call_hook({"tool_name": "Bash"}) == {}


class TestOutputFormat:
    """Verify output JSON structure matches PreToolUse hook contract."""

    def test_output_format_when_match_exists(self) -> None:
        """Redirect output matches PreToolUse hook JSON contract."""
        result = call_hook(
            {"tool_name": "Bash", "tool_input": {"command": "ln -sf src dest"}}
        )
        assert "hookSpecificOutput" in result
        assert result["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
        assert "additionalContext" in result["hookSpecificOutput"]
        assert result["hookSpecificOutput"]["additionalContext"] != ""
        assert "systemMessage" in result


class TestRedirectPatterns:
    """All three redirect patterns fire with correct additionalContext."""

    def test_ln_command_redirect(self) -> None:
        """Ln redirects to just sync-to-parent."""
        result = call_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "ln -sf agent-core/skills .claude/skills"},
            }
        )
        assert result
        assert (
            "just sync-to-parent" in result["hookSpecificOutput"]["additionalContext"]
        )
        assert result["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
        assert "systemMessage" in result

    def test_ln_bare_command_redirect(self) -> None:
        """Bare ln with no args still redirects."""
        result = call_hook({"tool_name": "Bash", "tool_input": {"command": "ln"}})
        assert (
            "just sync-to-parent" in result["hookSpecificOutput"]["additionalContext"]
        )

    def test_git_worktree_redirect(self) -> None:
        """Git worktree redirects to _worktree, not _worktree merge."""
        result = call_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "git worktree add --detach ../my-task HEAD"},
            }
        )
        assert result
        assert (
            "claudeutils _worktree" in result["hookSpecificOutput"]["additionalContext"]
        )
        assert (
            "claudeutils _worktree merge"
            not in result["hookSpecificOutput"]["additionalContext"]
        )

    def test_git_merge_redirect(self) -> None:
        """Git merge redirects to claudeutils _worktree merge."""
        result = call_hook(
            {"tool_name": "Bash", "tool_input": {"command": "git merge main"}}
        )
        assert result
        assert (
            "claudeutils _worktree merge"
            in result["hookSpecificOutput"]["additionalContext"]
        )

    def test_passthrough_non_redirect_commands(self) -> None:
        """Non-redirect commands produce no output."""
        assert (
            call_hook({"tool_name": "Bash", "tool_input": {"command": "git status"}})
            == {}
        )
        assert (
            call_hook(
                {"tool_name": "Bash", "tool_input": {"command": "git log --oneline"}}
            )
            == {}
        )
        assert (
            call_hook({"tool_name": "Bash", "tool_input": {"command": "pytest tests/"}})
            == {}
        )
        assert (
            call_hook({"tool_name": "Bash", "tool_input": {"command": "just test"}})
            == {}
        )
        assert (
            call_hook(
                {
                    "tool_name": "Bash",
                    "tool_input": {"command": "git merge-base HEAD main"},
                }
            )
            == {}
        )
