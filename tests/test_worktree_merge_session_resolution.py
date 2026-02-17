"""Tests for session.md merge resolution (pure function + integration)."""

import subprocess
from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

from claudeutils.worktree.merge import (
    _merge_session_contents,
    _resolve_session_md_conflict,
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
    remaining = _resolve_session_md_conflict(conflicts)

    assert remaining == []
    resolved = (repo / "agents" / "session.md").read_text()
    # Ours content preserved
    assert "**Status:** Updated on main" in resolved
    assert "**Task A**" in resolved
    # Branch content merged
    assert "**Task B**" in resolved
    assert "Branch discovered blocker" in resolved
