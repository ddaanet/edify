"""Tests for merge-then-rm sequence: lifecycle.md must not block session amend."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from edify.worktree.cli import worktree
from edify.worktree.merge import merge
from tests.fixtures_worktree import _git_setup, make_repo_with_branch


def test_rm_amends_after_merge_with_lifecycle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    mock_precommit: None,
) -> None:
    """Rm amends merge commit when lifecycle.md was written during merge.

    Reproduces the bug: _append_lifecycle_delivered ran after the merge commit,
    leaving lifecycle.md unstaged. rm's dirty check then bailed on session amend.
    """
    repo = tmp_path / "repo"
    make_repo_with_branch(repo, init_repo, branch="test-feature")
    monkeypatch.chdir(repo)

    # Set up session.md with worktree task entry for rm to remove
    session_dir = repo / "agents"
    session_dir.mkdir(exist_ok=True)
    session_file = session_dir / "session.md"
    session_file.write_text(
        "# Session\n\n## Pending Tasks\n\n"
        "## Worktree Tasks\n\n"
        "- [ ] **Test task** → `test-feature` — description\n"
    )
    _git_setup("add", "agents/session.md")
    _git_setup("commit", "-m", "Add session with worktree task")

    # Set up a plan with "reviewed" lifecycle status (triggers delivered append)
    plans_dir = repo / "plans" / "my-plan"
    plans_dir.mkdir(parents=True)
    lifecycle = plans_dir / "lifecycle.md"
    lifecycle.write_text("2026-02-20 reviewed — /deliverable-review\n")
    _git_setup("add", "plans/")
    _git_setup("commit", "-m", "Add reviewed plan")

    # Run merge
    merge("test-feature")

    # After merge: lifecycle.md should be committed (not dirty)
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert "lifecycle.md" not in status, (
        f"lifecycle.md should be in merge commit, not dirty. Status: {status}"
    )

    # Run rm — should amend merge commit with session.md change
    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "test-feature"])
    assert result.exit_code == 0, f"rm failed: {result.output}"

    # Session amend should succeed — no dirty-state warning
    assert "parent repo dirty" not in result.output
    assert "Merge commit amended" in result.output

    # Both lifecycle.md and session.md must be in the final commit
    changed_files = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1..HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "plans/my-plan/lifecycle.md" in changed_files
    assert "agents/session.md" in changed_files


def test_lifecycle_delivered_in_merge_commit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    mock_precommit: None,
) -> None:
    """Lifecycle 'delivered' entry must be part of the merge commit tree."""
    repo = tmp_path / "repo"
    make_repo_with_branch(repo, init_repo, branch="test-feature")
    monkeypatch.chdir(repo)

    # Set up a plan with "reviewed" lifecycle status
    plans_dir = repo / "plans" / "my-plan"
    plans_dir.mkdir(parents=True)
    lifecycle = plans_dir / "lifecycle.md"
    lifecycle.write_text("2026-02-20 reviewed — /deliverable-review\n")
    _git_setup("add", "plans/")
    _git_setup("commit", "-m", "Add reviewed plan")

    merge("test-feature")

    # Verify lifecycle.md "delivered" entry is in the merge commit
    committed_content = subprocess.run(
        ["git", "show", "HEAD:plans/my-plan/lifecycle.md"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "delivered" in committed_content
    assert "_worktree merge" in committed_content

    # Tree should be clean after merge
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert status == "", f"Tree dirty after merge: {status}"
