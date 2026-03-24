"""Tests for session commit parser and gates (Phase 5)."""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

import pytest

from claudeutils.session.commit import (
    CommitInputError,
    _split_sections,
    parse_commit_input,
)
from claudeutils.session.commit_gate import (
    CleanFileError,
    validate_files,
    vet_check,
)
from tests.pytest_helpers import init_repo_minimal

COMMIT_INPUT_FIXTURE = """\
## Files
- src/commit/cli.py
- src/commit/gate.py
- agent-core/fragments/vet-requirement.md

## Options
- no-vet
- amend

## Submodule agent-core
> 🤖 Update vet-requirement fragment
>
> - Add scripted gate classification reference

## Message
> ✨ Add commit CLI with scripted vet check
>
> - Structured markdown I/O
> - Submodule-aware commit pipeline
"""


# Cycle 5.1: parse commit markdown stdin


def test_parse_commit_input() -> None:
    """All sections of commit input parse correctly from shared fixture."""
    result = parse_commit_input(COMMIT_INPUT_FIXTURE)

    assert result.files == [
        "src/commit/cli.py",
        "src/commit/gate.py",
        "agent-core/fragments/vet-requirement.md",
    ]
    assert result.options == {"no-vet", "amend"}
    assert "agent-core" in result.submodules
    msg = result.submodules["agent-core"]
    assert msg.startswith("🤖 Update vet-requirement fragment")
    assert "- Add scripted gate classification reference" in msg
    assert result.message is not None
    assert result.message.startswith("✨ Add commit CLI")
    assert "- Structured markdown I/O" in result.message
    assert "- Submodule-aware commit pipeline" in result.message


def test_parse_commit_input_edge_cases() -> None:
    """Edge cases: missing sections, unknown options, no-edit rules."""
    # Missing ## Files → error
    with pytest.raises(CommitInputError, match="Files"):
        parse_commit_input("## Message\n> hello\n")

    # Missing ## Message without amend+no-edit → error
    with pytest.raises(CommitInputError, match="Message"):
        parse_commit_input("## Files\n- foo.py\n")

    # Unknown option → error
    with pytest.raises(CommitInputError, match="Unknown option"):
        parse_commit_input(
            "## Files\n- foo.py\n\n## Options\n- foobar\n\n## Message\n> msg\n"
        )

    # no-edit without amend → error
    with pytest.raises(CommitInputError, match="no-edit"):
        parse_commit_input(
            "## Files\n- foo.py\n\n## Options\n- no-edit\n\n## Message\n> msg\n"
        )

    # amend + no-edit without ## Message → valid
    result = parse_commit_input(
        "## Files\n- foo.py\n\n## Options\n- amend\n- no-edit\n"
    )
    assert result.message is None
    assert "amend" in result.options
    assert "no-edit" in result.options

    # no-edit with ## Message present → error (contradictory)
    with pytest.raises(CommitInputError, match="no-edit contradicts"):
        parse_commit_input(
            "## Files\n- f.py\n\n## Options\n- amend\n- no-edit\n\n## Message\n> msg\n"
        )


def test_parse_commit_empty_files_raises() -> None:
    """## Files section with no entries raises CommitInputError."""
    with pytest.raises(CommitInputError, match="empty"):
        parse_commit_input("## Files\n\n## Message\n> msg\n")


def test_parse_commit_no_options() -> None:
    """Input without ## Options produces empty set."""
    result = parse_commit_input("## Files\n- foo.py\n\n## Message\n> msg\n")
    assert result.options == set()


def test_parse_commit_multiple_submodules() -> None:
    """Multiple ## Submodule sections parsed independently."""
    text = """\
## Files
- foo.py

## Submodule agent-core
> Core update

## Submodule other-lib
> Lib update

## Message
> commit msg
"""
    result = parse_commit_input(text)
    assert len(result.submodules) == 2
    assert "agent-core" in result.submodules
    assert "other-lib" in result.submodules


def test_split_sections_in_message_preserves_headings() -> None:
    """## headings after ## Message stay in message body."""
    text = (
        "## Files\n"
        "- foo.py\n"
        "\n"
        "## Message\n"
        "> First line\n"
        ">\n"
        "## Not a section\n"
        "> More content\n"
    )
    sections = _split_sections(text)
    names = [name for name, _ in sections]
    assert names == ["Files", "Message"]
    # The "## Not a section" line must be in Message body
    msg_lines = sections[1][1]
    assert any("## Not a section" in line for line in msg_lines)


def test_parse_commit_blockquote_stripping() -> None:
    """Blockquote > prefix stripped from message and submodule lines."""
    text = """\
## Files
- foo.py

## Message
> First line
>
> - Detail line
> More text
"""
    result = parse_commit_input(text)
    assert result.message is not None
    # No leading "> " in message
    assert not any(line.startswith("> ") for line in result.message.split("\n"))
    assert "First line" in result.message
    assert "- Detail line" in result.message


# Cycle 5.2: validate_files — clean files check


def test_validate_files_dirty(tmp_path: Path) -> None:
    """All listed files appear in git status → passes."""
    init_repo_minimal(tmp_path)
    # Create and commit a file, then modify it
    f = tmp_path / "src" / "foo.py"
    f.parent.mkdir(parents=True)
    f.write_text("original")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    f.write_text("modified")

    # Should not raise
    validate_files(["src/foo.py"], cwd=tmp_path)


def test_validate_files_clean_error(tmp_path: Path) -> None:
    """Clean file raises CleanFileError with STOP directive."""
    init_repo_minimal(tmp_path)
    f = tmp_path / "clean.py"
    f.write_text("content")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    # File is committed, not modified — clean

    with pytest.raises(CleanFileError) as exc_info:
        validate_files(["clean.py"], cwd=tmp_path)

    err = exc_info.value
    assert "clean.py" in err.clean_files
    assert "STOP" in str(err)
    assert "no uncommitted changes" in str(err).lower()


def test_validate_files_amend(tmp_path: Path) -> None:
    """Amend mode accepts files in HEAD commit even if clean."""
    init_repo_minimal(tmp_path)
    f = tmp_path / "src" / "bar.py"
    f.parent.mkdir(parents=True)
    f.write_text("content")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    # File in HEAD commit, clean in working tree — amend allows it
    validate_files(["src/bar.py"], cwd=tmp_path, amend=True)

    # File not in HEAD and not dirty — amend still rejects
    (tmp_path / "other.py").write_text("x")
    subprocess.run(
        ["git", "add", "other.py"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "other"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    with pytest.raises(CleanFileError):
        validate_files(["src/bar.py"], cwd=tmp_path, amend=True)


# Cycle 5.3: scripted vet check


def test_vet_check_no_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """No [tool.claudeutils.commit] section → passes."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text("[tool.ruff]\n")

    result = vet_check(["src/foo.py"])
    assert result.passed is True


def test_vet_check_pass(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """File matches pattern with fresh report → passes."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        '[tool.claudeutils.commit]\nrequire-review = ["src/**/*.py"]\n'
    )
    src = tmp_path / "src" / "foo.py"
    src.parent.mkdir(parents=True)
    src.write_text("code")

    # Pin source mtime to 10s ago so report is reliably newer
    old_time = time.time() - 10
    os.utime(src, (old_time, old_time))

    report_dir = tmp_path / "plans" / "bar" / "reports"
    report_dir.mkdir(parents=True)
    report = report_dir / "vet-review.md"
    report.write_text("reviewed")

    result = vet_check(["src/foo.py"])
    assert result.passed is True


def test_vet_check_unreviewed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """File matches pattern with no report → unreviewed."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        '[tool.claudeutils.commit]\nrequire-review = ["src/**/*.py"]\n'
    )
    src = tmp_path / "src" / "foo.py"
    src.parent.mkdir(parents=True)
    src.write_text("code")
    # No plans/*/reports/ directories

    result = vet_check(["src/foo.py"])
    assert result.passed is False
    assert result.reason == "unreviewed"
    assert "src/foo.py" in result.unreviewed_files


def test_vet_check_stale(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Report older than source file → stale."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        '[tool.claudeutils.commit]\nrequire-review = ["src/**/*.py"]\n'
    )
    # Create report first (older mtime)
    report_dir = tmp_path / "plans" / "bar" / "reports"
    report_dir.mkdir(parents=True)
    report = report_dir / "vet-review.md"
    report.write_text("reviewed")

    # Set report mtime to 10 seconds ago
    old_time = time.time() - 10
    os.utime(report, (old_time, old_time))

    # Create source file (newer mtime)
    src = tmp_path / "src" / "foo.py"
    src.parent.mkdir(parents=True)
    src.write_text("new code")

    result = vet_check(["src/foo.py"])
    assert result.passed is False
    assert result.reason == "stale"
    assert result.stale_info is not None


def test_vet_check_stale_with_explicit_cwd(tmp_path: Path) -> None:
    """vet_check with explicit cwd detects stale without monkeypatch.chdir."""
    (tmp_path / "pyproject.toml").write_text(
        '[tool.claudeutils.commit]\nrequire-review = ["src/**/*.py"]\n'
    )

    report_dir = tmp_path / "plans" / "bar" / "reports"
    report_dir.mkdir(parents=True)
    report = report_dir / "vet-review.md"
    report.write_text("reviewed")

    # Pin report mtime to 10s ago so source is reliably newer
    old_time = time.time() - 10
    os.utime(report, (old_time, old_time))

    src = tmp_path / "src" / "foo.py"
    src.parent.mkdir(parents=True)
    src.write_text("new code")

    # Pass cwd explicitly — do NOT monkeypatch.chdir
    result = vet_check(["src/foo.py"], cwd=tmp_path)
    assert result.passed is False
    assert result.reason == "stale"
