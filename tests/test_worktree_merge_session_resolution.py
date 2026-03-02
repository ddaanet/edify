"""Tests for session.md merge resolution (pure function)."""

import subprocess
from pathlib import Path

import pytest

from claudeutils.worktree.resolve import (
    _merge_session_contents,
    resolve_session_md,
)


def test_merge_session_preserves_new_blockers() -> None:
    """Blockers from theirs not in ours are added to merged output."""
    ours = (
        "# Session: Test\n"
        "\n"
        "## In-tree Tasks\n"
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
        "## In-tree Tasks\n"
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
    ours = "# Session: Test\n\n## In-tree Tasks\n\n- [ ] **Task A** — existing task\n"
    theirs = (
        "# Session: Branch\n"
        "\n"
        "## In-tree Tasks\n"
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
        "## In-tree Tasks\n"
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
        "## In-tree Tasks\n"
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
    ours = "# Session: Test\n\n## In-tree Tasks\n\n- [ ] **Task A** — existing\n"
    theirs = (
        "# Session: Branch\n"
        "\n"
        "## In-tree Tasks\n"
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


def test_merge_session_worktree_tasks_additive() -> None:
    """New task in Worktree Tasks from theirs is merged into ours' section."""
    ours = (
        "# Session: Test\n"
        "\n"
        "## In-tree Tasks\n"
        "\n"
        "- [ ] **Task A** — in-tree task\n"
        "\n"
        "## Worktree Tasks\n"
        "\n"
        "- [ ] **WT Task 1** → `wt1` — existing worktree task\n"
    )
    theirs = (
        "# Session: Branch\n"
        "\n"
        "## In-tree Tasks\n"
        "\n"
        "- [ ] **Task A** — in-tree task\n"
        "\n"
        "## Worktree Tasks\n"
        "\n"
        "- [ ] **WT Task 1** → `wt1` — existing worktree task\n"
        "- [ ] **WT Task 2** → `wt2` — new worktree task\n"
    )
    result = _merge_session_contents(ours, theirs)
    assert "**WT Task 1**" in result
    assert "**WT Task 2**" in result
    # Verify both are in Worktree Tasks section
    assert "## Worktree Tasks" in result
    assert result.index("**WT Task 1**") < result.index("**WT Task 2**")


def test_merge_session_both_sections_additive() -> None:
    """New tasks in both sections are merged into their respective sections."""
    ours = (
        "# Session: Test\n"
        "\n"
        "## In-tree Tasks\n"
        "\n"
        "- [ ] **In-tree A** — existing in-tree\n"
        "\n"
        "## Worktree Tasks\n"
        "\n"
        "- [ ] **WT A** → `wt-a` — existing wt\n"
    )
    theirs = (
        "# Session: Branch\n"
        "\n"
        "## In-tree Tasks\n"
        "\n"
        "- [ ] **In-tree A** — existing in-tree\n"
        "- [ ] **In-tree B** — new in-tree\n"
        "\n"
        "## Worktree Tasks\n"
        "\n"
        "- [ ] **WT A** → `wt-a` — existing wt\n"
        "- [ ] **WT B** → `wt-b` — new wt\n"
    )
    result = _merge_session_contents(ours, theirs)
    # In-tree tasks
    assert "**In-tree A**" in result
    assert "**In-tree B**" in result
    # Worktree tasks
    assert "**WT A**" in result
    assert "**WT B**" in result


def test_resolve_session_md_fallback_outputs_to_stdout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Fallback hash-object path emits diagnostic to stdout, not stderr."""
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "session.md").write_text("# Session\n")
    monkeypatch.chdir(tmp_path)

    def mock_git(*args: str, **kwargs: object) -> str:
        if args[0] == "show" and len(args) > 1 and ":2:" in args[1]:
            return "# Session: Ours\n\n## Pending Tasks\n\n- [ ] **Task A**\n"
        if args[0] == "show" and len(args) > 1 and ":3:" in args[1]:
            return "# Session: Theirs\n\n## Pending Tasks\n\n- [ ] **Task B**\n"
        if args[0] == "add":
            raise subprocess.CalledProcessError(1, ["git", "add", args[1]])
        if args[0] == "hash-object":
            return "abc123def456abc123def456abc123def456abc1"
        if args[0] == "update-index":
            return ""
        return ""

    monkeypatch.setattr("claudeutils.worktree.resolve._git", mock_git)
    resolve_session_md(["agents/session.md"], slug="test")

    captured = capsys.readouterr()
    assert "hash-object" in captured.out, (
        f"Fallback message must go to stdout. out={captured.out!r} err={captured.err!r}"
    )
    assert "hash-object" not in captured.err


def test_merge_session_filters_completed_tasks_from_theirs() -> None:
    """Completed [x] and canceled [-] tasks from theirs are excluded."""
    ours = "# Session: Main\n\n## In-tree Tasks\n\n- [ ] **Task A** — existing task\n"
    theirs = (
        "# Session: Branch\n"
        "\n"
        "## In-tree Tasks\n"
        "\n"
        "- [ ] **Task A** — existing task\n"
        "- [x] **Done Task** — completed in branch\n"
        "- [-] **Canceled Task** — canceled in branch\n"
        "- [ ] **New Task** — genuinely new from branch\n"
    )
    result = _merge_session_contents(ours, theirs)
    assert "**Task A**" in result
    assert "**New Task**" in result
    assert "**Done Task**" not in result
    assert "**Canceled Task**" not in result
