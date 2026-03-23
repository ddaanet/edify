"""Tests for worktree utility functions."""

import json
import stat
from collections.abc import Callable
from pathlib import Path

import pytest

from claudeutils.git import _fail
from claudeutils.worktree.cli import add_sandbox_dir, derive_slug, focus_session
from claudeutils.worktree.git_ops import wt_path


def test_derive_slug() -> None:
    """Transforms task names to slugs."""
    assert derive_slug("Build docs") == "build-docs"
    assert derive_slug("Fix bug-123") == "fix-bug-123"
    assert derive_slug("Add v2.0 support") == "add-v2-0-support"
    assert derive_slug("a") == "a"
    assert derive_slug("Test   multiple   spaces") == "test-multiple-spaces"
    assert derive_slug("Feature-Name") == "feature-name"
    with pytest.raises(ValueError, match="task_name must not be empty"):
        derive_slug("")
    with pytest.raises(ValueError, match="task_name must not be empty"):
        derive_slug("   ")


def test_derive_slug_validates_format() -> None:
    """derive_slug validates task name format."""
    with pytest.raises(ValueError, match="forbidden character '_'"):
        derive_slug("task_name")

    with pytest.raises(ValueError, match="forbidden character '@'"):
        derive_slug("task@host")

    with pytest.raises(ValueError, match="exceeds 25 character limit"):
        derive_slug("This is a very long task name that exceeds limit")

    with pytest.raises(ValueError, match="empty"):
        derive_slug("")


def test_wt_path_not_in_container(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Container path when not in -wt."""
    repo_path = tmp_path / "my-repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    result_path = wt_path("feature-a")
    assert str(result_path).endswith("my-repo-wt/feature-a")


def test_wt_path_in_container(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Sibling path when in -wt container."""
    container_path = tmp_path / "my-repo-wt"
    container_path.mkdir()
    repo_path = container_path / "main"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    path_a = wt_path("feature-a")
    assert path_a.parent.name == "my-repo-wt"
    assert "-wt/-wt" not in str(path_a)


def test_wt_path_creates_container(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Creates container directory with create_container=True."""
    repo_path = tmp_path / "my-repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    container_path = repo_path.parent / "my-repo-wt"
    result_path = wt_path("feature-a", create_container=True)

    assert container_path.exists()
    assert result_path.parent == container_path
    assert stat.S_IMODE(container_path.stat().st_mode) == 0o755


def test_wt_path_edge_cases(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Edge cases: special characters, deep nesting, empty slug."""
    repo_path = tmp_path / "my-repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)
    assert "#123" in str(wt_path("fix-bug#123"))

    deep_path = tmp_path / "a" / "b" / "c" / "d" / "e" / "repo"
    deep_path.mkdir(parents=True)
    monkeypatch.chdir(deep_path)
    init_repo(deep_path)
    result = wt_path("nested-test")
    assert result.is_absolute()

    with pytest.raises(ValueError, match="slug"):
        wt_path("")
    with pytest.raises(ValueError, match="slug"):
        wt_path("   ")


def test_add_sandbox_dir_happy_path(tmp_path: Path) -> None:
    """Appends path to existing additionalDirectories array."""
    settings_file = tmp_path / "settings.json"
    initial_settings = {"permissions": {"additionalDirectories": ["/existing/path"]}}
    settings_file.write_text(json.dumps(initial_settings, indent=2))

    add_sandbox_dir("/new/path", settings_file)
    updated = json.loads(settings_file.read_text())
    assert updated["permissions"]["additionalDirectories"] == [
        "/existing/path",
        "/new/path",
    ]


def test_add_sandbox_dir_missing_file(tmp_path: Path) -> None:
    """Creates settings file from scratch when missing."""
    settings_file = tmp_path / "nonexistent" / "settings.json"
    add_sandbox_dir("/new/path", settings_file)
    created = json.loads(settings_file.read_text())
    assert created == {"permissions": {"additionalDirectories": ["/new/path"]}}


def test_add_sandbox_dir_missing_keys(tmp_path: Path) -> None:
    """Creates nested structure when JSON exists but keys missing."""
    settings_file = tmp_path / "empty.json"
    settings_file.write_text(json.dumps({}))
    add_sandbox_dir("/new/path", settings_file)
    result = json.loads(settings_file.read_text())
    assert result["permissions"]["additionalDirectories"] == ["/new/path"]

    settings_file.write_text(json.dumps({"permissions": {"other_key": "value"}}))
    add_sandbox_dir("/new/path", settings_file)
    result = json.loads(settings_file.read_text())
    assert result["permissions"]["additionalDirectories"] == ["/new/path"]
    assert result["permissions"]["other_key"] == "value"


def test_add_sandbox_dir_deduplication(tmp_path: Path) -> None:
    """Idempotent: existing paths not duplicated."""
    settings_file = tmp_path / "settings.json"
    initial_settings = {
        "permissions": {"additionalDirectories": ["/path/a", "/path/b"]}
    }
    settings_file.write_text(json.dumps(initial_settings, indent=2))

    add_sandbox_dir("/path/a", settings_file)
    result = json.loads(settings_file.read_text())
    assert result["permissions"]["additionalDirectories"] == ["/path/a", "/path/b"]

    add_sandbox_dir("/path/c", settings_file)
    add_sandbox_dir("/path/a", settings_file)
    result = json.loads(settings_file.read_text())
    assert result["permissions"]["additionalDirectories"] == [
        "/path/a",
        "/path/b",
        "/path/c",
    ]


def test_focus_session_task_extraction(tmp_path: Path) -> None:
    """Extract task block from session.md by matching task name."""
    session_file = tmp_path / "session.md"
    session_content = r"""# Session Handoff: 2026-02-12

## Worktree Tasks

- [ ] **Implement feature X** → `feature-x` — `\`/plan-adhoc\`` | sonnet
- [ ] **Fix bug Y** → `bug-y` — `\`/design\`` | haiku
"""
    session_file.write_text(session_content)
    result = focus_session("Implement feature X", session_file)
    assert "# Session: Worktree — Implement feature X" in result
    assert "**Status:** Focused worktree for parallel execution." in result
    assert r"- [ ] **Implement feature X** — `\`/plan-adhoc\`` | sonnet" in result
    assert "Fix bug Y" not in result


def test_focus_session_section_filtering(tmp_path: Path) -> None:
    """Filter blockers and references to only relevant entries."""
    session_file = tmp_path / "session.md"
    session_content = r"""# Session Handoff: 2026-02-12

## Worktree Tasks

- [ ] **Implement feature X** → `feature-x` — `\`/plan-adhoc\`` | sonnet
  - Plan: plans/feature-x/

## Blockers / Gotchas

- Implement feature X workflow depends on Phase 0 completion
- Unrelated issue: GPU memory constraints
- See plans/feature-x/ for implementation notes

## Reference Files

- `agents/decisions/implementation-notes.md` — General reference
- `plans/feature-x/design.md` — Design for feature X
- `plans/other-feature/design.md` — Unrelated design
"""
    session_file.write_text(session_content)
    result = focus_session("Implement feature X", session_file)

    assert "Implement feature X workflow depends on Phase 0 completion" in result
    assert "See plans/feature-x/ for implementation notes" in result
    assert "Unrelated issue: GPU memory constraints" not in result
    assert "Design for feature X" in result
    assert "Unrelated design" not in result


def test_focus_session_missing_task(tmp_path: Path) -> None:
    """Raise clear error when task name doesn't exist in session.md."""
    session_file = tmp_path / "session.md"
    session_file.write_text(
        "## Worktree Tasks\n\n- [ ] **Existing task** → `existing` — `/plan`"
    )

    with pytest.raises(
        ValueError, match=r"Task 'nonexistent-task' not found in session\.md"
    ):
        focus_session("nonexistent-task", session_file)


def test_fail_writes_to_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    """_fail prints message to stdout and raises SystemExit with code."""
    with pytest.raises(SystemExit) as exc_info:
        _fail("error message", 1)

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "error message" in captured.out
    assert captured.err == ""


def test_fail_default_code() -> None:
    """_fail defaults to exit code 1 when code not provided."""
    with pytest.raises(SystemExit) as exc_info:
        _fail("msg")

    assert exc_info.value.code == 1


def test_fail_custom_code() -> None:
    """_fail uses custom exit code when provided."""
    with pytest.raises(SystemExit) as exc_info:
        _fail("validation error", 2)

    assert exc_info.value.code == 2
