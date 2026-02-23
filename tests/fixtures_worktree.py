"""Worktree-specific pytest fixtures and helpers."""

import subprocess
from collections.abc import Callable
from pathlib import Path
from unittest.mock import Mock

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree as worktree_cli

# ── Shared helpers (not fixtures, import directly) ──────────────────────


def _create_worktree(
    repo_path: Path, slug: str, init_repo: Callable[[Path], None]
) -> Path:
    """Create worktree via CLI and return its path."""
    runner = CliRunner()
    result = runner.invoke(worktree_cli, ["new", "--branch", slug])
    assert result.exit_code == 0
    container_path = repo_path.parent / f"{repo_path.name}-wt"
    return container_path / slug


def _branch_exists(name: str) -> bool:
    """Check if branch exists."""
    result = subprocess.run(
        ["git", "branch", "--list", name],
        capture_output=True,
        text=True,
        check=True,
    )
    return name in result.stdout


def _run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run git command in repo."""
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def _git_setup(*args: str) -> str:
    """Run git command in test setup; surface stderr on failure.

    Assumes cwd is set via monkeypatch.chdir. Returns stdout.
    """
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        msg = f"git {' '.join(args)} failed (exit {result.returncode}): {result.stderr}"
        raise RuntimeError(msg)
    return result.stdout


def make_repo_with_branch(  # noqa: PLR0913
    repo_dir: Path,
    init_fn: Callable[[Path], None],
    branch: str = "test-branch",
    *,
    files: dict[str, str] | None = None,
    empty_msg: str | None = None,
    n_commits: int = 0,
    diverge: bool = False,
    merge: bool = False,
) -> None:
    """Init repo, create branch with commits, optionally diverge/merge.

    Default: one file commit ("file.txt") on branch.
    """
    repo_dir.mkdir(exist_ok=True)
    if not (repo_dir / ".git").exists():
        init_fn(repo_dir)
    _run_git(repo_dir, "checkout", "-b", branch)
    if empty_msg:
        _run_git(repo_dir, "commit", "--allow-empty", "-m", empty_msg)
    elif files:
        for fname, content in files.items():
            (repo_dir / fname).write_text(content)
            _run_git(repo_dir, "add", fname)
            _run_git(repo_dir, "commit", "-m", f"Add {fname}")
    elif n_commits > 0:
        for i in range(n_commits):
            (repo_dir / f"file-{i}.txt").write_text(f"content {i}")
            _run_git(repo_dir, "add", f"file-{i}.txt")
            _run_git(repo_dir, "commit", "-m", f"Commit {i}")
    else:
        (repo_dir / "file.txt").write_text("branch content")
        _run_git(repo_dir, "add", ".")
        _run_git(repo_dir, "commit", "-m", "branch commit")
    _run_git(repo_dir, "checkout", "main")
    if diverge:
        (repo_dir / "other.txt").write_text("main content")
        _run_git(repo_dir, "add", ".")
        _run_git(repo_dir, "commit", "-m", "main commit")
    if merge:
        _run_git(repo_dir, "merge", "--no-edit", branch)


def add_worktree(repo_dir: Path, slug: str) -> Path:
    """Create git worktree for slug, return worktree path."""
    wt_dir = repo_dir / "wt" / slug
    wt_dir.parent.mkdir(parents=True, exist_ok=True)
    _run_git(repo_dir, "worktree", "add", str(wt_dir), slug)
    return wt_dir


def last_commit_subject(repo_dir: Path) -> str:
    """Get the subject line of the last commit."""
    return _run_git(repo_dir, "log", "-1", "--format=%s").stdout.strip()


# ── Fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
def mock_precommit(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock subprocess.run for 'just precommit' to return success.

    This fixture mocks the precommit validation step in merge operations to
    avoid requiring an actual justfile in test environments.
    """
    original_run = subprocess.run

    def mock_run(*args: object, **kwargs: object) -> object:
        cmd = args[0] if args else kwargs.get("args")
        if (
            isinstance(cmd, list)
            and cmd
            and cmd[0] == "just"
            and len(cmd) > 1
            and cmd[1] == "precommit"
        ):
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            mock_result.stderr = ""
            return mock_result
        return original_run(*args, **kwargs)  # type: ignore[call-overload]

    monkeypatch.setattr(subprocess, "run", mock_run)


@pytest.fixture
def init_repo() -> Callable[[Path], None]:
    """Return function to initialize git repo with config and commit."""

    def _init_repo(repo_path: Path) -> None:
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

    return _init_repo


@pytest.fixture
def repo_with_submodule(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create git repo with submodule and session files.

    Returns the main repo path. The repo has:
    - Initial commit with README.md
    - agent-core submodule initialized
    - agents/session.md, agents/learnings.md committed
    """
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    # Initialize main repo
    subprocess.run(["git", "init"], check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"], check=True, capture_output=True
    )

    # Create initial commit
    (repo_path / "README.md").write_text("test")
    subprocess.run(["git", "add", "README.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"], check=True, capture_output=True
    )

    # Initialize submodule (agent-core)
    submodule_path = repo_path / "agent-core"
    submodule_path.mkdir()
    subprocess.run(["git", "init"], cwd=submodule_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=submodule_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=submodule_path,
        check=True,
        capture_output=True,
    )
    (submodule_path / "README.md").write_text("submodule")
    subprocess.run(
        ["git", "add", "README.md"], cwd=submodule_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Submodule initial"],
        cwd=submodule_path,
        check=True,
        capture_output=True,
    )

    # Add submodule to main repo
    subprocess.run(
        ["git", "submodule", "add", str(submodule_path), "agent-core"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add submodule"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Add session files
    agents_dir = repo_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "session.md").write_text("# Session\n")
    (agents_dir / "learnings.md").write_text("# Learnings\n")
    subprocess.run(["git", "add", "agents/"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add session files"], check=True, capture_output=True
    )

    return repo_path


@pytest.fixture
def commit_file() -> Callable[[Path, str, str, str], None]:
    """Return function to create, stage, and commit a file."""

    def _commit_file(path: Path, filename: str, content: str, message: str) -> None:
        """Create, stage, and commit a file."""
        (path / filename).write_text(content)
        subprocess.run(
            ["git", "add", filename], cwd=path, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", message], cwd=path, check=True, capture_output=True
        )

    return _commit_file


@pytest.fixture
def setup_repo_with_submodule() -> Callable[[Path, Callable[[Path], None]], None]:
    """Return function to set up test repo with simulated submodule (gitlink).

    The submodule is created using git plumbing commands (gitlink).
    """

    def _setup(repo_path: Path, init_repo: Callable[[Path], None]) -> None:
        """Set up test repo with submodule using gitlink."""
        init_repo(repo_path)

        agent_core_path = repo_path / "agent-core"
        agent_core_path.mkdir()
        subprocess.run(
            ["git", "init"], cwd=agent_core_path, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=agent_core_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=agent_core_path,
            check=True,
            capture_output=True,
        )

        (agent_core_path / "core.txt").write_text("core content")
        subprocess.run(
            ["git", "add", "core.txt"],
            cwd=agent_core_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial core commit"],
            cwd=agent_core_path,
            check=True,
            capture_output=True,
        )

        (repo_path / ".gitmodules").write_text(
            '[submodule "agent-core"]\n\tpath = agent-core\n\turl = ./agent-core\n'
        )

        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=agent_core_path,
            capture_output=True,
            text=True,
            check=True,
        )
        commit_hash = result.stdout.strip()

        subprocess.run(
            [
                "git",
                "update-index",
                "--add",
                "--cacheinfo",
                f"160000,{commit_hash},agent-core",
            ],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "add", ".gitmodules"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Add submodule"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

        (repo_path / ".gitignore").write_text("wt/\n")
        subprocess.run(
            ["git", "add", ".gitignore"], cwd=repo_path, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Add gitignore"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

    return _setup
