"""Tests for remerge_session_md (phase 4 structural merge)."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree
from claudeutils.worktree.remerge import remerge_session_md
from claudeutils.worktree.resolve import _merge_session_contents


def _git_helper(*args: str, cwd: Path | None = None) -> str:
    """Run git command, return stdout."""
    r = subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    )
    return r.stdout.strip()


def _write_commit(path: Path, filepath: str, content: str, msg: str) -> None:
    """Write file, stage, commit."""
    (path / filepath).parent.mkdir(parents=True, exist_ok=True)
    (path / filepath).write_text(content)
    _git_helper("add", filepath, cwd=path)
    _git_helper("commit", "-m", msg, cwd=path)


# --- Pure function tests ---


def test_merge_session_modified_blocker_keeps_ours() -> None:
    """Blocker with same first line on both sides → ours version kept."""
    ours = (
        "# Session: Test\n"
        "\n"
        "## Blockers / Gotchas\n"
        "\n"
        "- Known issue X\n"
        "  Original details from main\n"
    )
    theirs = (
        "# Session: Branch\n"
        "\n"
        "## Blockers / Gotchas\n"
        "\n"
        "- Known issue X\n"
        "  Modified details from branch\n"
    )
    result = _merge_session_contents(ours, theirs)
    assert "Original details from main" in result
    assert "Modified details from branch" not in result


# --- Remerge unit tests ---


MAIN_SESSION = (
    "# Session Handoff: 2026-01-02\n"
    "\n"
    "**Status:** Updated on main\n"
    "\n"
    "## Completed This Session\n"
    "\n"
    "- Did main work\n"
    "\n"
    "## In-tree Tasks\n"
    "\n"
    "- [ ] **Task A** — first task\n"
    "- [ ] **Task B** — second task\n"
    "- [ ] **Task C** — third task\n"
    "\n"
    "## Worktree Tasks\n"
    "\n"
    "- [ ] **Other Task** → `other-slug` — other work\n"
    "\n"
    "## Reference Files\n"
    "\n"
    "- `path/to/file.py` — reference\n"
)

FOCUSED_SESSION = (
    "# Session: Worktree — Task A\n"
    "\n"
    "**Status:** Focused worktree for parallel execution.\n"
    "\n"
    "## In-tree Tasks\n"
    "\n"
    "- [ ] **Task A** — first task\n"
    "- [ ] **Task D** — new task from branch\n"
)


def test_remerge_session_md_structural_merge(
    tmp_path: Path, monkeypatch: MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """remerge_session_md structurally merges session.md using HEAD/MERGE_HEAD.

    Main has full session (WT section, 3 tasks, refs). Branch has focused
    session (1 task + 1 new). After remerge, main's structure preserved +
    branch's new task added.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)
    _write_commit(repo, "agents/session.md", MAIN_SESSION, "Base")

    # Branch: focused session with new task
    subprocess.run(
        ["git", "checkout", "-b", "test-wt"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    _write_commit(repo, "agents/session.md", FOCUSED_SESSION, "Branch: focused session")

    # Main: diverge so merge isn't fast-forward
    subprocess.run(
        ["git", "checkout", "main"], cwd=repo, check=True, capture_output=True
    )
    _write_commit(repo, "dummy.txt", "force divergence\n", "Main: diverge")

    # Start merge (--no-commit keeps MERGE_HEAD)
    subprocess.run(
        ["git", "merge", "--no-commit", "--no-ff", "test-wt"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )

    monkeypatch.chdir(repo)
    remerge_session_md("test-wt")

    merged = (repo / "agents" / "session.md").read_text()
    # Main's structure preserved
    assert "**Status:** Updated on main" in merged
    assert "## Worktree Tasks" in merged
    assert "**Other Task**" in merged
    assert "## Reference Files" in merged
    assert "path/to/file.py" in merged
    # All original tasks preserved
    assert "**Task A**" in merged
    assert "**Task B**" in merged
    assert "**Task C**" in merged
    # Branch's new task added
    assert "**Task D**" in merged


def test_remerge_session_md_skips_without_merge_head(
    tmp_path: Path, monkeypatch: MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """remerge_session_md is a no-op when MERGE_HEAD is absent."""
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)
    _write_commit(repo, "agents/session.md", MAIN_SESSION, "Session commit")

    monkeypatch.chdir(repo)
    original = (repo / "agents" / "session.md").read_text()
    remerge_session_md("some-slug")
    assert (repo / "agents" / "session.md").read_text() == original


def test_remerge_session_md_skips_without_session_file(
    tmp_path: Path, monkeypatch: MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """remerge_session_md returns without error when no session.md on disk."""
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)

    # Create a branch and merge to get MERGE_HEAD
    subprocess.run(
        ["git", "checkout", "-b", "test-br"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    _write_commit(repo, "branch.txt", "branch\n", "Branch")
    subprocess.run(
        ["git", "checkout", "main"], cwd=repo, check=True, capture_output=True
    )
    _write_commit(repo, "main.txt", "main\n", "Main diverge")
    subprocess.run(
        ["git", "merge", "--no-commit", "--no-ff", "test-br"],
        cwd=repo,
        capture_output=True,
        check=False,
    )

    monkeypatch.chdir(repo)
    # No agents/session.md on disk — should return without error
    remerge_session_md("test-br")


# --- Pipeline integration tests ---


def _setup_merge_worktree(repo: Path, slug: str = "test-merge") -> Path:
    """Create branch and worktree, return worktree path."""
    _git_helper("branch", slug, cwd=repo)
    result = CliRunner().invoke(worktree, ["new", "--branch", slug])
    assert result.exit_code == 0, f"new failed: {result.output}"
    return repo.parent / f"{repo.name}-wt" / slug


def test_merge_clean_path_preserves_session_structure(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
) -> None:
    """Full merge pipeline: clean-merge path preserves WT section and tasks.

    Main has full session (WT section, multiple tasks, reference files).
    Branch has focused session (drops most sections). Only branch modifies
    session.md, so git resolves cleanly — taking branch's version, which loses
    main's structure. remerge_session_md in phase 4 fixes this.
    """
    _write_commit(repo_with_submodule, ".gitignore", "wt/\n", "Add gitignore")

    # Set up main's session with rich structure
    main_session = (
        "# Session Handoff: 2026-01-02\n"
        "\n"
        "**Status:** Main status\n"
        "\n"
        "## In-tree Tasks\n"
        "\n"
        "- [ ] **Task A** — first task\n"
        "- [ ] **Task B** — second task\n"
        "- [ ] **Task C** — third task\n"
        "\n"
        "## Worktree Tasks\n"
        "\n"
        "- [ ] **Other WT Task** → `other-slug` — other work\n"
        "\n"
        "## Reference Files\n"
        "\n"
        "- `path/to/file.py` — reference\n"
    )
    _write_commit(
        repo_with_submodule, "agents/session.md", main_session, "Main session"
    )

    # Create worktree (branch from main's HEAD which has main_session)
    wt_path = _setup_merge_worktree(repo_with_submodule)

    # Branch: focused session (drops most sections, adds new task)
    branch_session = (
        "# Session: Worktree — Task A\n"
        "\n"
        "**Status:** Focused worktree for parallel execution.\n"
        "\n"
        "## In-tree Tasks\n"
        "\n"
        "- [ ] **Task A** — first task\n"
        "- [ ] **New Branch Task** — discovered during work\n"
        "\n"
        "## Blockers / Gotchas\n"
        "\n"
        "- Branch discovered a blocker\n"
    )
    _write_commit(
        wt_path, "agents/session.md", branch_session, "Branch focused session"
    )

    # Merge (main hasn't changed session.md since branch point → clean merge)
    result = CliRunner().invoke(worktree, ["merge", "test-merge"])
    assert result.exit_code == 0, f"merge failed: {result.output}"

    merged = (repo_with_submodule / "agents" / "session.md").read_text()

    # Main's structure preserved
    assert "**Status:** Main status" in merged
    assert "## Worktree Tasks" in merged
    assert "**Other WT Task**" in merged
    assert "## Reference Files" in merged
    assert "path/to/file.py" in merged

    # All original tasks preserved
    assert "**Task A**" in merged
    assert "**Task B**" in merged
    assert "**Task C**" in merged

    # Branch's new task added
    assert "**New Branch Task**" in merged

    # Branch's new blocker tagged with [from: slug]
    assert "Branch discovered a blocker" in merged
    assert "[from: test-merge]" in merged
