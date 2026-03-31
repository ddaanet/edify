"""Tests for commit pipeline error propagation (rework cycles 1.1-1.2)."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from claudeutils.session.commit import CommitInput
from claudeutils.session.commit_pipeline import (
    CommitResult,
    _error,
    _git_commit,
    commit_pipeline,
)
from tests.pytest_helpers import init_repo_at as _init_repo


def test_git_commit_raises_on_failure(tmp_path: Path) -> None:
    """_git_commit raises CalledProcessError on non-zero exit."""
    _init_repo(tmp_path)
    # Nothing staged — git commit will exit 1
    with pytest.raises(subprocess.CalledProcessError, match="non-zero exit status"):
        _git_commit("nothing to commit", cwd=tmp_path)


def test_pipeline_returns_failure_on_git_commit_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Pipeline returns success=False when git commit fails."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)

    # Create and stage a real file
    (tmp_path / "a.py").write_text("content\n")
    subprocess.run(
        ["git", "add", "a.py"], cwd=tmp_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "initial a.py"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    # Modify so validate_files passes, stage so git add works
    (tmp_path / "a.py").write_text("modified\n")

    ci = CommitInput(files=["a.py"], message="update")
    # Mock only precommit (needs justfile) and _git_commit (need it to fail)
    with (
        patch(
            "claudeutils.session.commit_pipeline._run_precommit",
            return_value=(True, "ok"),
        ),
        patch(
            "claudeutils.session.commit_pipeline._git_commit",
            side_effect=subprocess.CalledProcessError(1, ["git", "commit"]),
        ),
    ):
        result = commit_pipeline(ci, cwd=tmp_path)

    assert result.success is False


def test_pipeline_returns_failure_on_stage_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Pipeline returns success=False when staging raises."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)

    (tmp_path / "a.py").write_text("content\n")
    subprocess.run(
        ["git", "add", "a.py"], cwd=tmp_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "initial a.py"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    (tmp_path / "a.py").write_text("modified\n")

    ci = CommitInput(files=["a.py"], message="update")
    with (
        patch(
            "claudeutils.session.commit_pipeline._run_precommit",
            return_value=(True, "ok"),
        ),
        patch(
            "claudeutils.session.commit_pipeline._stage_files",
            side_effect=subprocess.CalledProcessError(
                128, ["git", "add"], stderr="fatal: staging failed"
            ),
        ),
    ):
        result = commit_pipeline(ci, cwd=tmp_path)

    assert result.success is False
    assert "**Error:**" in result.output


# Cycle 1.2: Structured error messages without Python repr


def test_error_structured_with_empty_stderr() -> None:
    """_error() produces structured output with empty stderr."""
    exc = subprocess.CalledProcessError(1, ["git", "commit"])
    exc.stderr = ""  # Empty stderr — the problematic path

    result = _error("staging failed", exc)

    assert result.success is False
    assert "**Error:** staging failed" in result.output
    assert "Command '[" not in result.output  # No raw repr


def test_error_structured_with_populated_stderr() -> None:
    """_error() includes stderr content when present."""
    exc = subprocess.CalledProcessError(128, ["git", "add"])
    exc.stderr = "fatal: not a git repository"

    result = _error("staging failed", exc)

    assert result.success is False
    assert "**Error:** staging failed" in result.output
    assert "fatal: not a git repository" in result.output


# Cycle 1.2: validation before submodule commit


def test_pipeline_validates_before_submodule_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Validation gate runs before submodule commits."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)

    # Set up submodule-like structure for partitioning
    sub = tmp_path / "plugin"
    sub.mkdir()
    _init_repo(sub)
    (sub / "f.md").write_text("new")

    ci = CommitInput(
        files=["plugin/f.md"],
        message="msg",
        submodules={"plugin": "sub msg"},
    )

    commit_sub = MagicMock(return_value="ok")
    validate_fail = CommitResult(success=False, output="Precommit: failed")

    with (
        patch(
            "claudeutils.session.commit_pipeline.discover_submodules",
            return_value=["plugin"],
        ),
        patch("claudeutils.session.commit_pipeline.validate_files"),
        patch(
            "claudeutils.session.commit_pipeline._commit_submodule",
            commit_sub,
        ),
        patch(
            "claudeutils.session.commit_pipeline._validate",
            return_value=validate_fail,
        ),
    ):
        result = commit_pipeline(ci, cwd=tmp_path)

    assert result.success is False
    # The bug: submodule committed before validation
    commit_sub.assert_not_called()


# Cycle 1.1: Submodule commit failure propagates error


def test_submodule_commit_failure_propagates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Submodule commit failure (check=False case) detected and propagated."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)

    sub = tmp_path / "plugin"
    sub.mkdir()
    _init_repo(sub)
    (sub / "f.md").write_text("v1\n")
    subprocess.run(["git", "add", "."], cwd=sub, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=sub,
        check=True,
        capture_output=True,
    )

    (sub / "f.md").write_text("v2\n")

    ci = CommitInput(
        files=["plugin/f.md"],
        message="update",
        submodules={"plugin": "submodule commit"},
    )

    # Mock subprocess.run to simulate git commit failure with check=True
    original_run = subprocess.run

    def mock_run(cmd: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        if (
            isinstance(cmd, list)
            and len(cmd) >= 2
            and cmd[0] == "git"
            and cmd[1] == "commit"
            and kwargs.get("cwd") == sub
        ):
            # Raise CalledProcessError to simulate commit failure
            exc = subprocess.CalledProcessError(1, cmd)
            exc.stderr = "nothing to commit"
            raise exc
        return original_run(cmd, **kwargs)

    with (
        patch(
            "claudeutils.session.commit_pipeline.discover_submodules",
            return_value=["plugin"],
        ),
        patch(
            "claudeutils.session.commit_pipeline._run_precommit",
            return_value=(True, "ok"),
        ),
        patch("subprocess.run", side_effect=mock_run),
    ):
        result = commit_pipeline(ci, cwd=tmp_path)

    assert result.success is False, (
        "Expected pipeline to fail when submodule commit fails, "
        f"got success={result.success}"
    )
    assert "**Error:**" in result.output


# C#5: amend+no-edit pipeline test


def test_commit_amend_no_edit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Amend+no-edit preserves existing commit message."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)

    f = tmp_path / "tracked.py"
    f.write_text("v1")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Original message"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    f.write_text("v2")

    ci = CommitInput(files=["tracked.py"], message=None, options={"amend", "no-edit"})

    with patch(
        "claudeutils.session.commit_pipeline._run_precommit",
        return_value=(True, "ok"),
    ):
        result = commit_pipeline(ci, cwd=tmp_path)

    assert result.success is True
    log = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert "Original message" in log.stdout
