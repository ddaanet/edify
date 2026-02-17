"""Tests for validate-runbook.py CLI scaffold."""

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "agent-core" / "bin" / "validate-runbook.py"


def test_scaffold_cli() -> None:
    """Script exposes four subcommands and exits 1 when invoked without one."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    for subcommand in ("model-tags", "lifecycle", "test-counts", "red-plausibility"):
        assert subcommand in result.stdout

    result_no_args = subprocess.run(
        [sys.executable, str(SCRIPT)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result_no_args.returncode == 1
