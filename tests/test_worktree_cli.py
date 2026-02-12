"""Tests for worktree CLI module."""

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import derive_slug, worktree, wt_path


def _init_repo(repo_path: Path) -> None:
    """Initialize git repo with user config and initial commit."""
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    (repo_path / "README.md").write_text("test")
    subprocess.run(
        ["git", "add", "README.md"], cwd=repo_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )


def test_package_import() -> None:
    """Verifies module loads."""
    assert worktree is not None


def test_worktree_command_group() -> None:
    """Help output includes command group name."""
    runner = CliRunner()
    result = runner.invoke(worktree, ["--help"])
    assert result.exit_code == 0
    assert "_worktree" in result.output


def test_derive_slug() -> None:
    """Transforms task names to slugs: lowercase, hyphens, 30 char limit."""
    assert derive_slug("Implement ambient awareness") == "implement-ambient-awareness"
    assert derive_slug("Design runbook identifiers") == "design-runbook-identifiers"
    assert (
        derive_slug("Review agent-core orphaned revisions")
        == "review-agent-core-orphaned-rev"
    )
    assert derive_slug("Multiple    spaces   here") == "multiple-spaces-here"
    assert derive_slug("Special!@#$%chars") == "special-chars"
    assert derive_slug("A" * 35 + "test") == "a" * 30


def test_ls_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Empty output when no worktrees exist."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _init_repo(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["ls"])
    assert result.exit_code == 0
    assert result.output == ""


def test_ls_multiple_worktrees(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Parses porcelain output and extracts slug from path."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _init_repo(repo_path)

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
    assert len(lines) == 2

    line_a = lines[0].split("\t")
    line_b = lines[1].split("\t")

    assert line_a[0] == "task-a"
    assert line_a[1] == "refs/heads/task-a"
    assert str(worktree_a) in line_a[2]

    assert line_b[0] == "task-b"
    assert line_b[1] == "refs/heads/task-b"
    assert str(worktree_b) in line_b[2]


def test_wt_path_not_in_container(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """wt_path() returns correct container path when repo not in -wt container.

    Verifies absolute path, correct slug, and -wt suffix on parent.
    """
    repo_path = tmp_path / "my-repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _init_repo(repo_path)

    result_path = wt_path("feature-a")

    assert result_path.is_absolute()
    assert result_path.name == "feature-a"
    assert result_path.parent.name.endswith("-wt")
    assert str(result_path).endswith("my-repo-wt/feature-a")


def test_wt_path_in_container(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """wt_path() detects when repo is already inside a -wt container.

    When cwd is inside a container, returns sibling path (not nested). Multiple
    slugs return different paths sharing same container parent.
    """
    container_path = tmp_path / "my-repo-wt"
    container_path.mkdir()
    repo_path = container_path / "main"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _init_repo(repo_path)

    path_a = wt_path("feature-a")
    path_b = wt_path("feature-b")

    assert path_a.is_absolute()
    assert path_b.is_absolute()

    assert path_a.name == "feature-a"
    assert path_b.name == "feature-b"

    assert path_a.parent == path_b.parent
    assert path_a.parent.name == "my-repo-wt"

    assert path_a != path_b
    assert str(path_a).endswith("my-repo-wt/feature-a")
    assert str(path_b).endswith("my-repo-wt/feature-b")

    assert "-wt/-wt" not in str(path_a)
    assert "-wt/-wt" not in str(path_b)


def test_new_session_precommit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Session file committed to worktree branch before worktree creation."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _init_repo(repo_path)

    session_file = tmp_path / "test-session.md"
    session_file.write_text("# Focused Session\n\nTask content")

    runner = CliRunner()
    result = runner.invoke(
        worktree, ["new", "test-feature", "--session", str(session_file)]
    )
    assert result.exit_code == 0

    worktree_path = repo_path / "wt" / "test-feature"
    assert worktree_path.exists()

    session_md_path = worktree_path / "agents" / "session.md"
    assert session_md_path.exists()
    assert session_md_path.read_text() == "# Focused Session\n\nTask content"

    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD..test-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    commits_ahead = int(result.stdout.strip())
    assert commits_ahead == 1

    result = subprocess.run(
        ["git", "diff", "--cached"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout == ""

    result = subprocess.run(
        ["git", "log", "-1", "--format=%s", "test-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    commit_msg = result.stdout.strip()
    assert commit_msg == "Focused session for test-feature"
