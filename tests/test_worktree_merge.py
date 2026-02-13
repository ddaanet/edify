"""Tests for worktree merge operations."""

import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import cast
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree


def test_merge_branch_existence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Verify branch exists and warn about missing worktree directory."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    # Test 1: Branch doesn't exist
    result = CliRunner().invoke(worktree, ["merge", "nonexistent-branch"])
    assert result.exit_code == 2
    assert "Branch nonexistent-branch not found" in result.output

    # Test 2: Branch exists but worktree directory doesn't
    subprocess.run(["git", "branch", "branch-only"], check=True, capture_output=True)
    result = CliRunner().invoke(worktree, ["merge", "branch-only"])
    assert result.exit_code == 0
    assert "Worktree directory not found, merging branch only" in result.output

    # Test 3: Both branch and worktree directory exist
    subprocess.run(["git", "branch", "full-merge"], check=True, capture_output=True)
    result = CliRunner().invoke(worktree, ["new", "full-merge"])
    assert result.exit_code == 0

    result = CliRunner().invoke(worktree, ["merge", "full-merge"])
    assert result.exit_code == 0
    assert "Worktree directory not found" not in result.output


def test_merge_submodule_ancestry(
    repo_with_submodule: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify merge performs submodule commit ancestry check.

    Ancestry check logic:
    - Extract worktree's submodule commit from git ls-tree
    - Get local submodule commit via rev-parse
    - Check if worktree commit is ancestor of local (skips if yes)
    """
    monkeypatch.chdir(repo_with_submodule)

    (repo_with_submodule / ".gitignore").write_text("wt/\n")
    subprocess.run(
        ["git", "add", ".gitignore"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add gitignore"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    subprocess.run(
        ["git", "branch", "test-feature"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    result = CliRunner().invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0

    agent_core_path = repo_with_submodule / "agent-core"
    initial_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=agent_core_path,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    (agent_core_path / "change.txt").write_text("submodule change")
    subprocess.run(
        ["git", "add", "change.txt"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Submodule change"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    new_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=agent_core_path,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    assert initial_commit != new_commit

    result = subprocess.run(
        ["git", "ls-tree", "test-feature", "--", "agent-core"],
        cwd=repo_with_submodule,
        capture_output=True,
        text=True,
        check=True,
    )
    wt_submodule_commit = result.stdout.split()[2]

    assert wt_submodule_commit == initial_commit

    result = subprocess.run(
        [
            "git",
            "-C",
            str(agent_core_path),
            "merge-base",
            "--is-ancestor",
            wt_submodule_commit,
            new_commit,
        ],
        check=False,
    )
    is_ancestor = result.returncode == 0
    assert is_ancestor

    mock_git = MagicMock()
    with patch("claudeutils.worktree.merge._git", mock_git):
        mock_git.return_value = ""
        result = CliRunner().invoke(worktree, ["merge", "test-feature"])
        assert result.exit_code == 0

        ls_tree_called = any("ls-tree" in str(call) for call in mock_git.call_args_list)
        assert ls_tree_called, "merge should extract submodule commit via git ls-tree"


def test_merge_submodule_fetch(
    repo_with_submodule: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify merge checks object reachability and fetches when needed."""
    monkeypatch.chdir(repo_with_submodule)

    (repo_with_submodule / ".gitignore").write_text("wt/\n")
    subprocess.run(
        ["git", "add", ".gitignore"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add gitignore"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    agent_core_path = repo_with_submodule / "agent-core"

    (agent_core_path / "fetch_change.txt").write_text("fetch test change")
    subprocess.run(
        ["git", "add", "fetch_change.txt"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Fetch test change"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    base_commit = subprocess.run(
        ["git", "-C", str(agent_core_path), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    subprocess.run(
        ["git", "add", "agent-core"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Update agent-core pointer"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    subprocess.run(
        ["git", "branch", "fetch-test"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    result = CliRunner().invoke(worktree, ["new", "fetch-test"])
    assert result.exit_code == 0

    subprocess.run(
        ["git", "-C", str(agent_core_path), "reset", "--hard", base_commit],
        check=True,
        capture_output=True,
    )

    (agent_core_path / "diverged_change.txt").write_text("diverged change")
    subprocess.run(
        ["git", "add", "diverged_change.txt"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Diverged change"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    result = subprocess.run(
        ["git", "ls-tree", "fetch-test", "--", "agent-core"],
        cwd=repo_with_submodule,
        capture_output=True,
        text=True,
        check=True,
    )
    if not result.stdout.strip():
        pytest.skip("Branch has no agent-core submodule entry (test setup incomplete)")
    wt_submodule_commit = result.stdout.split()[2]

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


def test_merge_submodule_merge_commit(
    repo_with_submodule: Path, monkeypatch: pytest.MonkeyPatch
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

    (repo_with_submodule / ".gitignore").write_text("wt/\n")
    subprocess.run(
        ["git", "add", ".gitignore"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add gitignore"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    agent_core_path = repo_with_submodule / "agent-core"

    (agent_core_path / "base_change.txt").write_text("base change")
    subprocess.run(
        ["git", "add", "base_change.txt"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Base change"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    subprocess.run(
        ["git", "-C", str(agent_core_path), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    subprocess.run(
        ["git", "add", "agent-core"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Update agent-core to base"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    subprocess.run(
        ["git", "branch", "merge-test"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    result = CliRunner().invoke(worktree, ["new", "merge-test"])
    assert result.exit_code == 0

    (agent_core_path / "main_change.txt").write_text("main change")
    subprocess.run(
        ["git", "add", "main_change.txt"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Main branch change"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    main_commit = subprocess.run(
        ["git", "-C", str(agent_core_path), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    subprocess.run(
        ["git", "add", "agent-core"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Update to main commit"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    wt_agent_core = (
        repo_with_submodule.parent
        / f"{repo_with_submodule.name}-wt"
        / "merge-test"
        / "agent-core"
    )
    (wt_agent_core / "wt_change.txt").write_text("wt change")
    subprocess.run(
        ["git", "add", "wt_change.txt"],
        cwd=wt_agent_core,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Worktree change"],
        cwd=wt_agent_core,
        check=True,
        capture_output=True,
    )

    wt_commit = subprocess.run(
        ["git", "-C", str(wt_agent_core), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    wt_branch = (
        repo_with_submodule.parent / f"{repo_with_submodule.name}-wt" / "merge-test"
    )
    subprocess.run(
        ["git", "add", "agent-core"],
        cwd=wt_branch,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Update wt pointer"],
        cwd=wt_branch,
        check=True,
        capture_output=True,
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
