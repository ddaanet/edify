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
            if "merge-base" in cmd:
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

    commit_message = subprocess.run(
        ["git", "log", "-1", "--format=%s"],
        cwd=repo_with_submodule,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    assert "🔀 Merge agent-core from merge-test" in commit_message, (
        f"commit message should reflect merge, got: {commit_message}"
    )
