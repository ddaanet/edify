"""Tests for verify-step.sh script."""

import subprocess
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).parent.parent
    / "plugin"
    / "skills"
    / "orchestrate"
    / "scripts"
    / "verify-step.sh"
)


def _setup_git_repo(repo_path: Path) -> None:
    """Initialize a git repo with an initial commit."""
    subprocess.run(
        ["git", "init"],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )


def _create_justfile(repo_path: Path) -> None:
    """Create a minimal justfile with precommit recipe."""
    justfile = repo_path / "justfile"
    justfile.write_text("precommit:\n\t@echo 'ok'\n")
    subprocess.run(
        ["git", "add", "justfile"],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "add justfile"],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )


def _make_dirty_state(repo_path: Path, scenario: str) -> None:
    """Create a dirty git state for the given scenario."""
    if scenario == "uncommitted":
        dirty_file = repo_path / "test.txt"
        dirty_file.write_text("uncommitted content")
        subprocess.run(
            ["git", "add", "test.txt"],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )
    elif scenario == "untracked":
        untracked_file = repo_path / "untracked.txt"
        untracked_file.write_text("untracked content")


def test_verify_step_clean_state(tmp_path: Path) -> None:
    """verify-step.sh exits with 0 and prints CLEAN on clean repo."""
    _setup_git_repo(tmp_path)
    _create_justfile(tmp_path)

    result = subprocess.run(
        [str(SCRIPT)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}. "
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "CLEAN" in result.stdout or "CLEAN" in result.stderr, (
        f"Expected 'CLEAN' in output. stdout: {result.stdout}\nstderr: {result.stderr}"
    )


@pytest.mark.parametrize(
    "scenario",
    ["uncommitted", "untracked"],
)
def test_verify_step_dirty_states(tmp_path: Path, scenario: str) -> None:
    """verify-step.sh detects dirty states and non-zero exit."""
    _setup_git_repo(tmp_path)
    _create_justfile(tmp_path)
    _make_dirty_state(tmp_path, scenario)

    result = subprocess.run(
        [str(SCRIPT)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0, (
        f"Expected non-zero exit for {scenario!r}, got {result.returncode}. "
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "DIRTY" in result.stdout or "DIRTY" in result.stderr, (
        f"Expected 'DIRTY' in output for {scenario!r}. "
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_verify_step_precommit_failure(tmp_path: Path) -> None:
    """verify-step.sh exits 1 with PRECOMMIT when precommit fails."""
    _setup_git_repo(tmp_path)
    # Create a justfile with a failing precommit recipe
    justfile = tmp_path / "justfile"
    justfile.write_text("precommit:\n\t@echo 'lint failed' && exit 1\n")
    subprocess.run(
        ["git", "add", "justfile"],
        cwd=tmp_path,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "add justfile"],
        cwd=tmp_path,
        capture_output=True,
        check=True,
    )

    result = subprocess.run(
        [str(SCRIPT)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0, (
        f"Expected non-zero exit for precommit failure, got {result.returncode}. "
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "PRECOMMIT" in result.stdout or "PRECOMMIT" in result.stderr, (
        f"Expected 'PRECOMMIT' in output. "
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
