"""Tests for session.md merge resolution (pure function + integration)."""

import subprocess
from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

from claudeutils.worktree.resolve import (
    _merge_session_contents,
    resolve_session_md,
)


def test_merge_session_preserves_new_blockers() -> None:
    """Blockers from theirs not in ours are added to merged output."""
    ours = (
        "# Session: Test\n"
        "\n"
        "## Pending Tasks\n"
        "\n"
        "- [ ] **Task A** — existing task\n"
        "\n"
        "## Blockers / Gotchas\n"
        "\n"
        "- Known issue X\n"
    )
    theirs = (
        "# Session: Branch\n"
        "\n"
        "## Pending Tasks\n"
        "\n"
        "- [ ] **Task A** — existing task\n"
        "\n"
        "## Blockers / Gotchas\n"
        "\n"
        "- Known issue X\n"
        "- New blocker Y from branch work\n"
    )
    result = _merge_session_contents(ours, theirs)
    assert "Known issue X" in result
    assert "New blocker Y from branch work" in result


def test_merge_session_preserves_new_tasks() -> None:
    """Tasks from theirs not in ours are added to merged output."""
    ours = "# Session: Test\n\n## Pending Tasks\n\n- [ ] **Task A** — existing task\n"
    theirs = (
        "# Session: Branch\n"
        "\n"
        "## Pending Tasks\n"
        "\n"
        "- [ ] **Task A** — existing task\n"
        "- [ ] **Task B** — new from branch\n"
    )
    result = _merge_session_contents(ours, theirs)
    assert "**Task A**" in result
    assert "**Task B**" in result


def test_merge_session_preserves_tasks_and_blockers() -> None:
    """Both new tasks and new blockers from theirs are preserved."""
    ours = (
        "# Session: Test\n"
        "\n"
        "## Pending Tasks\n"
        "\n"
        "- [ ] **Task A** — existing\n"
        "\n"
        "## Blockers / Gotchas\n"
        "\n"
        "- Existing blocker\n"
    )
    theirs = (
        "# Session: Branch\n"
        "\n"
        "## Pending Tasks\n"
        "\n"
        "- [ ] **Task A** — existing\n"
        "- [ ] **Task C** — branch task\n"
        "\n"
        "## Blockers / Gotchas\n"
        "\n"
        "- Existing blocker\n"
        "- Branch-specific gotcha\n"
    )
    result = _merge_session_contents(ours, theirs)
    assert "**Task A**" in result
    assert "**Task C**" in result
    assert "Existing blocker" in result
    assert "Branch-specific gotcha" in result


def test_merge_session_no_blocker_section_in_ours() -> None:
    """When ours has no Blockers section, one is created from theirs."""
    ours = "# Session: Test\n\n## Pending Tasks\n\n- [ ] **Task A** — existing\n"
    theirs = (
        "# Session: Branch\n"
        "\n"
        "## Pending Tasks\n"
        "\n"
        "- [ ] **Task A** — existing\n"
        "\n"
        "## Blockers / Gotchas\n"
        "\n"
        "- Branch blocker\n"
    )
    result = _merge_session_contents(ours, theirs)
    assert "## Blockers / Gotchas" in result
    assert "Branch blocker" in result


def test_merge_conflict_preserves_branch_session_tasks(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    """Integration test for session.md conflict resolution.

    Merge conflict on session.md preserves new tasks and blockers from branch.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    # Base: session.md with one task
    (repo / "agents").mkdir()
    base_session = (
        "# Session: Test\n\n## Pending Tasks\n\n- [ ] **Task A** — shared task\n"
    )
    (repo / "agents" / "session.md").write_text(base_session)
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Base"], cwd=repo, check=True, capture_output=True
    )

    # Branch: add a new task and blockers section
    subprocess.run(
        ["git", "checkout", "-b", "feature"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    branch_session = (
        "# Session: Branch\n"
        "\n"
        "## Pending Tasks\n"
        "\n"
        "- [ ] **Task A** — shared task\n"
        "- [ ] **Task B** — new from branch\n"
        "\n"
        "## Blockers / Gotchas\n"
        "\n"
        "- Branch discovered blocker\n"
    )
    (repo / "agents" / "session.md").write_text(branch_session)
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Branch changes"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    # Main: modify session.md differently (creates conflict)
    subprocess.run(
        ["git", "checkout", "main"], cwd=repo, check=True, capture_output=True
    )
    main_session = (
        "# Session: Main\n"
        "\n"
        "**Status:** Updated on main\n"
        "\n"
        "## Pending Tasks\n"
        "\n"
        "- [ ] **Task A** — shared task\n"
    )
    (repo / "agents" / "session.md").write_text(main_session)
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Main changes"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    # Merge with --no-commit to get conflict state
    result = subprocess.run(
        ["git", "merge", "--no-commit", "--no-ff", "feature"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0, "Expected merge conflict"

    monkeypatch.chdir(repo)
    conflicts = ["agents/session.md"]
    remaining = resolve_session_md(conflicts)

    assert remaining == []
    resolved = (repo / "agents" / "session.md").read_text()
    # Ours content preserved
    assert "**Status:** Updated on main" in resolved
    assert "**Task A**" in resolved
    # Branch content merged
    assert "**Task B**" in resolved
    assert "Branch discovered blocker" in resolved


def test_resolve_session_md_with_slug_tags_blockers(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    """Integration test: resolve_session_md with slug parameter tags blockers.

    Tests the full call chain from resolve_session_md through _merge_session_contents
    with a slug parameter, verifying blockers get tagged with [from: slug].
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    # Base: session.md with one task and blocker
    (repo / "agents").mkdir()
    base_session = (
        "# Session: Test\n"
        "\n"
        "## Pending Tasks\n"
        "\n"
        "- [ ] **Task A** — shared task\n"
        "\n"
        "## Blockers / Gotchas\n"
        "\n"
        "- Main blocker\n"
        "  Main details\n"
    )
    (repo / "agents" / "session.md").write_text(base_session)
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Base"], cwd=repo, check=True, capture_output=True
    )

    # Branch: add new blockers
    subprocess.run(
        ["git", "checkout", "-b", "test-wt"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    branch_session = (
        "# Session: Branch\n"
        "\n"
        "## Pending Tasks\n"
        "\n"
        "- [ ] **Task A** — shared task\n"
        "\n"
        "## Blockers / Gotchas\n"
        "\n"
        "- Main blocker\n"
        "  Main details\n"
        "\n"
        "- WT blocker 1\n"
        "  WT detail 1\n"
        "\n"
        "- WT blocker 2\n"
        "  WT detail 2\n"
    )
    (repo / "agents" / "session.md").write_text(branch_session)
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Branch changes"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    # Main: modify session.md (creates conflict)
    subprocess.run(
        ["git", "checkout", "main"], cwd=repo, check=True, capture_output=True
    )
    main_session = (
        "# Session: Main\n"
        "\n"
        "**Status:** Updated on main\n"
        "\n"
        "## Pending Tasks\n"
        "\n"
        "- [ ] **Task A** — shared task\n"
        "\n"
        "## Blockers / Gotchas\n"
        "\n"
        "- Main blocker\n"
        "  Main details\n"
    )
    (repo / "agents" / "session.md").write_text(main_session)
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Main changes"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    # Merge with --no-commit to get conflict state
    result = subprocess.run(
        ["git", "merge", "--no-commit", "--no-ff", "test-wt"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0, "Expected merge conflict"

    monkeypatch.chdir(repo)
    conflicts = ["agents/session.md"]
    remaining = resolve_session_md(conflicts, slug="test-wt")

    assert remaining == []
    resolved = (repo / "agents" / "session.md").read_text()
    # Ours content preserved
    assert "**Status:** Updated on main" in resolved
    assert "**Task A**" in resolved
    # Main blocker preserved (not tagged)
    assert "- Main blocker" in resolved
    # WT blockers tagged with [from: test-wt]
    assert "- WT blocker 1 [from: test-wt]" in resolved
    assert "- WT blocker 2 [from: test-wt]" in resolved
    assert "  WT detail 1" in resolved
    assert "  WT detail 2" in resolved
