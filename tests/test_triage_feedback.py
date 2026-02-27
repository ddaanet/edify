"""Tests for triage-feedback script."""

import subprocess
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent / "agent-core" / "bin" / "triage-feedback.sh"
)


def _init_repo(tmp_path: Path) -> tuple[Path, str]:
    """Initialize git repo with initial commit.

    Returns (repo_path, commit_sha).
    """
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()

    result = subprocess.run(
        ["git", "init"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git init failed: {result.stderr}"

    result = subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git config email failed: {result.stderr}"

    result = subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git config name failed: {result.stderr}"

    (repo_path / "dummy.txt").write_text("initial content")

    result = subprocess.run(
        ["git", "add", "dummy.txt"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git add failed: {result.stderr}"

    result = subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git commit failed: {result.stderr}"

    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git rev-parse failed: {result.stderr}"
    commit_sha = result.stdout.strip()

    return repo_path, commit_sha


def test_script_exists_and_executable() -> None:
    """Script exists and has executable permission."""
    assert SCRIPT.exists(), f"Script not found at {SCRIPT}"
    assert SCRIPT.stat().st_mode & 0o111, f"Script is not executable: {SCRIPT}"


def test_no_args_shows_usage() -> None:
    """Running without args shows usage to stderr and exits 0."""
    result = subprocess.run(
        [str(SCRIPT)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}: {result.stderr}"
    )
    assert "Usage" in result.stderr, f"Usage not in stderr: {result.stderr}"


def test_basic_invocation_produces_output(tmp_path: Path) -> None:
    """Invocation with args produces both Evidence and Verdict sections."""
    repo_path, baseline_sha = _init_repo(tmp_path)

    result = subprocess.run(
        [str(SCRIPT), "testjob", baseline_sha],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}: {result.stderr}"
    )
    assert "## Evidence" in result.stdout, f"Evidence section missing: {result.stdout}"
    assert "## Verdict" in result.stdout, f"Verdict section missing: {result.stdout}"


def test_files_changed_count(tmp_path: Path) -> None:
    """Script counts files changed since baseline commit."""
    repo_path, baseline_sha = _init_repo(tmp_path)

    (repo_path / "newfile.txt").write_text("new content")

    result = subprocess.run(
        ["git", "add", "newfile.txt"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git add failed: {result.stderr}"

    result = subprocess.run(
        ["git", "commit", "-m", "add new file"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git commit failed: {result.stderr}"

    result = subprocess.run(
        [str(SCRIPT), "testjob", baseline_sha],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}: {result.stderr}"
    )
    assert "Files changed: 1" in result.stdout, (
        f"Expected 'Files changed: 1', got: {result.stdout}"
    )
