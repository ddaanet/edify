"""Tests for worktree new subcommand."""

import json
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree


def _init_git_repo(repo_path: Path) -> None:
    """Initialize git repository with user config."""
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
    """Set up repo with agent-core submodule."""
    _init_git_repo(repo_path)
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

    agent_core_path = repo_path / "agent-core"
    agent_core_path.mkdir()
    _init_git_repo(agent_core_path)
    (agent_core_path / "core.txt").write_text("core content")
    subprocess.run(
        ["git", "add", "core.txt"], cwd=agent_core_path, check=True, capture_output=True
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
        ["git", "add", ".gitmodules"], cwd=repo_path, check=True, capture_output=True
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


def test_new_collision_detection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Reuses existing branch without error."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _init_git_repo(repo_path)
    (repo_path / "README.md").write_text("test")
    subprocess.run(["git", "add", "README.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"], check=True, capture_output=True
    )
    subprocess.run(["git", "branch", "test-feature"], check=True, capture_output=True)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])

    assert result.exit_code == 0
    container_path = tmp_path / "repo-wt"
    worktree_path = container_path / "test-feature"
    assert worktree_path.exists()


def test_new_directory_collision(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Detects existing directory collision."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _init_git_repo(repo_path)
    (repo_path / "README.md").write_text("test")
    subprocess.run(["git", "add", "README.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"], check=True, capture_output=True
    )

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
    """Creates worktree with new branch in sibling container."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _init_git_repo(repo_path)
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
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Creates multiple worktrees in sibling container."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _init_git_repo(repo_path)
    (repo_path / "README.md").write_text("test")
    subprocess.run(["git", "add", "README.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"], check=True, capture_output=True
    )

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-wt"])
    assert result.exit_code == 0

    container_path = tmp_path / "repo-wt"
    worktree_path = container_path / "test-wt"
    assert worktree_path.exists()
    assert "repo-wt/test-wt" in result.output

    branch_result = subprocess.run(
        ["git", "branch", "--list", "test-wt"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-wt" in branch_result.stdout

    result = runner.invoke(worktree, ["new", "another-wt"])
    assert result.exit_code == 0

    worktree_path2 = container_path / "another-wt"
    assert worktree_path2.exists()
    assert "repo-wt/another-wt" in result.output

    subprocess.run(
        ["git", "branch", "existing-branch"], check=True, capture_output=True
    )
    result = runner.invoke(worktree, ["new", "existing-branch"])
    assert result.exit_code == 0
    assert (container_path / "existing-branch").exists()
    assert "repo-wt/existing-branch" in result.output


def test_new_sandbox_registration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Registers container in main and worktree settings."""
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

    container_path = tmp_path / "repo-wt"
    worktree_path = container_path / "test-feature"

    main_settings = repo_path / ".claude" / "settings.local.json"
    assert main_settings.exists()

    with main_settings.open() as f:
        main_settings_data = json.load(f)

    dirs = main_settings_data.get("permissions", {}).get("additionalDirectories", [])
    assert str(container_path) in dirs

    wt_settings = worktree_path / ".claude" / "settings.local.json"
    assert wt_settings.exists()

    with wt_settings.open() as f:
        wt_settings_data = json.load(f)

    wt_dirs = wt_settings_data.get("permissions", {}).get("additionalDirectories", [])
    assert str(container_path) in wt_dirs

    result = runner.invoke(worktree, ["new", "test-feature-2"])
    assert result.exit_code == 0

    with main_settings.open() as f:
        main_settings_data_after = json.load(f)

    dirs_after = main_settings_data_after.get("permissions", {}).get(
        "additionalDirectories", []
    )
    count = dirs_after.count(str(container_path))
    assert count == 1


def test_new_environment_initialization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Runs just setup in worktree if available."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _init_git_repo(repo_path)

    (repo_path / "README.md").write_text("test")
    subprocess.run(["git", "add", "README.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"], check=True, capture_output=True
    )

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

    monkeypatch.setattr("claudeutils.worktree.cli.subprocess.run", mock_run)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-setup"])

    assert result.exit_code == 0

    container_path = tmp_path / "repo-wt"
    worktree_path = container_path / "test-setup"
    assert worktree_path.exists()

    just_version_calls = [c for c in calls if c[0] == ["just", "--version"]]
    assert len(just_version_calls) > 0
    just_setup_calls = [c for c in calls if c[0] == ["just", "setup"]]
    assert len(just_setup_calls) > 0
    assert any(c[1].get("cwd") == worktree_path for c in just_setup_calls)


def test_new_task_option(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Creates worktree with --task option."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _init_git_repo(repo_path)
    (repo_path / "README.md").write_text("test")
    subprocess.run(["git", "add", "README.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"], check=True, capture_output=True
    )

    agents_dir = repo_path / "agents"
    agents_dir.mkdir()
    session_file = agents_dir / "session.md"
    session_file.write_text(
        "# Session\n\n"
        "## Pending Tasks\n\n"
        "- [ ] **Implement feature** — `command` | sonnet\n"
        "  - Plan: plans/test-plan\n"
        "- [ ] **Another task** — `command` | sonnet\n"
        "  - Plan: plans/other-plan\n"
    )

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "--task", "Implement feature"])
    assert result.exit_code == 0
    container_path = tmp_path / "repo-wt"
    worktree_path = container_path / "implement-feature"
    assert worktree_path.exists()

    result = runner.invoke(worktree, ["new", "explicit-slug", "--task", "Another task"])
    assert result.exit_code != 0
    assert (
        "mutually exclusive" in result.output.lower() or "both" in result.output.lower()
    )

    result = runner.invoke(
        worktree, ["new", "--task", "Another task", "--session", "some-session.md"]
    )
    assert result.exit_code == 0
    assert "warning" in result.output.lower() or "ignored" in result.output.lower()

    result = runner.invoke(worktree, ["new", "--help"])
    assert "--task" in result.output
    assert "--session-md" in result.output


def test_new_session_handling_branch_reuse(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Warns and ignores --session when branch already exists."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _init_git_repo(repo_path)
    (repo_path / "README.md").write_text("test")
    subprocess.run(["git", "add", "README.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"], check=True, capture_output=True
    )

    # Create existing branch
    subprocess.run(["git", "branch", "test-feature"], check=True, capture_output=True)

    # Create session file to pass
    agents_dir = repo_path / "agents"
    agents_dir.mkdir()
    session_file = agents_dir / "session.md"
    session_file.write_text("# Session\n\n## Pending Tasks\n\n- [ ] **Test** — test\n")

    runner = CliRunner()
    # Call with --session when branch exists
    result = runner.invoke(
        worktree, ["new", "test-feature", "--session", str(session_file)]
    )

    # Should succeed with warning
    assert result.exit_code == 0
    assert "warning" in result.output.lower() or "exists" in result.output.lower()
    assert "session" in result.output.lower() or "ignored" in result.output.lower()

    # Worktree should be created
    container_path = tmp_path / "repo-wt"
    worktree_path = container_path / "test-feature"
    assert worktree_path.exists()

    # New branch without --session should work normally
    result = runner.invoke(worktree, ["new", "new-branch"])
    assert result.exit_code == 0
    worktree_path2 = container_path / "new-branch"
    assert worktree_path2.exists()
