"""Tests for worktree CLI commands."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import _remove_worktrees, worktree, wt_path


def test_package_import() -> None:
    """Module loads."""
    assert worktree is not None


def test_worktree_command_group() -> None:
    """Help includes command group name."""
    runner = CliRunner()
    result = runner.invoke(worktree, ["--help"])
    assert result.exit_code == 0
    assert "_worktree" in result.output


def test_ls_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Empty when no worktrees."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    result = CliRunner().invoke(worktree, ["ls"])
    assert result.exit_code == 0
    assert result.output == ""


def test_ls_multiple_worktrees(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Parses porcelain, extracts slug and branch."""
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

    result = CliRunner().invoke(worktree, ["ls"])
    assert result.exit_code == 0

    lines = result.output.strip().split("\n")
    line_a = lines[0].split("\t")
    line_b = lines[1].split("\t")

    assert line_a[0] == "task-a"
    assert line_a[1] == "refs/heads/task-a"
    assert line_b[0] == "task-b"
    assert line_b[1] == "refs/heads/task-b"


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

    result = CliRunner().invoke(
        worktree, ["new", "test-feature", "--session", str(session_file)]
    )
    assert result.exit_code == 0

    session_md_path = tmp_path / "repo-wt" / "test-feature" / "agents" / "session.md"
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

    result = CliRunner().invoke(worktree, ["new", "--task", "Implement feature X"])
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

    result = CliRunner().invoke(worktree, ["new", "test-slug"])
    assert result.exit_code == 0

    worktree_path = wt_path("test-slug")
    assert worktree_path.exists()

    result = CliRunner().invoke(worktree, ["rm", "test-slug"])
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

    result = CliRunner().invoke(worktree, ["new", "test-slug"])
    assert result.exit_code == 0

    worktree_path = wt_path("test-slug")
    test_file = worktree_path / "test.txt"
    test_file.write_text("uncommitted content")

    result = CliRunner().invoke(worktree, ["rm", "test-slug"])
    assert result.exit_code == 0
    assert "Warning: worktree has" in result.output
    assert "uncommitted files" in result.output
    assert not worktree_path.exists()


def test_rm_worktree_registration_probing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, repo_with_submodule: Path
) -> None:
    """Rm command detects parent and submodule worktree registration states."""
    monkeypatch.chdir(repo_with_submodule)

    result = CliRunner().invoke(worktree, ["new", "test-slug"])
    assert result.exit_code == 0

    worktree_path = wt_path("test-slug")
    assert worktree_path.exists()

    parent_list = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert str(worktree_path) in parent_list

    submodule_list = subprocess.run(
        ["git", "-C", "agent-core", "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert str(worktree_path / "agent-core") in submodule_list

    result = CliRunner().invoke(worktree, ["rm", "test-slug"])
    assert result.exit_code == 0
    assert not worktree_path.exists()

    parent_list_after = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert str(worktree_path) not in parent_list_after

    submodule_list_after = subprocess.run(
        ["git", "-C", "agent-core", "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert str(worktree_path / "agent-core") not in submodule_list_after


def test_rm_submodule_first_ordering(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Removal order: submodule worktree removed first, parent worktree second."""
    call_sequence: list[list[str]] = []

    def mock_run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        call_sequence.append(args)
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", mock_run)

    worktree_path = tmp_path / "wt" / "test-slug"
    worktree_path.mkdir(parents=True)

    _remove_worktrees(
        worktree_path,
        parent_registered=True,
        submodule_registered=True,
    )

    assert len(call_sequence) == 2
    submodule_cmd = call_sequence[0]
    parent_cmd = call_sequence[1]

    assert submodule_cmd[1] == "-C"
    assert submodule_cmd[2] == "agent-core"
    assert submodule_cmd[3] == "worktree"
    assert submodule_cmd[4] == "remove"
    assert submodule_cmd[5] == "--force"

    assert parent_cmd[0] == "git"
    assert parent_cmd[1] == "worktree"
    assert parent_cmd[2] == "remove"
    assert parent_cmd[3] == "--force"
