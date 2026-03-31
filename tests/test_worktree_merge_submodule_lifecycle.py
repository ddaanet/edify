"""Tests for submodule MERGE_HEAD lifecycle during worktree merge."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from edify.worktree.cli import worktree
from tests.test_worktree_merge_submodule import _setup_submodule_conflict


def test_submodule_merge_head_not_orphaned_after_parent_merge(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
    commit_file: Callable[[Path, str, str, str], None],
) -> None:
    """Submodule MERGE_HEAD must not be orphaned after successful parent merge.

    Bug: Phase 2 submodule merge fails (conflict), leaves MERGE_HEAD in plugin.
    Phase 3+4 succeed on parent, exit 0. MERGE_HEAD persists undetected.
    Fix: after Phase 4 commit, check plugin for MERGE_HEAD. If present, exit 3.
    """
    monkeypatch.chdir(repo_with_submodule)

    agent_core_path, _wt_agent_core, _wt_commit = _setup_submodule_conflict(
        repo_with_submodule, "sub-merge-head-test", commit_file
    )

    runner = CliRunner()
    result = runner.invoke(worktree, ["merge", "sub-merge-head-test"])

    assert "Traceback" not in result.output, f"Unexpected traceback: {result.output}"
    # BUG: exits 0 with orphaned MERGE_HEAD in plugin
    # Fix: detect MERGE_HEAD after Phase 4, report and exit 3
    assert result.exit_code == 3, (
        f"Expected exit 3 (submodule MERGE_HEAD detected),"
        f" got {result.exit_code}. Output: {result.output}"
    )
    merge_head_check = subprocess.run(
        ["git", "-C", str(agent_core_path), "rev-parse", "--verify", "MERGE_HEAD"],
        capture_output=True,
        check=False,
    )
    assert merge_head_check.returncode == 0, (
        "plugin MERGE_HEAD should still exist (user must resolve and re-run)"
    )
