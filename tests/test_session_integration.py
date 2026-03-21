"""Cross-subcommand integration test (Phase 7)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.session.cli import handoff_cmd, status_cmd


def _init_repo(path: Path) -> None:
    """Initialize a git repo with session.md."""
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=path,
        check=True,
        capture_output=True,
    )

    session_dir = path / "agents"
    session_dir.mkdir()
    session_md = session_dir / "session.md"
    session_md.write_text(
        "# Session Handoff: 2026-03-21\n"
        "\n"
        "**Status:** Initial state\n"
        "\n"
        "## Completed This Session\n"
        "\n"
        "Nothing yet.\n"
        "\n"
        "## In-tree Tasks\n"
        "\n"
        "- [ ] **Build widget** — `/design plans/widget/brief.md`"
        " | sonnet\n"
    )

    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=path,
        check=True,
        capture_output=True,
    )


# Cycle 7.1: handoff then status round-trip


def test_handoff_then_status(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Handoff writes session.md, status reads it back."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)

    session_file = tmp_path / "agents" / "session.md"
    monkeypatch.setenv("CLAUDEUTILS_SESSION_FILE", str(session_file))

    # Handoff: update status and completed section
    handoff_stdin = (
        "**Status:** Phase 6 complete, commit pipeline delivered.\n"
        "\n"
        "## Completed This Session\n"
        "\n"
        "- Implemented commit pipeline with submodule coordination\n"
        "- Added amend semantics and validation levels\n"
        "\n"
        "## In-tree Tasks\n"
        "\n"
        "- [ ] **Build widget** — `/design plans/widget/brief.md`"
        " | sonnet\n"
    )

    runner = CliRunner()
    handoff_result = runner.invoke(handoff_cmd, input=handoff_stdin)
    assert handoff_result.exit_code == 0, f"handoff failed: {handoff_result.output}"

    # Status: read back the updated session.md
    status_result = runner.invoke(status_cmd)
    assert status_result.exit_code == 0, f"status failed: {status_result.output}"

    # Verify status reflects handoff updates
    output = status_result.output
    assert "Build widget" in output
