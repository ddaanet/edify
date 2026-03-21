"""Tests for commit pipeline validation levels (Cycle 6.4)."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from claudeutils.session.commit import CommitInput
from claudeutils.session.commit_pipeline import commit_pipeline


def _init_repo(path: Path) -> None:
    """Initialize a minimal git repo for pipeline testing."""
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


# Cycle 6.4: validation levels


def test_commit_just_lint(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Just-lint runs lint instead of full precommit."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)
    (tmp_path / "f.py").write_text("x")

    ci = CommitInput(files=["f.py"], message="msg", options={"just-lint"})

    precommit = MagicMock(return_value=(True, "ok"))
    lint = MagicMock(return_value=(True, "ok"))
    with (
        patch(
            "claudeutils.session.commit_pipeline._run_precommit",
            precommit,
        ),
        patch(
            "claudeutils.session.commit_pipeline._run_lint",
            lint,
        ),
    ):
        result = commit_pipeline(ci, cwd=tmp_path)

    precommit.assert_not_called()
    lint.assert_called_once()
    assert result.success is True


def test_commit_no_vet(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Default pipeline calls vet_check."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)
    (tmp_path / "f.py").write_text("x")

    ci = CommitInput(files=["f.py"], message="msg")

    vet = MagicMock()
    vet.return_value.passed = True
    with (
        patch(
            "claudeutils.session.commit_pipeline._run_precommit",
            return_value=(True, "ok"),
        ),
        patch(
            "claudeutils.session.commit_pipeline.vet_check",
            vet,
        ),
    ):
        commit_pipeline(ci, cwd=tmp_path)

    vet.assert_called_once()


def test_commit_combined_options(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Just-lint + amend: lint only, amend semantics."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)

    f = tmp_path / "f.py"
    f.write_text("v1")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "v1"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    f.write_text("v2")

    ci = CommitInput(
        files=["f.py"],
        message="amended",
        options={"just-lint", "amend"},
    )

    precommit = MagicMock(return_value=(True, "ok"))
    lint = MagicMock(return_value=(True, "ok"))
    with (
        patch(
            "claudeutils.session.commit_pipeline._run_precommit",
            precommit,
        ),
        patch(
            "claudeutils.session.commit_pipeline._run_lint",
            lint,
        ),
    ):
        result = commit_pipeline(ci, cwd=tmp_path)

    precommit.assert_not_called()
    lint.assert_called_once()
    assert result.success is True

    log = subprocess.run(
        ["git", "log", "--oneline"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    commits = [ln for ln in log.stdout.strip().split("\n") if ln]
    assert len(commits) == 2
