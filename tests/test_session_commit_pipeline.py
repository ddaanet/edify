"""Tests for session commit pipeline (Phase 6, Cycle 6.1)."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from claudeutils.session.commit import CommitInput
from claudeutils.session.commit_pipeline import (
    CommitResult,
    _strip_hints,
    commit_pipeline,
)
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
    assert "foo" in result.output.lower()

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
    assert "Precommit" in result.output
    assert "failed" in result.output

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


def test_strip_hints_filters_continuation_lines() -> None:
    """Strip continuation lines following hint/advice."""
    input1 = "hint: use --force\n  (helpful continuation)\nother line"
    result1 = _strip_hints(input1)
    assert "other line" in result1
    assert "helpful continuation" not in result1
    assert "hint:" not in result1

    input2 = "advice: do this\n\tcontinuation here\nnormal line"
    result2 = _strip_hints(input2)
    assert "normal line" in result2
    assert "continuation here" not in result2
    assert "advice:" not in result2

    input3 = "regular line\nhint: tip\n  more tip"
    result3 = _strip_hints(input3)
    assert "regular line" in result3
    assert "more tip" not in result3


def test_strip_hints_multi_continuation() -> None:
    """Multi-line continuations after hint all filtered."""
    text = "hint: use --force\n  line1\n  line2\n  line3\nnormal"
    result = _strip_hints(text)
    assert "normal" in result
    assert "line1" not in result
    assert "line2" not in result
    assert "line3" not in result
    assert "hint:" not in result


def test_strip_hints_single_space_not_continuation() -> None:
    """Single-space indent is not a continuation line."""
    text = "hint: tip\n not a continuation\nnormal"
    result = _strip_hints(text)
    assert "not a continuation" in result
    assert "normal" in result
    assert "hint:" not in result
