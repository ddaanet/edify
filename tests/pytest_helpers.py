"""Pytest helper functions for test setup and assertions."""

import json
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

# Test Constants
SESSION_ID_MAIN = "e12d203f-ca65-44f0-9976-cb10b74514c1"
SESSION_ID_ALT = "a1b2c3d4-1234-5678-9abc-def012345678"
TS_BASE = "2025-12-16T08:00:00.000Z"
TS_EARLY = "2025-12-16T10:00:00.000Z"
TS_MID = "2025-12-16T11:00:00.000Z"
TS_LATE = "2025-12-16T12:00:00.000Z"


def make_mock_history_dir(history_dir: Path) -> Callable[[str], Path]:
    """Create mock function that returns fixed history directory."""

    def mock_get_history(proj: str) -> Path:
        return history_dir

    return mock_get_history


def setup_cli_mocks(
    monkeypatch: pytest.MonkeyPatch,
    argv: list[str],
    cwd: str | None = None,
    history_dir: Path | None = None,
) -> None:
    """Set up common CLI test mocks.

    Args:
        monkeypatch: pytest monkeypatch fixture
        argv: sys.argv to set
        cwd: Current working directory to mock (optional)
        history_dir: History directory to mock (optional)
    """
    monkeypatch.setattr("sys.argv", argv)
    if cwd:
        monkeypatch.setattr("os.getcwd", lambda: cwd)
    if history_dir:
        monkeypatch.setattr(
            "claudeutils.cli.get_project_history_dir",
            make_mock_history_dir(history_dir),
        )


def init_repo_at(path: Path) -> None:
    """Initialize a git repo at path with an initial commit.

    Uses -C style so path need not be cwd. Suitable for multi-repo test setups.
    """
    subprocess.run(["git", "init", str(path)], capture_output=True, check=True)
    subprocess.run(
        ["git", "-C", str(path), "config", "user.email", "test@test.com"],
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(path), "config", "user.name", "Test"],
        capture_output=True,
        check=True,
    )
    (path / "README.md").write_text("init")
    subprocess.run(
        ["git", "-C", str(path), "add", "."], capture_output=True, check=True
    )
    subprocess.run(
        ["git", "-C", str(path), "commit", "-m", "init"],
        capture_output=True,
        check=True,
    )


def init_repo_minimal(path: Path) -> None:
    """Init a git repo with user config (cwd style)."""
    for args in [
        ["git", "init"],
        ["git", "config", "user.email", "test@test.com"],
        ["git", "config", "user.name", "Test"],
    ]:
        result = subprocess.run(
            args, cwd=path, check=False, capture_output=True, text=True
        )
        assert result.returncode == 0, f"git {' '.join(args)} failed: {result.stderr}"


def setup_git_repo(tmp_path: Path) -> None:
    """Initialize a git repo in tmp_path for git add in validate_and_create."""
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=False)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=tmp_path,
        capture_output=True,
        check=False,
    )


def setup_baseline_agents(tmp_path: Path) -> None:
    """Create minimal baseline agent files that prepare-runbook.py reads."""
    agents_dir = tmp_path / "agent-core" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    artisan = agents_dir / "artisan.md"
    artisan.write_text("---\nname: artisan\n---\n# Artisan\nBaseline agent.")

    test_driver = agents_dir / "test-driver.md"
    test_driver.write_text(
        "---\nname: test-driver\n---\n"
        "# TDD Task Agent - Baseline Template\nBaseline TDD agent."
    )

    corrector = agents_dir / "corrector.md"
    corrector.write_text(
        "---\nname: corrector\nmodel: sonnet\n---\n# Corrector\nBaseline corrector."
    )


def assert_json_output(
    capsys: pytest.CaptureFixture[str], expected_length: int | None = None
) -> list[dict[str, object]]:
    """Capture stdout and validate JSON list output.

    Args:
        capsys: pytest capture fixture
        expected_length: Optional expected list length to assert

    Returns:
        Parsed JSON output list
    """
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert isinstance(output, list)
    if expected_length is not None:
        assert len(output) == expected_length
    return output
