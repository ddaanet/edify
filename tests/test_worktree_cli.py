"""Tests for worktree CLI module."""

import json
import stat
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import (
    add_sandbox_dir,
    derive_slug,
    focus_session,
    worktree,
    wt_path,
)


def test_package_import() -> None:
    """Module loads."""
    assert worktree is not None


def test_worktree_command_group() -> None:
    """Help includes command group name."""
    runner = CliRunner()
    result = runner.invoke(worktree, ["--help"])
    assert result.exit_code == 0
    assert "_worktree" in result.output


def test_derive_slug() -> None:
    """Transforms task names to slugs."""
    assert derive_slug("Implement ambient awareness") == "implement-ambient-awareness"
    assert derive_slug("Design runbook identifiers") == "design-runbook-identifiers"
    assert (
        derive_slug("Review agent-core orphaned revisions")
        == "review-agent-core-orphaned-rev"
    )
    assert derive_slug("Multiple    spaces   here") == "multiple-spaces-here"
    assert derive_slug("Special!@#$%chars") == "special-chars"
    assert derive_slug("A" * 35 + "test") == "a" * 30
    assert derive_slug("feat: add login") == "feat-add-login"
    assert derive_slug("Feature-Name") == "feature-name"
    assert len(derive_slug("a" * 100)) <= 30
    assert not derive_slug("a" * 100).endswith("-")
    with pytest.raises(ValueError, match="task_name must not be empty"):
        derive_slug("")
    with pytest.raises(ValueError, match="task_name must not be empty"):
        derive_slug("   ")


def test_ls_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Empty output when no worktrees exist."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["ls"])
    assert result.exit_code == 0
    assert result.output == ""


def test_ls_multiple_worktrees(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Parses porcelain output and extracts slug from path."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    subprocess.run(["git", "branch", "task-a"], check=True, capture_output=True)
    subprocess.run(["git", "branch", "task-b"], check=True, capture_output=True)

    worktree_a = repo_path / "wt" / "task-a"
    worktree_b = repo_path / "wt" / "task-b"
    subprocess.run(
        ["git", "worktree", "add", str(worktree_a), "task-a"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "worktree", "add", str(worktree_b), "task-b"],
        check=True,
        capture_output=True,
    )

    runner = CliRunner()
    result = runner.invoke(worktree, ["ls"])
    assert result.exit_code == 0

    lines = result.output.strip().split("\n")
    line_a = lines[0].split("\t")
    line_b = lines[1].split("\t")

    assert line_a[0] == "task-a"
    assert line_a[1] == "refs/heads/task-a"
    assert line_b[0] == "task-b"
    assert line_b[1] == "refs/heads/task-b"


def test_wt_path_not_in_container(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Returns container path when repo not in -wt container."""
    repo_path = tmp_path / "my-repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    result_path = wt_path("feature-a")
    assert str(result_path).endswith("my-repo-wt/feature-a")


def test_wt_path_in_container(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Detects repo inside -wt container, returns sibling path."""
    container_path = tmp_path / "my-repo-wt"
    container_path.mkdir()
    repo_path = container_path / "main"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    path_a = wt_path("feature-a")
    assert path_a.parent.name == "my-repo-wt"
    assert "-wt/-wt" not in str(path_a)


def test_session_precommit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Session file committed to worktree branch before worktree creation."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    session_file = tmp_path / "test-session.md"
    session_file.write_text("# Focused Session\n\nTask content")

    runner = CliRunner()
    result = runner.invoke(
        worktree, ["new", "test-feature", "--session", str(session_file)]
    )
    assert result.exit_code == 0

    container_path = tmp_path / "repo-wt"
    worktree_path = container_path / "test-feature"
    session_md_path = worktree_path / "agents" / "session.md"
    assert session_md_path.read_text() == "# Focused Session\n\nTask content"

    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD..test-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert int(result.stdout.strip()) == 1

    result = subprocess.run(
        ["git", "log", "-1", "--format=%s", "test-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "Focused session for test-feature"


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

## Pending Tasks

- [ ] **Implement feature X** — `\`/plan-adhoc\`` | sonnet
- [ ] **Fix bug Y** — `\`/design\`` | haiku
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

## Pending Tasks

- [ ] **Implement feature X** — `\`/plan-adhoc\`` | sonnet | plan: plans/feature-x/

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
    session_file.write_text("## Pending Tasks\n\n- [ ] **Existing task** — `/plan`")

    with pytest.raises(
        ValueError, match=r"Task 'nonexistent-task' not found in session\.md"
    ):
        focus_session("nonexistent-task", session_file)


def test_task_mode_integration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Task mode: slug derivation, focused session, tab-separated output."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    session_file = repo_path / "agents" / "session.md"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_content = r"""# Session Handoff: 2026-02-12

## Pending Tasks

- [ ] **Implement feature X** — `\`/runbook\`` | sonnet
- [ ] **Fix bug Y** — `\`/design\`` | haiku
"""
    session_file.write_text(session_content)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "--task", "Implement feature X"])
    assert result.exit_code == 0

    lines = result.output.strip().split("\n")
    output_line = lines[-1]
    parts = output_line.split("\t")
    assert len(parts) == 2
    slug, _path_str = parts
    assert slug == "implement-feature-x"

    worktree_path = tmp_path / "repo-wt" / "implement-feature-x"
    session_md_path = worktree_path / "agents" / "session.md"

    session_content_created = session_md_path.read_text()
    assert "# Session: Worktree — Implement feature X" in session_content_created
    assert "Fix bug Y" not in session_content_created


def test_rm_command_path_resolution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Rm command uses wt_path() and warns about uncommitted changes."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-slug"])
    assert result.exit_code == 0

    worktree_path = wt_path("test-slug")
    assert worktree_path.exists()

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "test-slug"])
    assert result.exit_code == 0
    assert not worktree_path.exists()


def test_rm_command_dirty_tree_warning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Rm command warns when worktree has uncommitted changes."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-slug"])
    assert result.exit_code == 0

    worktree_path = wt_path("test-slug")

    test_file = worktree_path / "test.txt"
    test_file.write_text("uncommitted content")

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "test-slug"])
    assert result.exit_code == 0
    assert "Warning: worktree has" in result.output
    assert "uncommitted files" in result.output
    assert not worktree_path.exists()
