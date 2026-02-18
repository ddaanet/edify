"""Tests for worktree merge submodule operations."""

import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import cast
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree


def _setup_diverged_submodule(
    repo_with_submodule: Path,
    branch_name: str,
    commit_file: Callable[[Path, str, str, str], None],
) -> tuple[Path, str]:
    """Set up diverged submodule state for fetch testing.

    Returns:
        Tuple of (agent_core_path, wt_submodule_commit)
    """
    commit_file(repo_with_submodule, ".gitignore", "wt/\n", "Add gitignore")

    agent_core_path = repo_with_submodule / "agent-core"
    commit_file(
        agent_core_path,
        "fetch_change.txt",
        "fetch test change",
        "Fetch test change",
    )

    base_commit = subprocess.run(
        ["git", "-C", str(agent_core_path), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    _update_submodule_pointer(repo_with_submodule, "Update agent-core pointer")

    subprocess.run(
        ["git", "branch", branch_name],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    result = CliRunner().invoke(worktree, ["new", branch_name])
    assert result.exit_code == 0

    subprocess.run(
        ["git", "-C", str(agent_core_path), "reset", "--hard", base_commit],
        check=True,
        capture_output=True,
    )

    commit_file(
        agent_core_path,
        "diverged_change.txt",
        "diverged change",
        "Diverged change",
    )

    result = subprocess.run(
        ["git", "ls-tree", branch_name, "--", "agent-core"],
        cwd=repo_with_submodule,
        capture_output=True,
        text=True,
        check=True,
    )
    if not result.stdout.strip():
        pytest.skip("Branch has no agent-core submodule entry (test incomplete)")
    wt_submodule_commit = result.stdout.split()[2]

    return agent_core_path, wt_submodule_commit


def test_merge_submodule_fetch(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
    commit_file: Callable[[Path, str, str, str], None],
) -> None:
    """Verify merge checks object reachability and fetches when needed."""
    monkeypatch.chdir(repo_with_submodule)

    agent_core_path, wt_submodule_commit = _setup_diverged_submodule(
        repo_with_submodule, "fetch-test", commit_file
    )

    orig_subprocess_run = subprocess.run
    cat_file_calls = []
    fetch_calls = []
    merge_base_calls = []

    def fake_run(
        *args: object,
        **kwargs: object,
    ) -> MagicMock | object:
        if args and isinstance(args[0], list):
            cmd = args[0]
            if "merge-base" in cmd and "-C" in cmd and "agent-core" in cmd:
                # Only intercept submodule merge-base, not parent validation
                merge_base_calls.append(cmd)
                result_obj = MagicMock()
                result_obj.returncode = 1
                return result_obj
            if "cat-file" in cmd and "-e" in cmd:
                cat_file_calls.append(cmd)
                if wt_submodule_commit in cmd:
                    result_obj = MagicMock()
                    result_obj.returncode = 1
                    return result_obj
            elif "fetch" in cmd:
                fetch_calls.append(cmd)
        result = orig_subprocess_run(*args, **kwargs)  # type: ignore[call-overload]
        return cast("object", result)

    local_commit = subprocess.run(
        ["git", "-C", str(agent_core_path), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    assert wt_submodule_commit != local_commit, (
        f"Test setup issue: wt commit ({wt_submodule_commit}) "
        f"should differ from local ({local_commit})"
    )

    with patch("claudeutils.worktree.merge.subprocess.run", side_effect=fake_run):
        result = CliRunner().invoke(worktree, ["merge", "fetch-test"])
        assert result.exit_code == 0, f"merge failed: {result.output}"

        assert len(merge_base_calls) > 0, (
            f"merge should check ancestor, calls: {merge_base_calls}"
        )

        cat_file_has_wt = any(wt_submodule_commit in str(c) for c in cat_file_calls)
        assert cat_file_has_wt, (
            f"merge should check reachability with cat-file -e, "
            f"merge_base: {merge_base_calls}, cat_file: {cat_file_calls}"
        )

        assert len(fetch_calls) > 0, (
            f"merge should fetch when unreachable, fetch_calls: {fetch_calls}"
        )


def _update_submodule_pointer(repo: Path, message: str) -> None:
    """Stage and commit submodule pointer update."""
    subprocess.run(
        ["git", "add", "agent-core"], cwd=repo, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", message], cwd=repo, check=True, capture_output=True
    )


def _setup_merge_test_worktree(
    repo_with_submodule: Path,
    branch_name: str,
    commit_file: Callable[[Path, str, str, str], None],
) -> tuple[Path, str, str]:
    """Set up worktree with diverged submodule for merge commit testing.

    Returns:
        Tuple of (agent_core_path, main_commit, wt_commit)
    """
    commit_file(repo_with_submodule, ".gitignore", "wt/\n", "Add gitignore")

    agent_core_path = repo_with_submodule / "agent-core"
    commit_file(agent_core_path, "base_change.txt", "base change", "Base change")
    _update_submodule_pointer(repo_with_submodule, "Update agent-core to base")

    subprocess.run(
        ["git", "branch", branch_name],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    result = CliRunner().invoke(worktree, ["new", branch_name])
    assert result.exit_code == 0

    commit_file(
        agent_core_path,
        "main_change.txt",
        "main change",
        "Main branch change",
    )
    main_commit = subprocess.run(
        ["git", "-C", str(agent_core_path), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    _update_submodule_pointer(repo_with_submodule, "Update to main commit")

    wt_agent_core = (
        repo_with_submodule.parent
        / f"{repo_with_submodule.name}-wt"
        / branch_name
        / "agent-core"
    )
    commit_file(wt_agent_core, "wt_change.txt", "wt change", "Worktree change")
    wt_commit = subprocess.run(
        ["git", "-C", str(wt_agent_core), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    wt_branch = (
        repo_with_submodule.parent / f"{repo_with_submodule.name}-wt" / branch_name
    )
    _update_submodule_pointer(wt_branch, "Update wt pointer")

    return agent_core_path, main_commit, wt_commit


def test_merge_submodule_merge_commit(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
    commit_file: Callable[[Path, str, str, str], None],
) -> None:
    """Verify merge performs submodule merge and commits changes.

    Merge commit logic:
    - If no merge needed: skip entirely
    - If merge needed: run git -C agent-core merge --no-edit <wt-commit>
    - Stage submodule: git add agent-core
    - Check if staged: git diff --cached --quiet agent-core (exit != 0 means changes)
    - If staged changes: commit with "🔀 Merge agent-core from <slug>"
    - If no staged changes: skip commit
    """
    monkeypatch.chdir(repo_with_submodule)

    agent_core_path, main_commit, wt_commit = _setup_merge_test_worktree(
        repo_with_submodule, "merge-test", commit_file
    )

    result = CliRunner().invoke(worktree, ["merge", "merge-test"])
    assert result.exit_code == 0

    merged_commit = subprocess.run(
        ["git", "-C", str(agent_core_path), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    assert merged_commit != main_commit, "submodule should be merged to wt_commit"
    assert (
        subprocess.run(
            [
                "git",
                "-C",
                str(agent_core_path),
                "merge-base",
                "--is-ancestor",
                wt_commit,
                merged_commit,
            ],
            check=False,
        ).returncode
        == 0
    ), "merged_commit should have wt_commit as ancestor"

    # Should have two commits: Phase 2 submodule merge, Phase 4 parent merge
    recent_commits = (
        subprocess.run(
            ["git", "log", "-2", "--format=%s"],
            cwd=repo_with_submodule,
            capture_output=True,
            text=True,
            check=True,
        )
        .stdout.strip()
        .split("\n")
    )

    assert len(recent_commits) == 2, (
        f"Expected 2 commits (submodule + parent), got {len(recent_commits)}"
    )
    assert recent_commits[0] == "🔀 Merge merge-test", (
        f"Latest commit should be parent merge, got: {recent_commits[0]}"
    )
    assert recent_commits[1] == "🔀 Merge agent-core from merge-test", (
        f"Previous commit should be submodule merge, got: {recent_commits[1]}"
    )


def test_submodule_conflict_does_not_abort_pipeline(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
    commit_file: Callable[[Path, str, str, str], None],
) -> None:
    """Verify merge handles submodule conflicts without aborting pipeline.

    When submodule merge produces conflicts:
    - merge(slug) does NOT exit with CalledProcessError traceback
    - Agent-core MERGE_HEAD exists after call (submodule conflict preserved)
    - Exit code is 0 or 3
    - Output does not contain "Traceback"
    """
    monkeypatch.chdir(repo_with_submodule)

    agent_core_path = repo_with_submodule / "agent-core"

    # Create a base commit on main in a file in agent-core
    commit_file(agent_core_path, "conflict.txt", "base content", "Base change")
    base_commit = subprocess.run(
        ["git", "-C", str(agent_core_path), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    _update_submodule_pointer(repo_with_submodule, "Update to base commit")

    # Create branch and worktree
    subprocess.run(
        ["git", "branch", "conflict-test"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    result = CliRunner().invoke(worktree, ["new", "conflict-test"])
    assert result.exit_code == 0

    # In worktree's agent-core, create conflicting change to same file
    wt_agent_core = (
        repo_with_submodule.parent
        / f"{repo_with_submodule.name}-wt"
        / "conflict-test"
        / "agent-core"
    )
    commit_file(wt_agent_core, "conflict.txt", "wt change", "Worktree conflict change")
    wt_commit = subprocess.run(
        ["git", "-C", str(wt_agent_core), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    # Update worktree's submodule pointer
    wt_branch = repo_with_submodule.parent / f"{repo_with_submodule.name}-wt" / "conflict-test"
    _update_submodule_pointer(wt_branch, "Update wt pointer to conflict commit")

    # Back on main, create a different change to the same file (real conflict)
    commit_file(agent_core_path, "conflict.txt", "main change", "Main conflict change")
    _update_submodule_pointer(repo_with_submodule, "Update to main commit")

    # Invoke merge
    result = CliRunner().invoke(worktree, ["merge", "conflict-test"])

    # Verify no traceback in output
    assert "Traceback" not in result.output, (
        f"merge should not raise uncaught exception, got: {result.output}"
    )

    # Verify exit code is 0 or 3 (not uncaught exception)
    assert result.exit_code in (0, 3), (
        f"merge should exit with 0 or 3, got {result.exit_code}: {result.output}"
    )

    # Verify agent-core MERGE_HEAD exists (conflict preserved)
    merge_head_check = subprocess.run(
        ["git", "-C", str(agent_core_path), "rev-parse", "--verify", "MERGE_HEAD"],
        capture_output=True,
        check=False,
    )
    assert merge_head_check.returncode == 0, (
        "agent-core MERGE_HEAD should exist after submodule conflict"
    )


def test_merge_resume_after_submodule_resolution(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
    commit_file: Callable[[Path, str, str, str], None],
) -> None:
    """Verify merge succeeds after manual submodule conflict resolution.

    Scenario:
    - First merge creates submodule conflict (exit 3)
    - Manually resolve agent-core conflict and commit
    - Stage the updated agent-core pointer
    - Re-run merge → should succeed (exit 0)
    - Verify commit log shows both resolution and final merge commits
    """
    monkeypatch.chdir(repo_with_submodule)

    agent_core_path = repo_with_submodule / "agent-core"

    # Create a base commit on main in a file in agent-core
    commit_file(agent_core_path, "conflict.txt", "base content", "Base change")
    base_commit = subprocess.run(
        ["git", "-C", str(agent_core_path), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    _update_submodule_pointer(repo_with_submodule, "Update to base commit")

    # Create branch and worktree
    subprocess.run(
        ["git", "branch", "resume-test"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    result = CliRunner().invoke(worktree, ["new", "resume-test"])
    assert result.exit_code == 0

    # In worktree's agent-core, create conflicting change
    wt_agent_core = (
        repo_with_submodule.parent
        / f"{repo_with_submodule.name}-wt"
        / "resume-test"
        / "agent-core"
    )
    commit_file(wt_agent_core, "conflict.txt", "wt change", "Worktree conflict change")
    wt_commit = subprocess.run(
        ["git", "-C", str(wt_agent_core), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    # Update worktree's submodule pointer
    wt_branch = repo_with_submodule.parent / f"{repo_with_submodule.name}-wt" / "resume-test"
    _update_submodule_pointer(wt_branch, "Update wt pointer to conflict commit")

    # Back on main, create a different change to the same file (real conflict)
    commit_file(agent_core_path, "conflict.txt", "main change", "Main conflict change")
    _update_submodule_pointer(repo_with_submodule, "Update to main commit")

    # First merge: should fail with submodule conflict (exit 3)
    result = CliRunner().invoke(worktree, ["merge", "resume-test"])
    assert result.exit_code in (0, 3), (
        f"First merge should exit 0 or 3, got {result.exit_code}: {result.output}"
    )

    # Manually resolve submodule conflict
    subprocess.run(
        ["git", "-C", str(agent_core_path), "checkout", "--theirs", "conflict.txt"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(agent_core_path), "add", "conflict.txt"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(agent_core_path), "commit", "-m", "Resolve submodule conflict"],
        check=True,
        capture_output=True,
    )

    # Stage the updated agent-core pointer
    subprocess.run(
        ["git", "add", "agent-core"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    # Second merge: should succeed (exit 0)
    result = CliRunner().invoke(worktree, ["merge", "resume-test"])
    assert result.exit_code == 0, (
        f"Second merge should exit 0, got {result.exit_code}: {result.output}"
    )

    # Verify wt_commit is ancestor of current agent-core HEAD
    ancestor_check = subprocess.run(
        [
            "git",
            "-C",
            str(agent_core_path),
            "merge-base",
            "--is-ancestor",
            wt_commit,
            "HEAD",
        ],
        check=False,
    )
    assert ancestor_check.returncode == 0, (
        "wt_commit should be ancestor of agent-core HEAD after resolution"
    )

    # Verify git log shows merge commits
    # After first merge: creates parent merge commit (even with submodule conflict)
    # After manual submodule resolution and second merge: creates another parent merge commit
    # (because agent-core staged changes trigger Phase 4 commit)
    log_output = subprocess.run(
        ["git", "log", "-2", "--format=%s"],
        cwd=repo_with_submodule,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    recent_commits = log_output.split("\n")

    # Both commits should be merge commits
    assert len(recent_commits) >= 2, (
        f"Expected at least 2 commits in log, got {len(recent_commits)}: {recent_commits}"
    )
    assert recent_commits[0] == "🔀 Merge resume-test", (
        f"Latest commit should be parent merge, got: {recent_commits[0]}"
    )
    assert recent_commits[1] == "🔀 Merge resume-test", (
        f"Second commit should also be parent merge, got: {recent_commits[1]}"
    )
