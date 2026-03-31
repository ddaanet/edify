"""Tests for segment-level diff3 merge of learnings.md."""

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from edify.validation.learnings import parse_segments
from edify.worktree.cli import worktree


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
    result = CliRunner().invoke(worktree, ["new", "--branch", slug])
    assert result.exit_code == 0, f"new failed: {result.output}"
    return repo.parent / f"{repo.name}-wt" / slug


def test_merge_learnings_segment_diff3_prevents_orphans(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
) -> None:
    """Segment diff3 merge prevents orphaned lines on clean-merge path."""
    monkeypatch.chdir(repo_with_submodule)
    _write_commit(repo_with_submodule, ".gitignore", "wt/\n", "Add gitignore")
    wt_path = _setup_merge_worktree(repo_with_submodule)

    preamble = "# Learnings\n\nSoft limit: 80 lines.\n\n---\n"
    base = (
        preamble
        + "## When analyzing X\n- bullet A1\n- bullet A2\n"
        + "## When selecting Y\n- bullet B1\n- bullet B2\n"
    )

    (repo_with_submodule / "agents").mkdir(exist_ok=True)
    (wt_path / "agents").mkdir(exist_ok=True)

    _write_commit(repo_with_submodule, "agents/learnings.md", base, "Base learnings")
    _write_commit(wt_path, "agents/learnings.md", base, "Base learnings")

    # Branch: modify first entry body + add new entry at tail
    branch_content = (
        preamble
        + "## When analyzing X\n- bullet A1 MODIFIED\n- bullet A2\n"
        + "## When selecting Y\n- bullet B1\n- bullet B2\n"
        + "## When comparing Z\n- bullet Z1\n- bullet Z2\n"
    )
    _write_commit(wt_path, "agents/learnings.md", branch_content, "Branch changes")

    # Main: add different new entry at tail
    _git("checkout", "main", cwd=repo_with_submodule)
    main_content = (
        preamble
        + "## When analyzing X\n- bullet A1\n- bullet A2\n"
        + "## When selecting Y\n- bullet B1\n- bullet B2\n"
        + "## When compressing W\n- bullet W1\n- bullet W2\n"
    )
    _write_commit(
        repo_with_submodule, "agents/learnings.md", main_content, "Main adds entry W"
    )

    result = CliRunner().invoke(worktree, ["merge", "test-merge"])
    assert result.exit_code == 0, f"merge should succeed: {result.output}"

    merged_text = (repo_with_submodule / "agents" / "learnings.md").read_text()

    segments = parse_segments(merged_text)

    # All 4 entries present
    assert "When analyzing X" in segments, f"Missing 'When analyzing X': {merged_text}"
    assert "When selecting Y" in segments, f"Missing 'When selecting Y': {merged_text}"
    assert "When comparing Z" in segments, f"Missing 'When comparing Z': {merged_text}"
    assert "When compressing W" in segments, (
        f"Missing 'When compressing W': {merged_text}"
    )

    # Branch's modified body is kept (not base's)
    analyzing_body = segments["When analyzing X"]
    assert "bullet A1 MODIFIED" in "\n".join(analyzing_body), (
        f"Expected modified body for 'When analyzing X': {analyzing_body}"
    )

    # No orphaned content in preamble key
    preamble_content = segments.get("", [])
    orphan_lines = [
        ln
        for ln in preamble_content
        if ln.strip()
        and not ln.strip().startswith("#")
        and not ln.strip().startswith("Soft limit")
        and not ln.strip().startswith("---")
    ]
    assert not orphan_lines, f"Orphaned lines in preamble: {orphan_lines}"


def test_merge_learnings_divergent_edit_produces_conflict(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
) -> None:
    """Same-entry divergent edits produce conflict markers, exit 3."""
    monkeypatch.chdir(repo_with_submodule)
    _write_commit(repo_with_submodule, ".gitignore", "wt/\n", "Add gitignore")
    wt_path = _setup_merge_worktree(repo_with_submodule)

    preamble = "# Learnings\n\nSoft limit: 80 lines.\n\n---\n"
    base = preamble + "## When analyzing X\n- original bullet\n"

    (repo_with_submodule / "agents").mkdir(exist_ok=True)
    (wt_path / "agents").mkdir(exist_ok=True)

    _write_commit(repo_with_submodule, "agents/learnings.md", base, "Base learnings")
    _write_commit(wt_path, "agents/learnings.md", base, "Base learnings")

    # Branch: modify the entry body
    branch_content = preamble + "## When analyzing X\n- branch modified bullet\n"
    _write_commit(wt_path, "agents/learnings.md", branch_content, "Branch edit")

    # Main: modify the SAME entry body differently
    _git("checkout", "main", cwd=repo_with_submodule)
    main_content = preamble + "## When analyzing X\n- main modified bullet\n"
    _write_commit(repo_with_submodule, "agents/learnings.md", main_content, "Main edit")

    result = CliRunner().invoke(worktree, ["merge", "test-merge"])
    assert result.exit_code == 3, f"merge should exit 3 on conflict: {result.output}"

    content = (repo_with_submodule / "agents" / "learnings.md").read_text()
    assert "<<<<<<<" in content, f"Missing conflict marker '<<<<<<<': {content}"
    assert "=======" in content, f"Missing conflict marker '=======': {content}"
    assert ">>>>>>>" in content, f"Missing conflict marker '>>>>>>>': {content}"
    assert "## When analyzing X" in content, f"Heading missing from file: {content}"
    assert "branch modified bullet" in content, f"Branch body missing: {content}"
    assert "main modified bullet" in content, f"Main body missing: {content}"
