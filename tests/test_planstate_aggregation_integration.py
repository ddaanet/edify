"""Integration tests for planstate aggregation (git worktree operations)."""

import os
import subprocess
from pathlib import Path

from claudeutils.planstate.aggregation import (
    AggregatedStatus,
    _task_summary,
    aggregate_trees,
)


def _init_git_repo(repo_path: str) -> None:
    """Initialize a git repository with standard config."""
    subprocess.run(
        ["git", "init"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )


def test_task_summary_extraction(tmp_path: Path) -> None:
    """Extract first pending task name from session.md."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    repo_str = str(repo_path)

    _init_git_repo(repo_str)

    # Create session.md with In-tree Tasks section
    session_dir = repo_path / "agents"
    session_dir.mkdir(parents=True, exist_ok=True)
    session_file = session_dir / "session.md"
    session_content = "# Session\n\n## In-tree Tasks\n- [ ] **Fix bug** — description\n"
    session_file.write_text(session_content)
    subprocess.run(
        ["git", "add", "agents/session.md"],
        cwd=repo_str,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial session"],
        cwd=repo_str,
        check=True,
        capture_output=True,
    )

    result = _task_summary(repo_path)
    assert result == "Fix bug"

    # No In-tree Tasks section → None
    session_file.write_text("# Session\n\n## Other Section\n")
    result = _task_summary(repo_path)
    assert result is None

    # Empty In-tree Tasks → None
    session_file.write_text("# Session\n\n## In-tree Tasks\n")
    result = _task_summary(repo_path)
    assert result is None

    # Missing session.md → None
    session_file.unlink()
    result = _task_summary(repo_path)
    assert result is None


def test_tree_sorting_by_timestamp(tmp_path: Path) -> None:
    """Sort trees by latest_commit_timestamp descending."""
    main_repo = tmp_path / "main"
    main_repo.mkdir()
    _init_git_repo(str(main_repo))

    # Main commit at T1 (oldest)
    test_file = main_repo / "main.txt"
    test_file.write_text("main content\n")
    env_t1 = {
        **os.environ,
        "GIT_AUTHOR_DATE": "1000000000 +0000",
        "GIT_COMMITTER_DATE": "1000000000 +0000",
    }
    subprocess.run(
        ["git", "add", "main.txt"],
        cwd=str(main_repo),
        check=True,
        capture_output=True,
        env=env_t1,
    )
    subprocess.run(
        ["git", "commit", "-m", "Main commit"],
        cwd=str(main_repo),
        check=True,
        capture_output=True,
        env=env_t1,
    )

    # Worktree-1 at T2 (middle)
    wt1_path = main_repo / "wt" / "worktree-1"
    subprocess.run(
        ["git", "worktree", "add", str(wt1_path), "-b", "worktree-1"],
        cwd=str(main_repo),
        check=True,
        capture_output=True,
    )
    wt1_file = wt1_path / "wt1.txt"
    wt1_file.write_text("worktree1 content\n")
    env_t2 = {
        **os.environ,
        "GIT_AUTHOR_DATE": "1000000100 +0000",
        "GIT_COMMITTER_DATE": "1000000100 +0000",
    }
    subprocess.run(
        ["git", "add", "wt1.txt"],
        cwd=str(wt1_path),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Worktree-1 commit"],
        cwd=str(wt1_path),
        check=True,
        capture_output=True,
        env=env_t2,
    )

    # Worktree-2 at T3 (newest)
    wt2_path = main_repo / "wt" / "worktree-2"
    subprocess.run(
        ["git", "worktree", "add", str(wt2_path), "-b", "worktree-2"],
        cwd=str(main_repo),
        check=True,
        capture_output=True,
    )
    wt2_file = wt2_path / "wt2.txt"
    wt2_file.write_text("worktree2 content\n")
    env_t3 = {
        **os.environ,
        "GIT_AUTHOR_DATE": "1000000200 +0000",
        "GIT_COMMITTER_DATE": "1000000200 +0000",
    }
    subprocess.run(
        ["git", "add", "wt2.txt"],
        cwd=str(wt2_path),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Worktree-2 commit"],
        cwd=str(wt2_path),
        check=True,
        capture_output=True,
        env=env_t3,
    )

    result = aggregate_trees(main_repo)

    assert hasattr(result, "trees")
    assert len(result.trees) == 3

    # Descending: worktree-2 (T3), worktree-1 (T2), main (T1)
    assert result.trees[0].slug == "worktree-2"
    assert result.trees[1].slug == "worktree-1"
    assert result.trees[2].is_main is True

    assert (
        result.trees[0].latest_commit_timestamp
        > result.trees[1].latest_commit_timestamp
    )
    assert (
        result.trees[1].latest_commit_timestamp
        > result.trees[2].latest_commit_timestamp
    )

    for tree in result.trees:
        assert isinstance(tree.latest_commit_timestamp, int)


def test_per_tree_plan_discovery(tmp_path: Path) -> None:
    """Discover plans from each tree and aggregate with deduplication."""
    main_repo = tmp_path / "main"
    main_repo.mkdir()
    _init_git_repo(str(main_repo))

    # plan-a in main
    plans_dir = main_repo / "plans"
    plans_dir.mkdir()
    plan_a = plans_dir / "plan-a"
    plan_a.mkdir()
    (plan_a / "requirements.md").write_text("# Plan A\n")
    subprocess.run(
        ["git", "add", "plans/"],
        cwd=str(main_repo),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add plan-a"],
        cwd=str(main_repo),
        check=True,
        capture_output=True,
    )

    # plan-b in worktree
    wt_path = main_repo / "wt" / "worktree-1"
    subprocess.run(
        ["git", "worktree", "add", str(wt_path), "-b", "worktree-1"],
        cwd=str(main_repo),
        check=True,
        capture_output=True,
    )
    wt_plans = wt_path / "plans"
    wt_plans.mkdir(exist_ok=True)
    plan_b = wt_plans / "plan-b"
    plan_b.mkdir()
    (plan_b / "design.md").write_text("# Plan B Design\n")
    subprocess.run(
        ["git", "add", "plans/"],
        cwd=str(wt_path),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add plan-b"],
        cwd=str(wt_path),
        check=True,
        capture_output=True,
    )

    result = aggregate_trees(main_repo)

    assert isinstance(result, AggregatedStatus)
    assert len(result.plans) == 2
    plan_names = {plan.name for plan in result.plans}
    assert plan_names == {"plan-a", "plan-b"}

    # Deduplication: plan-c in both trees, main wins
    plan_c_main = plans_dir / "plan-c"
    plan_c_main.mkdir()
    (plan_c_main / "outline.md").write_text("# Plan C\n")
    subprocess.run(
        ["git", "add", "plans/plan-c/"],
        cwd=str(main_repo),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add plan-c in main"],
        cwd=str(main_repo),
        check=True,
        capture_output=True,
    )

    plan_c_wt = wt_plans / "plan-c"
    plan_c_wt.mkdir()
    (plan_c_wt / "requirements.md").write_text("# Plan C Reqs\n")
    subprocess.run(
        ["git", "add", "plans/plan-c/"],
        cwd=str(wt_path),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add plan-c in worktree"],
        cwd=str(wt_path),
        check=True,
        capture_output=True,
    )

    result = aggregate_trees(main_repo)
    plan_c_results = [p for p in result.plans if p.name == "plan-c"]
    assert len(plan_c_results) == 1

    # Verify main tree won (has outline.md, not requirements.md)
    assert "outline.md" in plan_c_results[0].artifacts
    assert "requirements.md" not in plan_c_results[0].artifacts
