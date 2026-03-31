"""Tests for merge() routing logic based on merge state detection."""

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from edify.worktree.cli import worktree
from edify.worktree.git_ops import _is_branch_merged
from edify.worktree.merge import merge
from edify.worktree.merge_state import _detect_merge_state


def _run(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def _commit_file(repo: Path, name: str, content: str, msg: str) -> None:
    (repo / name).write_text(content)
    _run(repo, "add", name)
    _run(repo, "commit", "-m", msg)


def _has_merge_head(repo: Path | None = None) -> bool:
    args = ["git"]
    if repo:
        args.extend(["-C", str(repo)])
    args.extend(["rev-parse", "--verify", "MERGE_HEAD"])
    return subprocess.run(args, check=False, capture_output=True).returncode == 0


def _parent_count() -> int:
    out = subprocess.run(
        ["git", "cat-file", "-p", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return len([line for line in out.split("\n") if line.startswith("parent ")])


def _setup_diverged_branch(
    repo: Path, branch: str, branch_file: str = "branch.txt"
) -> None:
    """Create a branch with one commit, return to main, add diverging commit."""
    _run(repo, "checkout", "-b", branch)
    _commit_file(repo, branch_file, "branch content\n", "Add branch file")
    _run(repo, "checkout", "main")
    _commit_file(repo, "main2.txt", "main commit 2\n", "Second commit on main")


def test_merge_merged_state_routes_through_phase1_2_4(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
) -> None:
    """Test merge() with already-merged branch succeeds via Phase 1+2+4.

    When branch is ancestor of HEAD, merge(slug) should:
    - Detect 'merged' state
    - Run Phase 1 (validate), Phase 2 (submodule no-op), Phase 4 (precommit)
    - Exit with code 0
    - Branch remains merged after call
    """
    monkeypatch.chdir(repo_with_submodule)

    _commit_file(repo_with_submodule, "main.txt", "main content\n", "Initial commit")
    _setup_diverged_branch(repo_with_submodule, "test-branch")

    # Merge the branch first to create "merged" state
    _run(repo_with_submodule, "merge", "--no-edit", "test-branch")
    assert _is_branch_merged("test-branch"), "Branch should be merged before test"

    _run(repo_with_submodule, "rev-parse", "HEAD").stdout.strip()

    # Call merge() on already-merged branch — should succeed
    merge("test-branch")

    assert _is_branch_merged("test-branch"), "Branch should still be merged"


def test_merge_resumes_from_parent_resolved(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
) -> None:
    """Test merge resumes from parent_resolved state.

    Repo has MERGE_HEAD with no unresolved conflicts. merge(slug) should:
    - Exit with code 0
    - Create a merge commit (HEAD has 2+ parents)
    - Not raise CalledProcessError from clean tree check
    """
    monkeypatch.chdir(repo_with_submodule)

    _commit_file(repo_with_submodule, "main.txt", "main content\n", "Initial commit")

    _run(repo_with_submodule, "checkout", "-b", "feature-branch")
    _commit_file(
        repo_with_submodule, "branch-file.txt", "branch content\n", "Add branch file"
    )
    _run(repo_with_submodule, "checkout", "main")
    _commit_file(repo_with_submodule, "other.txt", "other content\n", "Add other file")

    # Start merge manually (not committed yet)
    merge_result = subprocess.run(
        ["git", "merge", "--no-commit", "--no-ff", "feature-branch"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert merge_result.returncode == 0, "Merge should succeed with auto-resolution"

    conflicts = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert not conflicts.stdout.strip(), (
        f"Expected no conflicts, got: {conflicts.stdout}"
    )
    assert _has_merge_head(), "MERGE_HEAD should exist"

    merge("feature-branch")

    assert not _has_merge_head(), "MERGE_HEAD should be removed after merge()"
    assert _parent_count() >= 2, "Expected merge commit with 2+ parents"


def test_merge_continues_to_phase3_when_submodule_conflicts(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
) -> None:
    """Test merge routes submodule_conflicts state to Phase 3.

    When plugin has MERGE_HEAD (mid-merge), calling merge(slug) should:
    - Detect submodule_conflicts state (not clean)
    - Skip the clean-tree check
    - Route to Phase 3 (merge parent)
    - Exit with code 0 or 3 (not 1 from clean-tree check)
    """
    monkeypatch.chdir(repo_with_submodule)

    _commit_file(repo_with_submodule, "main.txt", "main content\n", "Initial commit")

    _run(repo_with_submodule, "checkout", "-b", "test-branch")
    _commit_file(
        repo_with_submodule, "branch.txt", "branch content\n", "Add branch file"
    )
    _run(repo_with_submodule, "checkout", "main")

    # Create conflicting commits on plugin
    agent_core = repo_with_submodule / "plugin"
    _commit_file(agent_core, "feature.py", "main feature\n", "Main feature")

    _run(agent_core, "checkout", "-b", "ac-feature")
    _commit_file(agent_core, "feature.py", "branch feature\n", "Branch feature")
    _run(agent_core, "checkout", "main")

    # Put plugin in mid-merge state
    merge_result = subprocess.run(
        ["git", "-C", str(agent_core), "merge", "--no-commit", "--no-ff", "ac-feature"],
        capture_output=True,
        text=True,
        check=False,
    )
    if merge_result.returncode != 0:
        _run(agent_core, "checkout", "--ours", "feature.py")
        _run(agent_core, "add", "feature.py")

    assert _has_merge_head(agent_core), "plugin should have MERGE_HEAD"

    state = _detect_merge_state("test-branch")
    assert state == "submodule_conflicts", (
        f"Expected submodule_conflicts state, got {state}"
    )

    runner = CliRunner()
    result = runner.invoke(worktree, ["merge", "test-branch"])

    assert result.exit_code == 3, (
        f"Expected 3 (submodule MERGE_HEAD persists), got"
        f" {result.exit_code}. Output: {result.output}"
    )


def test_merge_clean_state_runs_full_pipeline(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
) -> None:
    """Test merge(clean) routes through all 4 phases.

    When no merge is in progress and branch is not merged, merge(slug) should:
    - Detect 'clean' state
    - Run Phase 1 (validate clean trees)
    - Run Phase 2 (resolve submodule if needed)
    - Run Phase 3 (merge parent)
    - Run Phase 4 (commit and precommit)
    - Result: HEAD has exactly 2 parents (merge commit), exit code 0
    - _is_branch_merged(slug) returns True after call
    """
    monkeypatch.chdir(repo_with_submodule)

    _commit_file(repo_with_submodule, "main.txt", "main content\n", "Initial commit")
    _setup_diverged_branch(repo_with_submodule, "test-branch")

    assert not _has_merge_head(), "Should start in clean state (no MERGE_HEAD)"
    assert not _is_branch_merged("test-branch"), "Branch should not be merged yet"

    merge("test-branch")

    assert _parent_count() == 2, "Expected exactly 2 parents (merge commit)"

    commit_msg = subprocess.run(
        ["git", "log", "-1", "--format=%s"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert commit_msg.startswith("🔀 Merge"), (
        f"Expected merge commit message starting with '🔀 Merge', got: {commit_msg}"
    )

    assert _is_branch_merged("test-branch"), "Branch should be merged after merge()"
    assert not _has_merge_head(), "MERGE_HEAD should be removed after merge()"


def test_merge_reports_and_exits_3_when_parent_conflicts(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test merge exits with code 3 when parent merge has unresolved conflicts.

    Repo has MERGE_HEAD with unresolved conflicts. merge(slug) should:
    - Exit with code 3
    - Not run --abort or clean
    - MERGE_HEAD still exists after call
    - Output contains name of conflicted file
    - No traceback in output
    """
    monkeypatch.chdir(repo_with_submodule)

    _commit_file(repo_with_submodule, "main.txt", "main content\n", "Initial commit")

    _run(repo_with_submodule, "checkout", "-b", "conflict-branch")
    (repo_with_submodule / "src").mkdir(parents=True, exist_ok=True)
    _commit_file(
        repo_with_submodule,
        "src/feature.py",
        "branch version\n",
        "Add feature on branch",
    )

    _run(repo_with_submodule, "checkout", "main")
    (repo_with_submodule / "src").mkdir(parents=True, exist_ok=True)
    _commit_file(
        repo_with_submodule, "src/feature.py", "main version\n", "Add feature on main"
    )

    # Start merge manually (will have conflicts)
    subprocess.run(
        ["git", "merge", "--no-commit", "--no-ff", "conflict-branch"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert _has_merge_head(), "MERGE_HEAD should exist"

    conflicts = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert conflicts.stdout.strip(), "Expected unresolved conflicts"

    runner = CliRunner()
    result = runner.invoke(worktree, ["merge", "conflict-branch"])

    assert result.exit_code == 3, (
        f"Expected exit code 3, got {result.exit_code}. Output: {result.output}"
    )
    assert _has_merge_head(), "MERGE_HEAD should still exist after merge()"
    assert "feature.py" in result.output, (
        f"Expected 'feature.py' in output, got: {result.output}"
    )
    assert "Traceback" not in result.output, (
        f"Expected no traceback, got: {result.output}"
    )
