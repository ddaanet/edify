"""Tests for worktree new subcommand."""

import json
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree


def _setup_repo_with_submodule(
    repo_path: Path, init_repo: Callable[[Path], None]
) -> None:
    init_repo(repo_path)
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
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Reuses existing branch without error."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)
    subprocess.run(["git", "branch", "test-feature"], check=True, capture_output=True)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])

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


def test_new_basic_flow(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Creates worktree with new branch in sibling container."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])
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
    result = runner.invoke(worktree, ["new", "test-wt"])
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

    result = runner.invoke(worktree, ["new", "another-wt"])
    assert result.exit_code == 0
    assert (container_path / "another-wt").exists()
    assert "repo-wt/another-wt" in result.output

    subprocess.run(
        ["git", "branch", "existing-branch"], check=True, capture_output=True
    )
    result = runner.invoke(worktree, ["new", "existing-branch"])
    assert result.exit_code == 0
    assert (container_path / "existing-branch").exists()
    assert "repo-wt/existing-branch" in result.output


def test_new_sandbox_registration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Registers container in main and worktree settings."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0

    container_path = tmp_path / "repo-wt"
    main_settings = repo_path / ".claude" / "settings.local.json"
    assert main_settings.exists()
    with main_settings.open() as f:
        dirs = json.load(f).get("permissions", {}).get("additionalDirectories", [])
    assert str(container_path) in dirs

    wt_settings = container_path / "test-feature" / ".claude" / "settings.local.json"
    assert wt_settings.exists()
    with wt_settings.open() as f:
        wt_dirs = json.load(f).get("permissions", {}).get("additionalDirectories", [])
    assert str(container_path) in wt_dirs

    runner.invoke(worktree, ["new", "test-feature-2"])
    with main_settings.open() as f:
        dirs_after = (
            json.load(f).get("permissions", {}).get("additionalDirectories", [])
        )
    assert dirs_after.count(str(container_path)) == 1


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

    monkeypatch.setattr("claudeutils.worktree.cli.subprocess.run", mock_run)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-setup"])
    assert result.exit_code == 0

    worktree_path = tmp_path / "repo-wt" / "test-setup"
    assert worktree_path.exists()

    assert any(c[0] == ["just", "--version"] for c in calls)
    assert any(
        c[0] == ["just", "setup"] and c[1].get("cwd") == worktree_path for c in calls
    )


def test_new_task_option(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Creates worktree with --task option."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    (repo_path / "agents").mkdir()
    (repo_path / "agents" / "session.md").write_text(
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
    assert (tmp_path / "repo-wt" / "implement-feature").exists()

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
        worktree, ["new", "test-feature", "--session", str(session_file)]
    )

    assert result.exit_code == 0
    assert "warning" in result.output.lower() or "exists" in result.output.lower()
    assert "session" in result.output.lower() or "ignored" in result.output.lower()

    container_path = tmp_path / "repo-wt"
    assert (container_path / "test-feature").exists()

    result = runner.invoke(worktree, ["new", "new-branch"])
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

    monkeypatch.setattr("claudeutils.worktree.cli.subprocess.run", mock_run)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-failure"])
    assert result.exit_code == 0

    worktree_path = tmp_path / "repo-wt" / "test-failure"
    assert worktree_path.exists()
    assert "warning" in result.output.lower() or "failed" in result.output.lower()


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
    result = runner.invoke(worktree, ["new", "test-idempotent"])
    assert result.exit_code == 0

    assert (container_path / "test-idempotent").exists()
    result = runner.invoke(worktree, ["new", "test-idempotent-2"])
    assert result.exit_code == 0
    assert (container_path / "test-idempotent-2").exists()
