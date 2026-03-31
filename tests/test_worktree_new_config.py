"""Tests for worktree new command - configuration and setup."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from edify.worktree.cli import worktree


def test_new_environment_initialization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Runs just setup in worktree if available."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    original_run = subprocess.run
    calls: list[tuple[list[str], dict[str, object]]] = []

    def mock_run(args, **kwargs) -> subprocess.CompletedProcess[str]:  # noqa: ANN001, ANN003
        calls.append((args, kwargs))
        if args == ["just", "--version"]:
            return subprocess.CompletedProcess(
                args=args, returncode=0, stdout="just 1.0\n", stderr=""
            )
        if args == ["just", "setup"]:
            return subprocess.CompletedProcess(
                args=args, returncode=0, stdout="", stderr=""
            )
        return original_run(args, **kwargs)

    monkeypatch.setattr("edify.worktree.cli.subprocess.run", mock_run)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "--branch", "test-setup"])
    assert result.exit_code == 0

    worktree_path = tmp_path / "repo-wt" / "test-setup"
    assert worktree_path.exists()

    assert any(c[0] == ["just", "--version"] for c in calls)
    assert any(
        c[0] == ["just", "setup"] and c[1].get("cwd") == worktree_path for c in calls
    )


def test_new_positional_task_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Positional arg creates worktree with session integration."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    (repo_path / "agents").mkdir()
    (repo_path / "agents" / "session.md").write_text(
        "# Session\n\n"
        "## Pending Tasks\n\n"
        "- [ ] **Other task** — `command` | haiku\n\n"
        "## Worktree Tasks\n\n"
        "- [ ] **Implement feature** — `command` | sonnet\n"
        "  - Plan: plans/test-plan\n"
    )
    subprocess.run(
        ["git", "add", "agents/session.md"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add session"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "Implement feature"])
    assert result.exit_code == 0
    assert (tmp_path / "repo-wt" / "implement-feature").exists()

    result = runner.invoke(worktree, ["new", "--help"])
    assert "--branch" in result.output
    assert "--session-md" in result.output


def test_new_session_handling_branch_reuse(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Warns and ignores --session when branch already exists."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)
    subprocess.run(["git", "branch", "test-feature"], check=True, capture_output=True)

    (repo_path / "agents").mkdir()
    session_file = repo_path / "agents" / "session.md"
    session_file.write_text("# Session\n\n## Pending Tasks\n\n- [ ] **Test** — test\n")

    runner = CliRunner()
    result = runner.invoke(
        worktree,
        ["new", "--branch", "test-feature", "--session", str(session_file)],
    )

    assert result.exit_code == 0
    assert "warning" in result.output.lower() or "exists" in result.output.lower()
    assert "session" in result.output.lower() or "ignored" in result.output.lower()

    container_path = tmp_path / "repo-wt"
    assert (container_path / "test-feature").exists()

    result = runner.invoke(worktree, ["new", "--branch", "new-branch"])
    assert result.exit_code == 0
    assert (container_path / "new-branch").exists()


def test_new_environment_init_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Warns when just setup fails but continues worktree creation."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    original_run = subprocess.run
    calls: list[tuple[list[str], dict[str, object]]] = []

    def mock_run(args, **kwargs) -> subprocess.CompletedProcess[str]:  # noqa: ANN001, ANN003
        calls.append((args, kwargs))
        if args == ["just", "--version"]:
            return subprocess.CompletedProcess(
                args=args, returncode=0, stdout="just 1.0\n", stderr=""
            )
        if args == ["just", "setup"]:
            return subprocess.CompletedProcess(
                args=args, returncode=1, stdout="", stderr="Setup failed"
            )
        return original_run(args, **kwargs)

    monkeypatch.setattr("edify.worktree.cli.subprocess.run", mock_run)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "--branch", "test-failure"])
    assert result.exit_code == 0

    worktree_path = tmp_path / "repo-wt" / "test-failure"
    assert worktree_path.exists()
    assert "warning" in result.output.lower() or "failed" in result.output.lower()


def test_new_copies_test_sentinel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Copies tmp/.test-sentinel to new worktree when it exists."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    # Create sentinel in source repo
    (repo_path / "tmp").mkdir()
    (repo_path / "tmp" / ".test-sentinel").write_text("12345 67")

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "--branch", "test-sentinel"])
    assert result.exit_code == 0

    wt_sentinel = tmp_path / "repo-wt" / "test-sentinel" / "tmp" / ".test-sentinel"
    assert wt_sentinel.exists()
    assert wt_sentinel.read_text() == "12345 67"


def test_new_no_sentinel_no_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """No error when tmp/.test-sentinel doesn't exist."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "--branch", "test-no-sentinel"])
    assert result.exit_code == 0

    wt_sentinel = tmp_path / "repo-wt" / "test-no-sentinel" / "tmp" / ".test-sentinel"
    assert not wt_sentinel.exists()


def test_new_container_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Container creation is idempotent with exist_ok=True."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    container_path = tmp_path / "repo-wt"
    container_path.mkdir()

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "--branch", "test-idempotent"])
    assert result.exit_code == 0

    assert (container_path / "test-idempotent").exists()
    result = runner.invoke(worktree, ["new", "--branch", "test-idempotent-2"])
    assert result.exit_code == 0
    assert (container_path / "test-idempotent-2").exists()
