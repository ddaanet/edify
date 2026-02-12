"""Tests for worktree new subcommand."""

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree


def _init_git_repo(repo_path: Path) -> None:
    """Initialize a basic git repository.

    Args:
        repo_path: Root directory for the git repository.
    """
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


def _setup_repo_with_submodule(repo_path: Path) -> None:
    """Set up a test repo with a simulated submodule (gitlink).

    Args:
        repo_path: Root directory for the test repository.
    """
    _init_git_repo(repo_path)

    # Create initial commit
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

    # Create agent-core submodule
    agent_core_path = repo_path / "agent-core"
    agent_core_path.mkdir()
    _init_git_repo(agent_core_path)

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

    # Create .gitmodules
    gitmodules_path = repo_path / ".gitmodules"
    gitmodules_path.write_text(
        '[submodule "agent-core"]\n\tpath = agent-core\n\turl = ./agent-core\n'
    )

    # Create a gitlink entry in the index (simulates submodule)
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
        ["git", "add", ".gitmodules"], cwd=repo_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Add submodule"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Add .gitignore with wt/ entry
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


def test_new_collision_detection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify new subcommand reuses existing branch (no error)."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _init_git_repo(repo_path)

    # Create initial commit
    (repo_path / "README.md").write_text("test")
    subprocess.run(["git", "add", "README.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"], check=True, capture_output=True
    )

    # Create an existing branch
    subprocess.run(["git", "branch", "test-feature"], check=True, capture_output=True)

    # Run new command with existing branch name - should succeed and reuse branch
    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])

    assert result.exit_code == 0
    container_path = tmp_path / "repo-wt"
    worktree_path = container_path / "test-feature"
    assert worktree_path.exists()


def test_new_directory_collision(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify directory collision detection in sibling container."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _init_git_repo(repo_path)

    # Create initial commit
    (repo_path / "README.md").write_text("test")
    subprocess.run(["git", "add", "README.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"], check=True, capture_output=True
    )

    # Create an existing directory at repo-wt/test-feature
    container_path = tmp_path / "repo-wt"
    container_path.mkdir()
    (container_path / "test-feature").mkdir()

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])

    assert result.exit_code == 1
    assert "existing" in result.output.lower() or "directory" in result.output.lower()

    result = subprocess.run(
        ["git", "branch", "--list", "test-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-feature" not in result.stdout


def test_new_basic_flow(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify worktree creation with branch in sibling container."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _init_git_repo(repo_path)

    # Create initial commit
    (repo_path / "README.md").write_text("test")
    subprocess.run(["git", "add", "README.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"], check=True, capture_output=True
    )

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])

    assert result.exit_code == 0
    assert "repo-wt/test-feature" in result.output

    container_path = tmp_path / "repo-wt"
    worktree_path = container_path / "test-feature"
    assert worktree_path.exists()
    assert worktree_path.is_dir()

    result = subprocess.run(
        ["git", "branch", "--list", "test-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-feature" in result.stdout

    result = subprocess.run(
        ["git", "-C", str(worktree_path), "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-feature" in result.stdout


def test_new_submodule(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify new subcommand initializes submodule and creates branch.

    When creating a worktree in a repo with agent-core submodule:
    - Worktree created at sibling -wt container
    - Submodule is initialized via git submodule update
    - Submodule is on a branch matching the worktree slug (not detached HEAD)
    """
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _setup_repo_with_submodule(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])

    assert result.exit_code == 0

    container_path = tmp_path / "repo-wt"
    worktree_path = container_path / "test-feature"
    assert worktree_path.exists()
    assert worktree_path.is_dir()

    submodule_path = worktree_path / "agent-core"
    assert submodule_path.exists()

    result = subprocess.run(
        [
            "git",
            "-C",
            str(submodule_path),
            "rev-parse",
            "--abbrev-ref",
            "HEAD",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    branch_name = result.stdout.strip()
    assert branch_name == "test-feature"

    result = subprocess.run(
        ["git", "-C", str(submodule_path), "branch", "--list"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-feature" in result.stdout


def test_new_command_sibling_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Create worktree at sibling -wt paths and reuse existing branches.

    - Worktree at <repo>-wt/slug not wt/slug
    - Container directory created if needed
    - Existing branches reused (no -b flag)
    - New branches created with -b flag
    """
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _init_git_repo(repo_path)

    # Create initial commit
    (repo_path / "README.md").write_text("test")
    subprocess.run(["git", "add", "README.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"], check=True, capture_output=True
    )

    runner = CliRunner()

    # Test 1: Create new worktree (new branch)
    result = runner.invoke(worktree, ["new", "test-wt"])
    assert result.exit_code == 0

    container_path = tmp_path / "repo-wt"
    worktree_path = container_path / "test-wt"
    assert worktree_path.exists()
    assert worktree_path.is_dir()
    assert container_path.exists()

    # Verify output shows sibling path
    assert "repo-wt/test-wt" in result.output

    # Verify branch was created
    result = subprocess.run(
        ["git", "branch", "--list", "test-wt"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-wt" in result.stdout

    # Test 2: Create second new worktree (new branch), container already exists
    result = runner.invoke(worktree, ["new", "another-wt"])
    assert result.exit_code == 0

    worktree_path2 = container_path / "another-wt"
    assert worktree_path2.exists()
    assert "repo-wt/another-wt" in result.output

    # Test 3: Reuse existing branch (no error, uses branch without -b flag)
    # Create an existing branch in main repo first
    subprocess.run(
        ["git", "branch", "existing-branch"], check=True, capture_output=True
    )

    result = runner.invoke(worktree, ["new", "existing-branch"])
    assert result.exit_code == 0

    worktree_path3 = container_path / "existing-branch"
    assert worktree_path3.exists()
    assert "repo-wt/existing-branch" in result.output
