"""Tests for session commit pipeline (Phase 6, Cycle 6.1)."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from claudeutils.session.commit import CommitInput
from claudeutils.session.commit_pipeline import CommitResult, commit_pipeline
from tests.pytest_helpers import init_repo_at as _init_repo

# Cycle 6.1: parent-only commit pipeline


def test_commit_parent_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Stages files, runs precommit, commits with message."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)

    f = tmp_path / "src" / "foo.py"
    f.parent.mkdir(parents=True)
    f.write_text("new content")

    ci = CommitInput(
        files=["src/foo.py"],
        message="✨ Add foo module",
    )

    with patch(
        "claudeutils.session.commit_pipeline._run_precommit",
        return_value=(True, "All checks passed"),
    ):
        result = commit_pipeline(ci, cwd=tmp_path)

    assert isinstance(result, CommitResult)
    assert result.success is True
    assert "foo" in result.output.lower() or "1 file" in result.output

    log = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert "Add foo module" in log.stdout


def test_commit_precommit_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Precommit failure returns error, files staged but not committed."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)

    f = tmp_path / "src" / "bar.py"
    f.parent.mkdir(parents=True)
    f.write_text("bad content")

    ci = CommitInput(
        files=["src/bar.py"],
        message="Add bar",
    )

    with patch(
        "claudeutils.session.commit_pipeline._run_precommit",
        return_value=(False, "lint failed: E501"),
    ):
        result = commit_pipeline(ci, cwd=tmp_path)

    assert result.success is False
    assert "Precommit" in result.output or "failed" in result.output

    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert "src/bar.py" in status.stdout

    log = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert "Add bar" not in log.stdout
