"""Tests for commit CLI wiring (Cycle 6.6)."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from claudeutils.session.cli import commit_cmd


def _init_repo(path: Path) -> None:
    """Initialize a minimal git repo for CLI testing."""
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=path,
        check=True,
        capture_output=True,
    )
    (path / "README.md").write_text("init")
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=path,
        check=True,
        capture_output=True,
    )


# Cycle 6.6: CLI wiring


def test_commit_cli_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Valid commit markdown on stdin → exit 0, commit output."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)

    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "foo.py").write_text("code")

    stdin = "## Files\n- src/foo.py\n\n## Message\n> ✨ Add foo module\n"

    runner = CliRunner()
    with patch(
        "claudeutils.session.commit_pipeline._run_precommit",
        return_value=(True, "ok"),
    ):
        result = runner.invoke(commit_cmd, input=stdin)

    assert result.exit_code == 0
    assert "foo" in result.output.lower()


def test_commit_cli_validation_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Empty stdin → exit 2, missing section error."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)

    runner = CliRunner()
    result = runner.invoke(commit_cmd, input="")

    assert result.exit_code == 2
    assert "**Error:**" in result.output


def test_commit_cli_vet_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Files matching require-review, no report → exit 1."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)

    # Create pyproject.toml with require-review patterns
    (tmp_path / "pyproject.toml").write_text(
        '[tool.claudeutils.commit]\nrequire-review = ["src/**/*.py"]\n'
    )

    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "foo.py").write_text("code")

    stdin = "## Files\n- src/foo.py\n\n## Message\n> ✨ Add foo\n"

    runner = CliRunner()
    with patch(
        "claudeutils.session.commit_pipeline._run_precommit",
        return_value=(True, "ok"),
    ):
        result = runner.invoke(commit_cmd, input=stdin)

    assert result.exit_code == 1
    assert "unreviewed" in result.output.lower() or "Vet" in result.output
