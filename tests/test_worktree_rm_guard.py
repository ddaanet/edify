"""Tests for _is_branch_merged guard function."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from claudeutils.worktree.cli import _classify_branch
from claudeutils.worktree.utils import _is_branch_merged


def test_is_branch_merged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Verify branch merge detection with git merge-base.

    Tests that _is_branch_merged returns True for merged branches and False for
    unmerged branches using git merge-base --is-ancestor.
    """
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    # Create a branch that will be merged into main
    subprocess.run(
        ["git", "checkout", "-b", "merged-branch"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    (repo_path / "merged-file.txt").write_text("merged content")
    subprocess.run(
        ["git", "add", "merged-file.txt"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Commit on merged branch"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Switch back to main and merge the branch
    subprocess.run(
        ["git", "checkout", "-"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "merge", "merged-branch", "--no-edit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Test that merged branch returns True
    assert _is_branch_merged("merged-branch") is True

    # Create a branch that will NOT be merged
    subprocess.run(
        ["git", "checkout", "-b", "unmerged-branch"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    (repo_path / "unmerged-file.txt").write_text("unmerged content")
    subprocess.run(
        ["git", "add", "unmerged-file.txt"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Commit on unmerged branch"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Switch back to main to verify unmerged branch is not an ancestor
    subprocess.run(
        ["git", "checkout", "-"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Test that unmerged branch returns False
    assert _is_branch_merged("unmerged-branch") is False


def test_classify_branch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Verify branch classification by commit count and focused marker.

    Tests that _classify_branch returns (count, is_focused) where:
    - count is the number of commits between merge-base and branch tip
    - is_focused is True only if count==1 and message matches
      "Focused session for {slug}"
    """
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    init_repo(repo_path)
    monkeypatch.chdir(repo_path)

    # Case 1: Focused-session-only branch (1 commit with marker)
    subprocess.run(
        ["git", "checkout", "-b", "focused-session"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    # Create the exact marker text from _create_session_commit
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "Focused session for focused-session"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    # Switch back to main before calling _classify_branch
    subprocess.run(
        ["git", "checkout", "-"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    count, is_focused = _classify_branch("focused-session")
    assert count == 1, f"Expected count=1 but got {count}"
    assert is_focused is True, f"Expected is_focused=True but got {is_focused}"

    # Case 2: Real-history branch (1 user commit)
    # (we're already on main from the checkout - above)
    subprocess.run(
        ["git", "checkout", "-b", "real-history"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    (repo_path / "user-file.txt").write_text("user content")
    subprocess.run(
        ["git", "add", "user-file.txt"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "User commit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    # Switch back to main before calling _classify_branch
    subprocess.run(
        ["git", "checkout", "-"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    count, is_focused = _classify_branch("real-history")
    assert count == 1
    assert is_focused is False

    # Case 3: Multi-commit branch (3 commits)
    # (we're already on main from the checkout - above)
    subprocess.run(
        ["git", "checkout", "-b", "multi-commit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    for i in range(3):
        (repo_path / f"file-{i}.txt").write_text(f"content {i}")
        subprocess.run(
            ["git", "add", f"file-{i}.txt"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", f"Commit {i}"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
    # Switch back to main before calling _classify_branch
    subprocess.run(
        ["git", "checkout", "-"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    count, is_focused = _classify_branch("multi-commit")
    assert count == 3
    assert is_focused is False

    # Case 4: Marker with similar but wrong format (missing "for")
    # (we're already on main from the checkout - above)
    subprocess.run(
        ["git", "checkout", "-b", "wrong-format"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "Focused session wrong-format"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    # Switch back to main before calling _classify_branch
    subprocess.run(
        ["git", "checkout", "-"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    count, is_focused = _classify_branch("wrong-format")
    assert count == 1
    assert is_focused is False


def test_classify_orphan_branch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Verify orphan branch classification (no common ancestor).

    Tests that _classify_branch handles orphan branches (no merge-base)
    by returning (0, False) to treat as real history.
    """
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    init_repo(repo_path)
    monkeypatch.chdir(repo_path)

    # Create orphan branch (unrelated history)
    subprocess.run(
        ["git", "checkout", "--orphan", "orphan-test"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    # Commit on orphan branch
    (repo_path / "orphan-file.txt").write_text("orphan content")
    subprocess.run(
        ["git", "add", "orphan-file.txt"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Orphan commit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Switch back to main before calling _classify_branch
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Verify orphan branch returns (0, False)
    count, is_focused = _classify_branch("orphan-test")
    assert count == 0, f"Expected count=0 for orphan branch but got {count}"
    assert is_focused is False, f"Expected is_focused=False but got {is_focused}"


def test_rm_refuses_unmerged_real_history(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Verify rm refuses unmerged branches with real history.

    Tests that worktree rm refuses to remove branches with unmerged commits
    (not just focused-session markers) and orphan branches.
    """
    from click.testing import CliRunner

    from claudeutils.worktree.cli import worktree

    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    init_repo(repo_path)
    monkeypatch.chdir(repo_path)

    runner = CliRunner()

    # Scenario A: Real history branch with 2 unmerged commits
    subprocess.run(
        ["git", "checkout", "-b", "real-unmerged"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    (repo_path / "file1.txt").write_text("content 1")
    subprocess.run(
        ["git", "add", "file1.txt"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Commit 1"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    (repo_path / "file2.txt").write_text("content 2")
    subprocess.run(
        ["git", "add", "file2.txt"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Commit 2"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Switch back to main
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create worktree for real-unmerged
    worktree_path = repo_path / "wt" / "real-unmerged"
    worktree_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "worktree", "add", str(worktree_path), "real-unmerged"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Call worktree rm real-unmerged
    result = runner.invoke(worktree, ["rm", "real-unmerged"])

    # Verify exit code is 1 (refused)
    assert result.exit_code == 1, f"Expected exit code 1 but got {result.exit_code}"

    # Verify stderr message
    assert (
        "Branch real-unmerged has 2 unmerged commit(s). Merge first." in result.output
    ), f"Expected error message not found in: {result.output}"

    # Verify worktree directory still exists
    assert worktree_path.exists(), "Worktree directory was removed but should exist"

    # Verify branch still exists
    branch_check = subprocess.run(
        ["git", "rev-parse", "--verify", "real-unmerged"],
        cwd=repo_path,
        capture_output=True,
    )
    assert branch_check.returncode == 0, "Branch was removed but should exist"

    # Scenario B: Orphan branch
    subprocess.run(
        ["git", "checkout", "--orphan", "orphan-branch"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    (repo_path / "orphan-file.txt").write_text("orphan content")
    subprocess.run(
        ["git", "add", "orphan-file.txt"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Orphan commit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Switch back to main
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create worktree for orphan-branch
    worktree_path_orphan = repo_path / "wt" / "orphan-branch"
    subprocess.run(
        ["git", "worktree", "add", str(worktree_path_orphan), "orphan-branch"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Call worktree rm orphan-branch
    result = runner.invoke(worktree, ["rm", "orphan-branch"])

    # Verify exit code is 1 (refused)
    assert result.exit_code == 1, f"Expected exit code 1 but got {result.exit_code}"

    # Verify stderr message
    assert (
        "Branch orphan-branch is orphaned (no common ancestor). Merge first."
        in result.output
    ), f"Expected orphan error message not found in: {result.output}"

    # Verify branch still exists
    branch_check_orphan = subprocess.run(
        ["git", "rev-parse", "--verify", "orphan-branch"],
        cwd=repo_path,
        capture_output=True,
    )
    assert branch_check_orphan.returncode == 0, "Orphan branch was removed but should exist"


def test_rm_allows_merged_branch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Verify rm allows merged branch removal with safe delete.

    Tests that worktree rm allows removal of merged branches using git branch -d
    (safe delete) and outputs appropriate success message.
    """
    from click.testing import CliRunner

    from claudeutils.worktree.cli import worktree

    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    init_repo(repo_path)
    monkeypatch.chdir(repo_path)

    runner = CliRunner()

    # Create branch with commit
    subprocess.run(
        ["git", "checkout", "-b", "merged-branch"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    (repo_path / "merged-file.txt").write_text("merged content")
    subprocess.run(
        ["git", "add", "merged-file.txt"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Commit on merged branch"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Switch back to main and merge the branch
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "merge", "merged-branch", "--no-edit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create worktree for merged branch
    worktree_path = repo_path / "wt" / "merged-branch"
    worktree_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "worktree", "add", str(worktree_path), "merged-branch"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Call worktree rm merged-branch
    result = runner.invoke(worktree, ["rm", "merged-branch"])

    # Verify exit code is 0 (success)
    assert result.exit_code == 0, f"Expected exit code 0 but got {result.exit_code}"

    # Verify branch was deleted
    branch_check = subprocess.run(
        ["git", "rev-parse", "--verify", "merged-branch"],
        cwd=repo_path,
        capture_output=True,
    )
    assert branch_check.returncode != 0, "Branch should be deleted"

    # Verify output contains expected message (without "worktree" qualifier)
    assert (
        "Removed merged-branch" in result.output
    ), f"Expected 'Removed merged-branch' in output but got: {result.output}"


def test_rm_allows_focused_session_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Verify rm allows focused-session-only branch removal with force delete.

    Tests that worktree rm allows removal of unmerged branches that contain
    only the focused-session marker commit, using git branch -D (force delete)
    and outputs appropriate success message.
    """
    from click.testing import CliRunner

    from claudeutils.worktree.cli import worktree

    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    init_repo(repo_path)
    monkeypatch.chdir(repo_path)

    runner = CliRunner()

    # Create branch with exactly 1 commit: the focused-session marker
    subprocess.run(
        ["git", "checkout", "-b", "test-branch"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "Focused session for test-branch"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Switch back to main
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create worktree for test-branch
    worktree_path = repo_path / "wt" / "test-branch"
    worktree_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "worktree", "add", str(worktree_path), "test-branch"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Call worktree rm test-branch
    result = runner.invoke(worktree, ["rm", "test-branch"])

    # Verify exit code is 0 (success)
    assert result.exit_code == 0, f"Expected exit code 0 but got {result.exit_code}"

    # Verify branch was deleted (force delete required)
    branch_check = subprocess.run(
        ["git", "rev-parse", "--verify", "test-branch"],
        cwd=repo_path,
        capture_output=True,
    )
    assert branch_check.returncode != 0, "Branch should be deleted"

    # Verify output contains expected message
    assert (
        "Removed test-branch (focused session only)" in result.output
    ), f"Expected 'Removed test-branch (focused session only)' in output but got: {result.output}"


def test_rm_guard_prevents_destruction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Verify rm guard prevents ALL destructive operations for unmerged real history.

    Tests integration ordering: when guard refuses removal (exit 1), NONE of the
    following should execute:
    - session.md task removal
    - worktree directory deletion
    - _probe_registrations call
    - git branch deletion

    This is a regression test for the original incident where these operations
    happened despite guard refusal.
    """
    from click.testing import CliRunner

    from claudeutils.worktree.cli import worktree

    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    init_repo(repo_path)
    monkeypatch.chdir(repo_path)

    runner = CliRunner()

    # Create branch with 2 unmerged commits (real history, not focused)
    subprocess.run(
        ["git", "checkout", "-b", "guard-test"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    (repo_path / "file1.txt").write_text("content 1")
    subprocess.run(
        ["git", "add", "file1.txt"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Commit 1"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    (repo_path / "file2.txt").write_text("content 2")
    subprocess.run(
        ["git", "add", "file2.txt"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Commit 2"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Switch back to main
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create worktree directory
    worktree_path = repo_path / "wt" / "guard-test"
    worktree_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "worktree", "add", str(worktree_path), "guard-test"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Add task to session.md
    session_md_path = repo_path / "agents" / "session.md"
    session_md_path.parent.mkdir(parents=True, exist_ok=True)
    session_md_path.write_text(
        "# Session\n\n## Worktree Tasks\n\n"
        "- [ ] **Test Task** → `guard-test`\n"
    )

    # Call worktree rm guard-test
    result = runner.invoke(worktree, ["rm", "guard-test"])

    # Verify exit code is 1 (guard refused)
    assert result.exit_code == 1, f"Expected exit code 1 but got {result.exit_code}"

    # NEGATIVE ASSERTIONS (regression test for incident)

    # 1. Worktree directory still exists on disk
    assert worktree_path.exists(), (
        "Worktree directory was removed but should exist (guard should prevent deletion)"
    )

    # 2. Branch still exists
    branch_check = subprocess.run(
        ["git", "rev-parse", "--verify", "guard-test"],
        cwd=repo_path,
        capture_output=True,
    )
    assert branch_check.returncode == 0, (
        "Branch was removed but should exist (guard should prevent deletion)"
    )

    # 3. Session.md task NOT removed
    session_content = session_md_path.read_text()
    assert "→ `guard-test`" in session_content, (
        "Session.md task was removed but should exist (guard should prevent modification)"
    )

    # 4. _probe_registrations NOT called (verify via side effect absence)
    # If probe was called, worktree prune would have happened. Check that worktree
    # is still registered (proving prune didn't run).
    list_output = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert str(worktree_path) in list_output, (
        "Worktree not in git worktree list (prune may have run, indicating "
        "_probe_registrations was called despite guard refusal)"
    )
