"""Tests for worktree merge conflict auto-resolution."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree


def _git(*args: str, cwd: Path | None = None) -> str:
    r = subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    )
    return r.stdout.strip()


def _write_commit(path: Path, filepath: str, content: str, msg: str) -> None:
    (path / filepath).parent.mkdir(parents=True, exist_ok=True)
    (path / filepath).write_text(content)
    _git("add", filepath, cwd=path)
    _git("commit", "-m", msg, cwd=path)


def _setup_merge_worktree(repo: Path, slug: str = "test-merge") -> Path:
    """Create branch and worktree, return worktree path."""
    _git("branch", slug, cwd=repo)
    result = CliRunner().invoke(worktree, ["new", slug])
    assert result.exit_code == 0, f"new failed: {result.output}"
    return repo.parent / f"{repo.name}-wt" / slug


def test_merge_conflict_agent_core(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
    commit_file: Callable[[Path, str, str, str], None],
) -> None:
    """Auto-resolve agent-core conflict (already merged in Phase 2)."""
    monkeypatch.chdir(repo_with_submodule)
    commit_file(repo_with_submodule, ".gitignore", "wt/\n", "Add gitignore")

    wt_path = _setup_merge_worktree(repo_with_submodule)

    # Branch: file change + submodule update
    commit_file(wt_path, "branch-file.txt", "branch content\n", "Branch change")
    (wt_path / "agent-core" / "branch-change.txt").write_text("branch change\n")
    _git("add", "branch-change.txt", cwd=wt_path / "agent-core")
    _git("commit", "-m", "Branch change in submodule", cwd=wt_path / "agent-core")
    _git("add", "agent-core", cwd=wt_path)
    _git("commit", "-m", "Update agent-core on branch", cwd=wt_path)

    # Main: file change + different submodule update
    _git("checkout", "main", cwd=repo_with_submodule)
    commit_file(repo_with_submodule, "main-file.txt", "main content\n", "Main change")
    (repo_with_submodule / "agent-core" / "main-change.txt").write_text("main change\n")
    _git("add", "main-change.txt", cwd=repo_with_submodule / "agent-core")
    _git(
        "commit",
        "-m",
        "Main change in submodule",
        cwd=repo_with_submodule / "agent-core",
    )
    _git("add", "agent-core", cwd=repo_with_submodule)
    _git("commit", "-m", "Update agent-core on main", cwd=repo_with_submodule)

    result = CliRunner().invoke(worktree, ["merge", "test-merge"])
    assert result.exit_code == 0, f"merge should succeed: {result.output}"

    # agent-core auto-resolved
    unmerged = _git("diff", "--name-only", "--diff-filter=U", cwd=repo_with_submodule)
    assert "agent-core" not in unmerged

    # Merge complete (no MERGE_HEAD)
    r = subprocess.run(
        ["git", "rev-parse", "MERGE_HEAD"],
        check=False,
        cwd=repo_with_submodule,
        capture_output=True,
        text=True,
    )
    assert r.returncode != 0, "MERGE_HEAD should not exist after merge"


def _setup_session_conflict(
    repo: Path,
    wt: Path,
    sessions: dict[str, str],
) -> None:
    """Set up session.md conflict scenario on both sides.

    Args:
        repo: Main repo path
        wt: Worktree path
        sessions: Dict with keys 'main', 'wt_base', 'wt_updated', 'main_updated'
    """
    (repo / "agents").mkdir(exist_ok=True)
    (wt / "agents").mkdir(exist_ok=True)

    _write_commit(repo, "agents/session.md", sessions["main"], "Add session.md")
    _write_commit(wt, "agents/session.md", sessions["wt_base"], "Add session.md")
    _write_commit(wt, "agents/session.md", sessions["wt_updated"], "Update session.md")
    _git("checkout", "main", cwd=repo)
    _write_commit(
        repo, "agents/session.md", sessions["main_updated"], "Update session.md on main"
    )


def test_merge_conflict_session_md(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
    commit_file: Callable[[Path, str, str, str], None],
) -> None:
    """Auto-resolve session.md, extract new tasks from worktree."""
    monkeypatch.chdir(repo_with_submodule)
    commit_file(repo_with_submodule, ".gitignore", "wt/\n", "Add gitignore")
    wt_path = _setup_merge_worktree(repo_with_submodule)

    base = "# Session\n\n- [ ] **Task A** — `/design` | sonnet\n"
    _setup_session_conflict(
        repo_with_submodule,
        wt_path,
        {
            "main": base,
            "wt_base": base,
            "wt_updated": base + "- [ ] **Task B** — `/runbook` | haiku\n",
            "main_updated": "# Session\n\n- [ ] **Task A** — `/design` | opus\n",
        },
    )

    result = CliRunner().invoke(worktree, ["merge", "test-merge"])
    assert result.exit_code == 0, f"merge should succeed: {result.output}"

    unmerged = _git("diff", "--name-only", "--diff-filter=U", cwd=repo_with_submodule)
    assert "agents/session.md" not in unmerged

    session = (repo_with_submodule / "agents" / "session.md").read_text()
    assert "Task B" in session, f"Task B missing in: {session}"


def test_merge_conflict_session_md_multiline_blocks(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
    commit_file: Callable[[Path, str, str, str], None],
) -> None:
    """Auto-resolve session.md preserving multi-line task blocks."""
    monkeypatch.chdir(repo_with_submodule)
    commit_file(repo_with_submodule, ".gitignore", "wt/\n", "Add gitignore")
    wt_path = _setup_merge_worktree(repo_with_submodule)

    base = (
        "# Session\n\n## Pending Tasks\n\n"
        "- [ ] **Task A** — `/design` | sonnet\n\n## Blockers\n"
    )
    _setup_session_conflict(
        repo_with_submodule,
        wt_path,
        {
            "main": base,
            "wt_base": base,
            "wt_updated": (
                "# Session\n\n## Pending Tasks\n\n"
                "- [ ] **Task A** — `/design` | sonnet\n"
                "- [ ] **Task B** — `/runbook plans/foo/runbook.md` | haiku\n"
                "  - Plan: foo | Status: planned\n"
                "  - Notes: Multi-line task block\n\n"
                "## Blockers\n"
            ),
            "main_updated": (
                "# Session\n\n## Pending Tasks\n\n"
                "- [ ] **Task A** — `/design` | opus\n\n## Blockers\n"
            ),
        },
    )

    result = CliRunner().invoke(worktree, ["merge", "test-merge"])
    assert result.exit_code == 0, f"merge should succeed: {result.output}"

    unmerged = _git("diff", "--name-only", "--diff-filter=U", cwd=repo_with_submodule)
    assert "agents/session.md" not in unmerged

    session = (repo_with_submodule / "agents" / "session.md").read_text()
    assert "Task B" in session, f"Task B missing: {session}"
    assert "Plan: foo | Status: planned" in session, (
        f"Task B continuation line 1 missing: {session}"
    )
    assert "Notes: Multi-line task block" in session, (
        f"Task B continuation line 2 missing: {session}"
    )


def test_merge_conflict_session_md_insertion_position(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
    commit_file: Callable[[Path, str, str, str], None],
) -> None:
    """New tasks inserted before next section with blank line separation."""
    monkeypatch.chdir(repo_with_submodule)
    commit_file(repo_with_submodule, ".gitignore", "wt/\n", "Add gitignore")
    wt_path = _setup_merge_worktree(repo_with_submodule)

    base = (
        "# Session\n\n## Pending Tasks\n\n"
        "- [ ] **Task A** — `/design` | sonnet\n\n"
        "## Blockers / Gotchas\n\n- Some blocker note\n"
    )
    _setup_session_conflict(
        repo_with_submodule,
        wt_path,
        {
            "main": base,
            "wt_base": base,
            "wt_updated": (
                "# Session\n\n## Pending Tasks\n\n"
                "- [ ] **Task A** — `/design` | sonnet\n"
                "- [ ] **Task B** — `/runbook` | haiku\n\n"
                "## Blockers / Gotchas\n\n- Some blocker note\n"
            ),
            "main_updated": (
                "# Session\n\n## Pending Tasks\n\n"
                "- [ ] **Task A** — `/design` | opus\n\n"
                "## Blockers / Gotchas\n\n- Some blocker note\n"
            ),
        },
    )

    result = CliRunner().invoke(worktree, ["merge", "test-merge"])
    assert result.exit_code == 0, f"merge should succeed: {result.output}"

    session = (repo_with_submodule / "agents" / "session.md").read_text()
    assert "Task B" in session, f"Task B missing: {session}"

    # Task B before Blockers section
    assert session.find("Task B") < session.find("## Blockers")

    # Blank line before Blockers
    lines = session.split("\n")
    blockers_idx = next(i for i, ln in enumerate(lines) if "## Blockers" in ln)
    assert lines[blockers_idx - 1] == "", (
        f"Expected blank line before Blockers, got: {lines[blockers_idx - 1]!r}"
    )


def test_merge_conflict_learnings_md(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
    commit_file: Callable[[Path, str, str, str], None],
) -> None:
    """Auto-resolve learnings.md by keeping ours and appending theirs-only."""
    monkeypatch.chdir(repo_with_submodule)
    commit_file(repo_with_submodule, ".gitignore", "wt/\n", "Add gitignore")
    wt_path = _setup_merge_worktree(repo_with_submodule)

    (repo_with_submodule / "agents").mkdir(exist_ok=True)
    (wt_path / "agents").mkdir(exist_ok=True)

    base = "# Learnings\n\n- Learning A: Common content\n"
    _write_commit(repo_with_submodule, "agents/learnings.md", base, "Add learnings")
    _write_commit(wt_path, "agents/learnings.md", base, "Add learnings")
    _write_commit(
        wt_path,
        "agents/learnings.md",
        base + "- Learning B: Worktree-only learning\n",
        "Add Learning B",
    )
    _git("checkout", "main", cwd=repo_with_submodule)
    _write_commit(
        repo_with_submodule,
        "agents/learnings.md",
        "# Learnings\n\n- Learning A: Common content (modified on main)\n",
        "Update learnings on main",
    )

    result = CliRunner().invoke(worktree, ["merge", "test-merge"])
    assert result.exit_code == 0, f"merge should succeed: {result.output}"

    unmerged = _git("diff", "--name-only", "--diff-filter=U", cwd=repo_with_submodule)
    assert "agents/learnings.md" not in unmerged

    merged = (repo_with_submodule / "agents" / "learnings.md").read_text()
    assert "Common content (modified on main)" in merged
    assert "Learning B" in merged
