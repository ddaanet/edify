"""Tests for submodule-safety.py PreToolUse hook — cd && pattern support."""

from __future__ import annotations

import importlib.util
import types
from pathlib import Path
from typing import Any

import pytest

_hook_path = (
    Path(__file__).parent.parent / "plugin" / "hooks" / "submodule-safety.py"
)
_spec = importlib.util.spec_from_file_location("submodule_safety", _hook_path)
assert _spec is not None
assert _spec.loader is not None
submodule_safety: types.ModuleType = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(submodule_safety)

ROOT = "/Users/test/project"
WRONG = "/Users/test/other"


def _make_hook_input(command: str) -> dict[str, Any]:
    """Build a PreToolUse hook input dict."""
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "cwd": WRONG,
        "tool_input": {"command": command},
    }


def _run(command: str) -> int | None:
    """Run handle_pretooluse, return exit code."""
    try:
        submodule_safety.handle_pretooluse(_make_hook_input(command), WRONG, ROOT)
    except SystemExit as e:
        code = e.code
        return code if isinstance(code, int) else -1
    return None


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        # Bare cd restore (existing behavior)
        (f"cd {ROOT}", 0),
        (f'cd "{ROOT}"', 0),
        (f"cd '{ROOT}'", 0),
        # cd && compound pattern (FR-1)
        (f"cd {ROOT} && git status", 0),
        (f"cd {ROOT} && git add . && git commit -m 'msg'", 0),
        (f"cd {ROOT} && pytest tests/", 0),
        # Quoting/whitespace variants (FR-3)
        (f'cd "{ROOT}" && git status', 0),
        (f"cd '{ROOT}' && git status", 0),
        (f"cd {ROOT}&& git status", 0),
        (f"cd {ROOT}  &&  git status", 0),
    ],
    ids=[
        "bare-cd",
        "bare-cd-dquote",
        "bare-cd-squote",
        "cd-and-single",
        "cd-and-chain",
        "cd-and-pytest",
        "dquote-and",
        "squote-and",
        "no-space-amp",
        "extra-space-amp",
    ],
)
def test_allowed(command: str, expected: int) -> None:
    """Commands that restore cwd to project root are allowed."""
    assert _run(command) == expected


@pytest.mark.parametrize(
    "command",
    [
        # Wrong cwd, no restore
        "git status",
        "cd /somewhere/else",
        # Wrong path in cd && pattern
        "cd /somewhere/else && git status",
        # Security: path traversal
        f"cd {ROOT}/../evil && bad_cmd",
        # Security: partial path match
        f"cd {ROOT}-extra && cmd",
        f"cd {ROOT}/subdir && cmd",
        # Security: semicolon separator
        f"cd {ROOT} ; evil_cmd",
    ],
    ids=[
        "no-cd",
        "wrong-path-bare",
        "wrong-path-and",
        "path-traversal",
        "partial-match",
        "subdirectory",
        "semicolon",
    ],
)
def test_blocked(command: str) -> None:
    """Commands without valid cd-to-root prefix are blocked."""
    assert _run(command) == 2
