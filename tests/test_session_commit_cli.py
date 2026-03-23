"""Tests for commit CLI wiring (Cycle 6.6)."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from claudeutils.session.cli import commit_cmd
from tests.pytest_helpers import init_repo_at as _init_repo

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
    assert "unreviewed" in result.output.lower()
    assert "Vet" in result.output


# Cycle 1.3: CleanFileError exit code 2


def test_commit_cli_clean_file_exits_2(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """CleanFileError (no uncommitted changes) exits 2."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)

    # Create and commit a file — no uncommitted changes remain
    (tmp_path / "src").mkdir()
    f = tmp_path / "src" / "foo.py"
    f.write_text("committed\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "add foo"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    # File listed but already committed — CleanFileError
    stdin = "## Files\n- src/foo.py\n\n## Message\n> update\n"
    runner = CliRunner()
    result = runner.invoke(commit_cmd, input=stdin)

    assert result.exit_code == 2
    assert "no uncommitted changes" in result.output.lower()
