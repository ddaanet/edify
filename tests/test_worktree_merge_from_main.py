"""Tests for from_main direction support in the merge pipeline."""

import contextlib
import subprocess
from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest

from edify.worktree.merge import (
    _format_conflict_report,
    _phase1_validate_clean_trees,
    _phase3_merge_parent,
    _phase4_merge_commit_and_precommit,
    merge,
)
from edify.worktree.remerge import remerge_session_md
from edify.worktree.resolve import resolve_session_md
from tests.fixtures_worktree import _run_git


def _setup_main_merged_into_branch(
    repo: Path, init_repo: Callable[[Path], None]
) -> None:
    """Set up repo on feature branch with main as ancestor of HEAD."""
    repo.mkdir(exist_ok=True)
    init_repo(repo)
    (repo / "main-file.txt").write_text("main content")
    _run_git(repo, "add", "main-file.txt")
    _run_git(repo, "commit", "-m", "main commit")
    _run_git(repo, "checkout", "-b", "feature")
    (repo / "feature.txt").write_text("feature content")
    _run_git(repo, "add", "feature.txt")
    _run_git(repo, "commit", "-m", "feature commit")
    _run_git(repo, "merge", "--no-edit", "main")


def test_merge_accepts_from_main_keyword(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    mock_precommit: None,
) -> None:
    """Merge() accepts from_main=True when main is ancestor of HEAD."""
    repo = tmp_path / "repo"
    _setup_main_merged_into_branch(repo, init_repo)
    monkeypatch.chdir(repo)

    exit_code = 0
    try:
        merge("main", from_main=True)
    except SystemExit as e:
        exit_code = e.code
    assert exit_code == 0, f"Expected exit code 0, got {exit_code}"


def test_phase1_rejects_main_branch_when_from_main(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
) -> None:
    """_phase1_validate_clean_trees exits 2 on main branch."""
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)
    monkeypatch.chdir(repo)

    # HEAD is on main
    result = subprocess.run(
        ["git", "symbolic-ref", "--short", "HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "main", "expected to be on main branch"

    with pytest.raises(SystemExit) as exc_info:
        _phase1_validate_clean_trees("main", from_main=True)

    assert exc_info.value.code == 2


def test_phase1_passes_on_non_main_branch_when_from_main(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
) -> None:
    """_phase1_validate_clean_trees passes on non-main branch with from_main."""
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)
    _run_git(repo, "checkout", "-b", "feature")
    monkeypatch.chdir(repo)

    # Should not raise (no SystemExit)
    _phase1_validate_clean_trees("main", from_main=True)


def test_phase4_skips_lifecycle_when_from_main(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    mock_precommit: None,
) -> None:
    """_phase4 skips lifecycle 'delivered' when from_main=True."""
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)

    _run_git(repo, "checkout", "-b", "feature")
    (repo / "feat.txt").write_text("feat")
    _run_git(repo, "add", "feat.txt")
    _run_git(repo, "commit", "-m", "feat")
    _run_git(repo, "checkout", "main")
    _run_git(repo, "merge", "--no-edit", "feature")
    plans_dir = repo / "plans" / "my-plan"
    plans_dir.mkdir(parents=True)
    lifecycle = plans_dir / "lifecycle.md"
    lifecycle.write_text("reviewed\n")
    _run_git(repo, "add", "plans/")
    _run_git(repo, "commit", "-m", "add plan")

    monkeypatch.chdir(repo)

    with patch(
        "edify.planstate.inference._parse_lifecycle_status",
        return_value="reviewed",
    ):
        _phase4_merge_commit_and_precommit("feature", from_main=True)

    assert "delivered" not in lifecycle.read_text()


def test_format_conflict_report_hints_from_main(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
) -> None:
    """_format_conflict_report includes '--from-main' hint."""
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)

    _run_git(repo, "checkout", "-b", "feature")
    (repo / "conflict.txt").write_text("feature side")
    _run_git(repo, "add", "conflict.txt")
    _run_git(repo, "commit", "-m", "feature conflict")
    _run_git(repo, "checkout", "main")
    (repo / "conflict.txt").write_text("main side")
    _run_git(repo, "add", "conflict.txt")
    _run_git(repo, "commit", "-m", "main conflict")
    subprocess.run(
        ["git", "merge", "--no-commit", "--no-ff", "feature"],
        cwd=repo,
        check=False,
    )
    monkeypatch.chdir(repo)

    report = _format_conflict_report(["conflict.txt"], "main", from_main=True)

    assert "merge --from-main" in report


# ── Cycle 2.1 tests ──────────────────────────────────────────────────────


def _setup_session_md_conflict(
    repo: Path,
    init_repo: Callable[[Path], None],
    *,
    branch_session: str,
    main_session: str,
) -> list[str]:
    """Set up feature branch with session.md merge conflict against main."""
    repo.mkdir(exist_ok=True)
    init_repo(repo)
    agents_dir = repo / "agents"
    agents_dir.mkdir()
    (agents_dir / "session.md").write_text("# Session\n\nInitial content\n")
    _run_git(repo, "add", "agents/session.md")
    _run_git(repo, "commit", "-m", "add session.md")
    _run_git(repo, "checkout", "-b", "feature")
    (agents_dir / "session.md").write_text(branch_session)
    _run_git(repo, "add", "agents/session.md")
    _run_git(repo, "commit", "-m", "branch session")
    _run_git(repo, "checkout", "main")
    (agents_dir / "session.md").write_text(main_session)
    _run_git(repo, "add", "agents/session.md")
    _run_git(repo, "commit", "-m", "main session")
    _run_git(repo, "checkout", "feature")
    subprocess.run(
        ["git", "merge", "--no-commit", "--no-ff", "main"], cwd=repo, check=False
    )
    return ["agents/session.md"]


def test_resolve_session_md_from_main_keeps_ours_exactly(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
) -> None:
    """from_main=True keeps branch session, rejects main's."""
    branch_session = (
        "# Session Handoff: 2026-03-02\n\n"
        "## In-tree Tasks\n\n"
        "- [ ] **Branch task only** — `just test` | sonnet\n"
    )
    main_session = (
        "# Session Handoff: 2026-03-01\n\n"
        "## In-tree Tasks\n\n"
        "- [ ] **Main task A** — `just lint` | sonnet\n"
        "- [ ] **Main task B** — `just precommit` | sonnet\n"
    )

    repo = tmp_path / "repo"
    conflicts = _setup_session_md_conflict(
        repo, init_repo, branch_session=branch_session, main_session=main_session
    )
    monkeypatch.chdir(repo)

    remaining = resolve_session_md(conflicts, slug="main", from_main=True)
    assert "agents/session.md" not in remaining
    result_content = (repo / "agents" / "session.md").read_text()
    assert "Main task A" not in result_content
    assert "Main task B" not in result_content
    assert "Branch task only" in result_content


def test_resolve_session_md_default_direction_still_merges(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
) -> None:
    """Regression: default from_main=False still does additive merge."""
    branch_session = (
        "# Session Handoff: 2026-03-02\n\n"
        "## In-tree Tasks\n\n"
        "- [ ] **Branch task** — `just test` | sonnet\n"
    )
    main_session = (
        "# Session Handoff: 2026-03-01\n\n"
        "## In-tree Tasks\n\n"
        "- [ ] **Main task** — `just lint` | sonnet\n"
    )

    repo = tmp_path / "repo"
    conflicts = _setup_session_md_conflict(
        repo, init_repo, branch_session=branch_session, main_session=main_session
    )
    monkeypatch.chdir(repo)

    remaining = resolve_session_md(conflicts, slug="main")
    assert "agents/session.md" not in remaining
    result_content = (repo / "agents" / "session.md").read_text()
    assert "Branch task" in result_content
    assert "Main task" in result_content


def test_remerge_session_md_from_main_keeps_ours_exactly(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
) -> None:
    """Remerge from_main=True keeps branch session, rejects main's."""
    branch_session = (
        "# Session Handoff: 2026-03-02\n\n"
        "## In-tree Tasks\n\n"
        "- [ ] **Branch task only** — `just test` | sonnet\n"
    )
    main_session = (
        "# Session Handoff: 2026-03-01\n\n"
        "## In-tree Tasks\n\n"
        "- [ ] **Main task A** — `just lint` | sonnet\n"
        "- [ ] **Main task B** — `just precommit` | sonnet\n"
    )

    repo = tmp_path / "repo"
    _setup_session_md_conflict(
        repo, init_repo, branch_session=branch_session, main_session=main_session
    )
    monkeypatch.chdir(repo)

    remerge_session_md(slug="main", from_main=True)

    result_content = (repo / "agents" / "session.md").read_text()
    assert "Main task A" not in result_content
    assert "Main task B" not in result_content
    assert "Branch task only" in result_content


def test_remerge_session_md_default_direction_still_merges(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
) -> None:
    """Regression: remerge default still does additive merge."""
    branch_session = (
        "# Session Handoff: 2026-03-02\n\n"
        "## In-tree Tasks\n\n"
        "- [ ] **Branch task** — `just test` | sonnet\n"
    )
    main_session = (
        "# Session Handoff: 2026-03-01\n\n"
        "## In-tree Tasks\n\n"
        "- [ ] **Main task** — `just lint` | sonnet\n"
    )

    repo = tmp_path / "repo"
    _setup_session_md_conflict(
        repo, init_repo, branch_session=branch_session, main_session=main_session
    )
    monkeypatch.chdir(repo)

    remerge_session_md(slug="main")

    result_content = (repo / "agents" / "session.md").read_text()
    # Additive merge: both tasks should appear
    assert "Branch task" in result_content
    assert "Main task" in result_content


def test_phase3_passes_from_main_to_auto_resolve(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
) -> None:
    """_phase3 forwards from_main to _auto_resolve via conflict path."""
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)

    # Create conflicting file on feature branch
    _run_git(repo, "checkout", "-b", "feature")
    (repo / "shared.txt").write_text("feature version")
    _run_git(repo, "add", "shared.txt")
    _run_git(repo, "commit", "-m", "feature commit")

    # Create conflicting change on main
    _run_git(repo, "checkout", "main")
    (repo / "shared.txt").write_text("main version")
    _run_git(repo, "add", "shared.txt")
    _run_git(repo, "commit", "-m", "main commit")

    monkeypatch.chdir(repo)

    with (
        patch(
            "edify.worktree.merge._auto_resolve_known_conflicts",
            return_value=[],
        ) as mock_resolve,
        contextlib.suppress(SystemExit),
    ):
        _phase3_merge_parent("feature", from_main=True)

    assert mock_resolve.called, "_auto_resolve_known_conflicts must be called"
    _, kwargs = mock_resolve.call_args
    assert kwargs.get("from_main") is True or (
        len(mock_resolve.call_args.args) >= 3 and mock_resolve.call_args.args[2] is True
    )
