"""Tests for worktree new command - creation and collision handling."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree


def test_new_collision_detection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Reuses existing branch without error."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)
    subprocess.run(["git", "branch", "test-feature"], check=True, capture_output=True)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "--branch", "test-feature"])

    assert result.exit_code == 0
    assert (tmp_path / "repo-wt" / "test-feature").exists()


def test_new_directory_collision(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Detects existing directory collision."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    container_path = tmp_path / "repo-wt"
    container_path.mkdir()
    (container_path / "test-feature").mkdir()

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "--branch", "test-feature"])

    assert result.exit_code == 1
    assert "existing" in result.output.lower() or "directory" in result.output.lower()
    result = subprocess.run(
        ["git", "branch", "--list", "test-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-feature" not in result.stdout


def test_new_basic_flow(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Creates worktree with new branch in sibling container."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "--branch", "test-feature"])
    assert result.exit_code == 0
    assert "repo-wt/test-feature" in result.output

    worktree_path = tmp_path / "repo-wt" / "test-feature"
    assert worktree_path.exists()

    branch_result = subprocess.run(
        ["git", "branch", "--list", "test-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-feature" in branch_result.stdout

    head_result = subprocess.run(
        ["git", "-C", str(worktree_path), "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-feature" in head_result.stdout


def test_new_command_sibling_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Creates multiple worktrees in sibling container."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "--branch", "test-wt"])
    assert result.exit_code == 0

    container_path = tmp_path / "repo-wt"
    assert (container_path / "test-wt").exists()
    assert "repo-wt/test-wt" in result.output

    branch_result = subprocess.run(
        ["git", "branch", "--list", "test-wt"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-wt" in branch_result.stdout

    result = runner.invoke(worktree, ["new", "--branch", "another-wt"])
    assert result.exit_code == 0
    assert (container_path / "another-wt").exists()
    assert "repo-wt/another-wt" in result.output

    subprocess.run(
        ["git", "branch", "existing-branch"], check=True, capture_output=True
    )
    result = runner.invoke(worktree, ["new", "--branch", "existing-branch"])
    assert result.exit_code == 0
    assert (container_path / "existing-branch").exists()
    assert "repo-wt/existing-branch" in result.output


def test_new_task_commits_session_md(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """After new with task name, session.md is tracked on main."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    (repo_path / "agents").mkdir()
    (repo_path / "agents" / "session.md").write_text(
        "# Session\n\n## Pending Tasks\n\n- [ ] **My task** — `cmd` | sonnet\n"
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
    result = runner.invoke(worktree, ["new", "My task"])
    assert result.exit_code == 0

    # session.md should be tracked (move_task_to_worktree modifies it)
    status = subprocess.run(
        ["git", "status", "--porcelain", "agents/session.md"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    # Modified but tracked — should show "M" not "??"
    if status.stdout.strip():
        assert "??" not in status.stdout


def test_new_no_args_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """No task name and no --branch → usage error."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new"])

    assert result.exit_code != 0


def test_new_task_name_with_branch_override(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Task name + --branch: custom slug override with session integration."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    (repo_path / "agents").mkdir()
    (repo_path / "agents" / "session.md").write_text(
        "# Session\n\n## Pending Tasks\n\n"
        "- [ ] **Runbook quality gates Phase B** — `cmd` | sonnet\n"
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

    moved = []
    monkeypatch.setattr(
        "claudeutils.worktree.cli.move_task_to_worktree",
        lambda path, task, slug: moved.append((task, slug)),
    )

    runner = CliRunner()
    result = runner.invoke(
        worktree,
        ["new", "Runbook quality gates Phase B", "--branch", "runbook-quality-gates"],
    )

    assert result.exit_code == 0
    assert (tmp_path / "repo-wt" / "runbook-quality-gates").exists()
    assert len(moved) == 1
    assert moved[0] == ("Runbook quality gates Phase B", "runbook-quality-gates")


def test_new_positional_task_name_derives_slug_with_session(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Positional arg = task name: derives slug, calls move_task_to_worktree."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    (repo_path / "agents").mkdir()
    (repo_path / "agents" / "session.md").write_text(
        "# Session\n\n## Pending Tasks\n\n- [ ] **My task** — `cmd` | sonnet\n"
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

    moved = []
    monkeypatch.setattr(
        "claudeutils.worktree.cli.move_task_to_worktree",
        lambda path, task, slug: moved.append((task, slug)),
    )

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "My task"])

    assert result.exit_code == 0
    assert (tmp_path / "repo-wt" / "my-task").exists()
    assert len(moved) == 1
    assert moved[0] == ("My task", "my-task")


def test_new_branch_creates_worktree_without_session_or_sandbox(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """--branch creates bare worktree: no session, no sandbox."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "--branch", "my-feature"])

    assert result.exit_code == 0
    assert (tmp_path / "repo-wt" / "my-feature").exists()
    # No session.md touched
    assert not (repo_path / "agents" / "session.md").exists()
    # No sandbox registration
    assert not (repo_path / ".claude" / "settings.local.json").exists()
    wt_settings = (
        tmp_path / "repo-wt" / "my-feature" / ".claude" / "settings.local.json"
    )
    assert not wt_settings.exists()


def test_new_cleans_up_on_git_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Cleans up empty directory when git worktree add fails."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    monkeypatch.setattr(
        "claudeutils.worktree.cli._setup_worktree",
        lambda *a, **kw: (_ for _ in ()).throw(
            subprocess.CalledProcessError(255, "git worktree add")
        ),
    )

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "--branch", "test-feature"])

    assert result.exit_code != 0

    container = repo_path.parent / f"{repo_path.name}-wt"
    wt = container / "test-feature"
    assert not wt.exists(), "worktree directory should be cleaned up"
    assert not container.exists(), "empty container should be cleaned up"


def test_new_invalid_task_name_clean_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Invalid task name produces clean error with exit code 2."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "task_with_underscore"])

    assert result.exit_code == 2
    assert "forbidden character '_'" in result.output
    assert "Traceback" not in result.output
    assert "ValueError" not in result.output
