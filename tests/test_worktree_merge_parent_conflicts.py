"""Tests for parent_conflicts state routing: auto-resolution and output."""

import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest
from click.testing import CliRunner

from edify.worktree.cli import worktree


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


def _has_merge_head() -> bool:
    return (
        subprocess.run(
            ["git", "rev-parse", "--verify", "MERGE_HEAD"],
            check=False,
            capture_output=True,
        ).returncode
        == 0
    )


def _setup_diverged_branch(repo: Path, branch: str) -> None:
    _run(repo, "checkout", "-b", branch)
    _commit_file(repo, "branch.txt", "branch content\n", "Add branch file")
    _run(repo, "checkout", "main")
    _commit_file(repo, "main2.txt", "main commit 2\n", "Second commit on main")


def test_parent_conflicts_auto_resolves_session_md(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """parent_conflicts auto-resolves session.md, leaving only real conflicts.

    Bug: parent_conflicts branch reports all conflicts without auto-resolution.
    Fix: call _auto_resolve_known_conflicts before reporting remaining conflicts.
    """
    monkeypatch.chdir(repo_with_submodule)
    _commit_file(repo_with_submodule, "main.txt", "content\n", "Init")

    # Branch: session.md change + conflicting src file
    _run(repo_with_submodule, "checkout", "-b", "session-conflict")
    (repo_with_submodule / "src").mkdir(parents=True, exist_ok=True)
    _commit_file(repo_with_submodule, "src/conflict.py", "branch\n", "Branch py")
    session_file = repo_with_submodule / "agents" / "session.md"
    session_file.write_text(
        "# Session: Branch\n\n## In-tree Tasks\n\n- [ ] **Branch task**\n"
    )
    _run(repo_with_submodule, "add", "agents/session.md")
    _run(repo_with_submodule, "commit", "-m", "Branch session")

    # Main: conflicting changes to same files
    _run(repo_with_submodule, "checkout", "main")
    (repo_with_submodule / "src").mkdir(parents=True, exist_ok=True)
    _commit_file(repo_with_submodule, "src/conflict.py", "main\n", "Main py")
    session_file.write_text(
        "# Session: Main\n\n## In-tree Tasks\n\n- [ ] **Main task**\n"
    )
    _run(repo_with_submodule, "add", "agents/session.md")
    _run(repo_with_submodule, "commit", "-m", "Main session")

    subprocess.run(
        ["git", "merge", "--no-commit", "--no-ff", "session-conflict"],
        cwd=repo_with_submodule,
        capture_output=True,
        check=False,
    )
    assert _has_merge_head(), "MERGE_HEAD should exist"

    runner = CliRunner()
    result = runner.invoke(worktree, ["merge", "session-conflict"])

    assert result.exit_code == 3
    # BUG: session.md appears in conflict report (not auto-resolved)
    assert "session.md" not in result.output, (
        f"session.md should be auto-resolved. Output: {result.output}"
    )
    assert "conflict.py" in result.output


def test_parent_conflicts_all_auto_resolved_exits_0(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
) -> None:
    """When ALL parent_conflicts auto-resolve, proceed to Phase 4 (exit 0).

    Bug: parent_conflicts always exits 3, even when only session.md conflicts.
    Fix: when no conflicts remain after auto-resolution, fall through to Phase 4.
    """
    monkeypatch.chdir(repo_with_submodule)
    _commit_file(repo_with_submodule, "main.txt", "content\n", "Init")

    # Branch: only session.md changes (no hard conflicts)
    _run(repo_with_submodule, "checkout", "-b", "session-only-conflict")
    session_file = repo_with_submodule / "agents" / "session.md"
    session_file.write_text(
        "# Session: Branch\n\n## In-tree Tasks\n\n- [ ] **Branch task**\n"
    )
    _run(repo_with_submodule, "add", "agents/session.md")
    _run(repo_with_submodule, "commit", "-m", "Branch session only")

    # Main: different session.md changes only
    _run(repo_with_submodule, "checkout", "main")
    session_file.write_text(
        "# Session: Main\n\n## In-tree Tasks\n\n- [ ] **Main task**\n"
    )
    _run(repo_with_submodule, "add", "agents/session.md")
    _run(repo_with_submodule, "commit", "-m", "Main session only")

    subprocess.run(
        ["git", "merge", "--no-commit", "--no-ff", "session-only-conflict"],
        cwd=repo_with_submodule,
        capture_output=True,
        check=False,
    )
    assert _has_merge_head(), "MERGE_HEAD should exist"

    runner = CliRunner()
    result = runner.invoke(worktree, ["merge", "session-only-conflict"])

    # BUG: currently exits 3; fix: all auto-resolved → Phase 4 → exit 0
    assert result.exit_code == 0, (
        f"Expected exit 0 (all auto-resolved), got {result.exit_code}."
        f" Output: {result.output}"
    )


def test_precommit_stdout_forwarded(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Precommit failure output includes stdout (not only stderr).

    Bug: merge.py echoes precommit_result.stderr but drops .stdout.
    Fix: add click.echo(precommit_result.stdout) before the stderr echo.
    """
    monkeypatch.chdir(repo_with_submodule)
    _commit_file(repo_with_submodule, "main.txt", "content\n", "Init")
    _setup_diverged_branch(repo_with_submodule, "precommit-stdout-test")

    original_run = subprocess.run

    def mock_run(*args: object, **kwargs: object) -> object:
        cmd = args[0] if args else kwargs.get("args", [])
        if isinstance(cmd, list) and cmd[:2] == ["just", "precommit"]:
            r = Mock()
            r.returncode = 1
            r.stdout = "LINT: unused import in merge.py\n"
            r.stderr = "precommit failed\n"
            return r
        return original_run(*args, **kwargs)  # type: ignore[call-overload]

    monkeypatch.setattr(subprocess, "run", mock_run)

    runner = CliRunner()
    result = runner.invoke(worktree, ["merge", "precommit-stdout-test"])

    assert result.exit_code == 1
    # BUG: stdout from precommit is dropped — only stderr echoed
    assert "LINT: unused import" in result.output, (
        f"Expected precommit stdout in output. Output: {result.output}"
    )
    assert "precommit failed" in result.output
