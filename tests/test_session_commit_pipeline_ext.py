"""Tests for commit pipeline: submodule coordination and amend."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from claudeutils.session.commit import CommitInput
from claudeutils.session.commit_pipeline import commit_pipeline
from tests.pytest_helpers import init_repo_at as _init_repo


def _init_repo_with_submodule(tmp_path: Path) -> Path:
    """Set up parent repo with agent-core submodule."""
    sub_origin = tmp_path / "sub-origin"
    sub_origin.mkdir()
    subprocess.run(["git", "init"], cwd=sub_origin, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=sub_origin,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=sub_origin,
        check=True,
        capture_output=True,
    )
    (sub_origin / "init.md").write_text("init")
    subprocess.run(
        ["git", "add", "."],
        cwd=sub_origin,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=sub_origin,
        check=True,
        capture_output=True,
    )

    parent = tmp_path / "parent"
    parent.mkdir()
    _init_repo(parent)

    # Allow local file transport for submodule clone
    subprocess.run(
        [
            "git",
            "-c",
            "protocol.file.allow=always",
            "submodule",
            "add",
            str(sub_origin),
            "agent-core",
        ],
        cwd=parent,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "add submodule"],
        cwd=parent,
        check=True,
        capture_output=True,
    )
    # Configure submodule git identity
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=parent / "agent-core",
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=parent / "agent-core",
        check=True,
        capture_output=True,
    )
    return parent


# Cycle 6.2: submodule coordination (four-cell matrix)


def test_commit_with_submodule(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Submod files + submod message → both committed."""
    parent = _init_repo_with_submodule(tmp_path)
    monkeypatch.chdir(parent)

    (parent / "agent-core" / "new.md").write_text("new content")
    (parent / "src").mkdir(exist_ok=True)
    (parent / "src" / "main.py").write_text("code")

    ci = CommitInput(
        files=["agent-core/new.md", "src/main.py"],
        message="✨ Parent commit",
        submodules={"agent-core": "Add new.md to submodule"},
    )

    with patch(
        "claudeutils.session.commit_pipeline._run_precommit",
        return_value=(True, "All checks passed"),
    ):
        result = commit_pipeline(ci, cwd=parent)

    assert result.success is True
    assert "agent-core:" in result.output

    sub_log = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        cwd=parent / "agent-core",
        capture_output=True,
        text=True,
        check=False,
    )
    assert "Add new.md to submodule" in sub_log.stdout

    parent_log = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        cwd=parent,
        capture_output=True,
        text=True,
        check=False,
    )
    assert "Parent commit" in parent_log.stdout


def test_commit_submodule_no_message(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Submod files but no submod message → error."""
    parent = _init_repo_with_submodule(tmp_path)
    monkeypatch.chdir(parent)

    (parent / "agent-core" / "new.md").write_text("content")

    ci = CommitInput(
        files=["agent-core/new.md"],
        message="Commit without submodule msg",
        submodules={},
    )

    with patch(
        "claudeutils.session.commit_pipeline._run_precommit",
        return_value=(True, "ok"),
    ):
        result = commit_pipeline(ci, cwd=parent)

    assert result.success is False
    assert "**Error:**" in result.output


def test_commit_submodule_orphan_message(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No submod files but submod message → warning."""
    parent = _init_repo_with_submodule(tmp_path)
    monkeypatch.chdir(parent)

    (parent / "src").mkdir(exist_ok=True)
    (parent / "src" / "main.py").write_text("code")

    ci = CommitInput(
        files=["src/main.py"],
        message="Parent only",
        submodules={"agent-core": "Orphaned submodule message"},
    )

    with patch(
        "claudeutils.session.commit_pipeline._run_precommit",
        return_value=(True, "ok"),
    ):
        result = commit_pipeline(ci, cwd=parent)

    assert result.success is True
    assert "**Warning:**" in result.output
    assert (
        "Submodule message provided but no changes found for: agent-core. Ignored."
        in result.output
    )


def test_commit_no_submodule_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No submod files, no submod message → parent-only."""
    parent = _init_repo_with_submodule(tmp_path)
    monkeypatch.chdir(parent)

    (parent / "src").mkdir(exist_ok=True)
    (parent / "src" / "main.py").write_text("code")

    ci = CommitInput(
        files=["src/main.py"],
        message="Parent only",
        submodules={},
    )

    with patch(
        "claudeutils.session.commit_pipeline._run_precommit",
        return_value=(True, "ok"),
    ):
        result = commit_pipeline(ci, cwd=parent)

    assert result.success is True
    assert "**Warning:**" not in result.output


# Cycle 6.3: amend semantics


def test_commit_amend_parent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Amend replaces last parent commit."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)

    f = tmp_path / "src" / "foo.py"
    f.parent.mkdir(parents=True)
    f.write_text("original")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "original"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    f.write_text("amended")

    ci = CommitInput(
        files=["src/foo.py"],
        message="✨ Amended message",
        options={"amend"},
    )

    with patch(
        "claudeutils.session.commit_pipeline._run_precommit",
        return_value=(True, "ok"),
    ):
        result = commit_pipeline(ci, cwd=tmp_path)

    assert result.success is True

    log = subprocess.run(
        ["git", "log", "--oneline"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    commits = [ln for ln in log.stdout.strip().split("\n") if ln]
    assert len(commits) == 2
    assert "Amended message" in log.stdout
    assert "original" not in log.stdout


def test_commit_amend_submodule(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Amend with submodule: both amended, not new commits."""
    parent = _init_repo_with_submodule(tmp_path)
    monkeypatch.chdir(parent)

    (parent / "agent-core" / "feat.md").write_text("v1")
    subprocess.run(
        ["git", "add", "feat.md"],
        cwd=parent / "agent-core",
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "sub original"],
        cwd=parent / "agent-core",
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "add", "agent-core"],
        cwd=parent,
        check=True,
        capture_output=True,
    )
    (parent / "src").mkdir(exist_ok=True)
    (parent / "src" / "main.py").write_text("v1")
    subprocess.run(
        ["git", "add", "src/main.py"],
        cwd=parent,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "parent original"],
        cwd=parent,
        check=True,
        capture_output=True,
    )

    (parent / "agent-core" / "feat.md").write_text("v2")
    (parent / "src" / "main.py").write_text("v2")

    ci = CommitInput(
        files=["agent-core/feat.md", "src/main.py"],
        message="✨ Amended parent",
        options={"amend"},
        submodules={"agent-core": "Amended submodule"},
    )

    with patch(
        "claudeutils.session.commit_pipeline._run_precommit",
        return_value=(True, "ok"),
    ):
        result = commit_pipeline(ci, cwd=parent)

    assert result.success is True
    assert "agent-core:" in result.output

    # Submodule should have 2 commits: init and amended
    sub_log = subprocess.run(
        ["git", "log", "--oneline"],
        cwd=parent / "agent-core",
        capture_output=True,
        text=True,
        check=False,
    )
    sub_commits = [ln for ln in sub_log.stdout.strip().split("\n") if ln]
    assert len(sub_commits) == 2
    assert "Amended submodule" in sub_log.stdout
    assert "sub original" not in sub_log.stdout


def test_commit_amend_validation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Amend accepts HEAD files without working-tree changes."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)

    f = tmp_path / "tracked.py"
    f.write_text("content")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "add tracked"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    ci = CommitInput(
        files=["tracked.py"],
        message="✨ Amend HEAD-only file",
        options={"amend"},
    )

    with patch(
        "claudeutils.session.commit_pipeline._run_precommit",
        return_value=(True, "ok"),
    ):
        result = commit_pipeline(ci, cwd=tmp_path)

    assert result.success is True
    log = subprocess.run(
        ["git", "log", "--oneline"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert "Amend HEAD-only file" in log.stdout
    commits = [ln for ln in log.stdout.strip().split("\n") if ln]
    assert len(commits) == 2
